# Developed by Gehan Fernando
"""The `audio8d` command-line tool."""

import argparse
import dataclasses
import logging
import runpy
import sys
import threading
import time
from collections.abc import Callable, Sequence
from pathlib import Path

if __name__ == "__main__" and not __package__:
    # `python cli.py` without installing: __main__.py sets up the package and runs it
    runpy.run_path(str(Path(__file__).with_name("__main__.py")), run_name="__main__")

# pylint: disable=wrong-import-position
from . import __version__, display, guided, hints, launcher
from .batch import BatchItem, default_jobs, progress_tracker, run_batch
from .core.errors import Audio8DError, InputValidationError
from .core.presets import Preset
from .core.settings import (
    EffectConfig,
)
from .core.types import AudioStreamInfo, Trim
from .core.user_presets import save_user_preset
from .ffmpeg import FFmpegToolchain, probe_audio
from .files import (
    default_output_for,
    find_songs,
    resolve_input,
)
from .logs import start_log_file
from .opener import open_path as open_in_player
from .options import (
    create_parser,
    known_presets,
    resolve_config,
    used_only_defaults,
)
from .pipeline import (
    ConvertOptions,
    compare,
    compare_output_for,
    convert,
    preview,
    preview_output_for,
    stages_for,
)

# pylint: enable=wrong-import-position

LOG = logging.getLogger("audio8d")

# The helper's path cleaner, kept under its old name for existing callers
_clean_typed_path = guided.clean_typed_path


def configure_logging(verbose: bool) -> None:
    """Short messages normally; timestamps and pipeline details with --verbose."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
        if verbose
        else "%(levelname)s %(name)s: %(message)s",
        # The windowed exe has no console to print to
        handlers=None if sys.stderr is not None else [logging.NullHandler()],
    )
    if not verbose:
        # The panel already says what the pipeline is doing; the log file still gets it
        quiet = convert.__module__
        for handler in logging.getLogger().handlers:
            if not getattr(handler, "audio8d_quiet", False) and not getattr(
                handler, "audio8d_file", False
            ):
                handler.addFilter(
                    lambda record: (
                        record.levelno >= logging.WARNING or record.name != quiet
                    )
                )
                handler.audio8d_quiet = True  # type: ignore[attr-defined]
    start_log_file()


def _explain(painter: display.Painter, error: Audio8DError) -> None:
    """Known problems get a one-line message and a plain fix, never a traceback."""
    LOG.error("%s", error)
    fix = hints.fix_for(error)
    if fix:
        display.show_fix(painter, fix)


def _peek_source(input_path: Path) -> AudioStreamInfo | None:
    """Read the song's details for the panel; convert() reports any problem later."""
    try:
        return probe_audio(FFmpegToolchain.discover(), resolve_input(input_path))
    except Audio8DError:
        return None


@dataclasses.dataclass(frozen=True, slots=True)
class Plan:  # pylint: disable=too-many-instance-attributes
    """Everything decided before any work starts, shared by all the run modes."""

    config: EffectConfig
    preset: str | None
    options: ConvertOptions
    overwrite: bool = False
    output_dir: Path | None = None
    name_style: str = "8d"
    jobs: int = 1
    recursive: bool = False
    play: bool = False
    show_tip: bool = False
    presets: dict[str, Preset] = dataclasses.field(default_factory=dict)


def _output_for(song: Path, plan: Plan, relative_to: Path | None = None) -> Path:
    """Where one song's 8D copy is saved."""
    return default_output_for(
        song,
        plan.config.extension,
        output_dir=plan.output_dir,
        name_style=plan.name_style,
        relative_to=relative_to,
    )


def run_single(
    input_path: Path, output_path: Path, plan: Plan, *, banner: bool = True
) -> int:
    """Show the settings, convert one file, and turn known problems into exit code 1."""
    painter = display.Painter(sys.stderr)

    # A missing or empty song is the most common slip, so say so before the whole panel
    try:
        resolve_input(input_path)
    except Audio8DError as exc:
        _explain(painter, exc)
        return 1

    display.show_settings(
        painter,
        version=__version__,
        song_in=input_path,
        song_out=output_path,
        preset=plan.preset,
        config=plan.config,
        banner=banner,
        source=_peek_source(input_path),
        trim=plan.options.trim,
        presets=plan.presets or None,
    )

    progress_bar = display.ProgressBar(painter)
    started = time.perf_counter()
    try:
        result = convert(
            input_path=input_path,
            output_path=output_path,
            config=plan.config,
            overwrite=plan.overwrite,
            options=plan.options,
            on_progress=progress_bar.update,
        )
    except Audio8DError as exc:
        progress_bar.finish()
        _explain(painter, exc)
        return 1
    progress_bar.finish()

    display.show_result(painter, result, time.perf_counter() - started)
    if result.original_removed_to:
        display.show_removed(painter, input_path, result.original_removed_to)
    display.show_listen(painter)
    if plan.show_tip:
        display.show_tip(painter)
    if plan.play:
        open_in_player(result.output)
    return 0


def _split_existing(
    found: list[Path], plan: Plan, folder: Path
) -> tuple[list[BatchItem], list[Path]]:
    """Songs still to make, and 8D copies that already exist (skipped)."""
    items: list[BatchItem] = []
    skipped: list[Path] = []
    for song in found:
        output = _output_for(song, plan, relative_to=folder)
        replacing_itself = plan.options.replace_original and output == song
        if output.exists() and not plan.overwrite and not replacing_itself:
            skipped.append(output)
        else:
            items.append(BatchItem(song, output))
    return items, skipped


def _batch_display(
    painter: display.Painter, plan: Plan, count: int
) -> tuple[
    display.BatchBar,
    Callable[[int, str, float], None],
    Callable[[int, object], None],
]:
    """The overall bar plus the two callbacks that keep it up to date."""
    stages = stages_for(plan.options)
    update, overall = progress_tracker(count, stages)
    progress_bar = display.BatchBar(painter, count)
    progress_bar.draw(0.0)

    def on_progress(index: int, stage: str, share: float) -> None:
        """Fold one song's progress into the overall bar."""
        update(index, stage, share)
        progress_bar.draw(overall())

    def on_done(_index: int, outcome: object) -> None:
        """Print the finished song's line above the bar."""
        number = progress_bar.finished + 1
        progress_bar.song_line(display.batch_line(painter, number, count, outcome))

    return progress_bar, on_progress, on_done


def run_folder(  # pylint: disable=too-many-locals
    folder: Path, plan: Plan, *, banner: bool = True, songs: list[Path] | None = None
) -> int:
    """Convert every song in a folder, several at once, then show the totals."""
    painter = display.Painter(sys.stderr)
    try:
        found = (
            songs if songs is not None else find_songs(folder, recursive=plan.recursive)
        )
        if not found:
            raise InputValidationError(f"No songs found in {folder}")
    except Audio8DError as exc:
        _explain(painter, exc)
        return 1

    items, skipped = _split_existing(found, plan, folder)

    display.show_settings(
        painter,
        version=__version__,
        song_in=folder,
        song_out=plan.output_dir or Path("next to each original"),
        preset=plan.preset,
        config=plan.config,
        banner=banner,
        trim=plan.options.trim,
        presets=plan.presets or None,
    )
    for path in skipped:
        painter.line(painter.paint(f"  Skipped (already made): {path.name}", "dim"))
    if not items:
        painter.line(
            painter.paint(
                "  Nothing new to convert. Add --overwrite to redo them.", "yellow"
            )
        )
        return 0
    display.show_batch_plan(
        painter, len(items), plan.jobs, plan.output_dir, plan.options.replace_original
    )

    progress_bar, on_progress, on_done = _batch_display(painter, plan, len(items))
    cancel = threading.Event()
    try:
        report = run_batch(
            items,
            plan.config,
            options=plan.options,
            overwrite=plan.overwrite,
            jobs=plan.jobs,
            on_progress=on_progress,
            on_done=on_done,
            cancel=cancel,
        )
    except KeyboardInterrupt:
        cancel.set()
        progress_bar.close()
        painter.line(
            painter.paint("  Stopped. Songs already finished are kept.", "yellow")
        )
        return 1
    progress_bar.close()
    display.show_batch_summary(painter, report)
    for outcome in report.failed:
        assert outcome.error is not None
        fix = hints.fix_for(outcome.error)
        if fix:
            painter.line(painter.paint(f"  {outcome.item.source.name}: ", "dim") + fix)
    if report.converted:
        display.show_listen(painter)
    if plan.play and report.converted:
        open_in_player(report.converted[0].result.output)  # type: ignore[union-attr]
    return 1 if report.failed else 0


def run_preview(
    input_path: Path, plan: Plan, seconds: float, output: Path | None
) -> int:
    """Make a short sample from the loudest part, so you can try a style quickly."""
    painter = display.Painter(sys.stderr)
    target = output or preview_output_for(input_path, plan.config.extension)
    progress_bar = display.ProgressBar(painter)
    try:
        resolve_input(input_path)
        display.show_settings(
            painter,
            version=__version__,
            song_in=input_path,
            song_out=target,
            preset=plan.preset,
            config=plan.config,
            source=_peek_source(input_path),
            presets=plan.presets or None,
        )
        painter.line(
            painter.paint(f"  Preview: {seconds:g} s from the loudest part.", "cyan")
        )
        started = time.perf_counter()
        result = preview(
            input_path,
            target,
            plan.config,
            seconds=seconds,
            on_progress=progress_bar.update,
        )
    except Audio8DError as exc:
        progress_bar.finish()
        _explain(painter, exc)
        return 1
    progress_bar.finish()
    display.show_result(painter, result, time.perf_counter() - started)
    display.show_listen(painter)
    if plan.play:
        open_in_player(result.output)
    return 0


def run_compare(input_path: Path, plan: Plan, output: Path | None) -> int:
    """Make the A/B file: the original, a short pause, then the 8D version."""
    painter = display.Painter(sys.stderr)
    target = output or compare_output_for(input_path)
    progress_bar = display.ProgressBar(painter)
    try:
        resolve_input(input_path)
        display.show_settings(
            painter,
            version=__version__,
            song_in=input_path,
            song_out=target,
            preset=plan.preset,
            config=plan.config,
            source=_peek_source(input_path),
            presets=plan.presets or None,
        )
        started = time.perf_counter()
        made = compare(input_path, target, plan.config, on_progress=progress_bar.update)
    except Audio8DError as exc:
        progress_bar.finish()
        _explain(painter, exc)
        return 1
    progress_bar.finish()
    display.show_done(painter, made, time.perf_counter() - started)
    painter.line(
        painter.paint(
            "  First 15 s: the ORIGINAL (A). A short pause. Then the 8D version (B).",
            "green",
        )
    )
    painter.line(
        painter.paint(
            "  Both are the same loudness, so only the 8D effect differs.", "dim"
        )
    )
    if plan.play:
        open_in_player(made)
    return 0


def _save_preset(args: argparse.Namespace, config: EffectConfig) -> int:
    """Save the typed settings as a named style and say where."""
    painter = display.Painter(sys.stderr)
    try:
        where = save_user_preset(
            args.save_preset,
            config,
            based_on=args.preset or "classic",
            summary=f"your style, based on {args.preset or 'classic'}",
        )
    except Audio8DError as exc:
        _explain(painter, exc)
        return 1
    painter.line(
        "  "
        + painter.paint(f"Saved your style '{args.save_preset}'", "bold", "green")
        + painter.paint(f" in {where}", "green")
    )
    painter.line(f'  Use it with: audio8d "My Song.mp3" --preset {args.save_preset}')
    return 0


def plan_from_args(args: argparse.Namespace) -> Plan:
    """Turn the parsed command line into a Plan (may raise InputValidationError)."""
    presets = known_presets()
    config = resolve_config(args, presets)
    config.validate()
    only_defaults = used_only_defaults(args)
    replace = bool(args.replace)
    # Replacing usually means "put the 8D song where the old one was"
    name_style = args.name or ("original" if replace else "8d")
    trim = (
        Trim(args.start, args.end)
        if args.start is not None or args.end is not None
        else None
    )
    if (
        trim
        and trim.start is not None
        and trim.end is not None
        and trim.end <= trim.start
    ):
        raise InputValidationError("The chosen start and end leave no sound to convert")
    return Plan(
        config=config,
        # Typing nothing is the same as choosing the classic style, so say so
        preset="classic" if only_defaults else args.preset,
        options=ConvertOptions(
            trim=trim,
            keep_cover=not args.no_cover,
            tag_title=not args.keep_title,
            check=not args.no_check,
            replace_original=replace,
        ),
        overwrite=args.overwrite,
        output_dir=args.output_dir,
        name_style=name_style,
        jobs=args.jobs or default_jobs(),
        recursive=args.recursive,
        play=args.play,
        show_tip=only_defaults,
        presets=presets,
    )


def _run_interactive() -> int:
    """Walk a first-time user through four questions, e.g. after double-clicking."""
    configure_logging(verbose=False)
    painter = display.Painter(sys.stdout)
    display.show_welcome(painter, __version__)
    presets = known_presets()

    try:
        chosen = guided.ask_for_music(painter)
        if chosen is None:
            painter.line("  Nothing given, nothing to do.")
            code = 2
        else:
            songs = (
                guided.ask_which_songs(painter, chosen) if chosen.is_dir() else [chosen]
            )
            if not songs:
                code = 2
            else:
                style = guided.ask_for_style(painter, presets)
                destination = guided.ask_for_destination(painter)
                replace, name_style = guided.ask_about_originals(painter)
                painter.line()
                plan = Plan(
                    config=presets[style].config,
                    preset=style,
                    options=ConvertOptions(replace_original=replace),
                    output_dir=destination,
                    name_style=name_style,
                    jobs=default_jobs(),
                    presets=presets,
                )
                if chosen.is_dir():
                    code = run_folder(chosen, plan, banner=False, songs=songs)
                else:
                    code = run_single(
                        chosen, _output_for(chosen, plan), plan, banner=False
                    )
        # Keep a double-clicked window open long enough to read the result
        input("\nPress Enter to close...")
    except (EOFError, KeyboardInterrupt):
        print()
        return 1

    return code


def _should_ask_interactively(argv: Sequence[str] | None) -> bool:
    """True only for a real person with no arguments, never for scripts or pipes."""
    return (
        argv is None
        and len(sys.argv) <= 1
        and sys.stdin.isatty()
        and sys.stdout.isatty()
    )


def _parse(
    parser: argparse.ArgumentParser, argv: Sequence[str] | None
) -> tuple[argparse.Namespace, list[Path]]:
    """The typed options, plus every song given when opening the window."""
    # The window takes any number of songs (e.g. several dropped on Audio8D.pyw)
    args, extra = parser.parse_known_args(argv)
    if not args.gui or any(word.startswith("-") for word in extra):
        return parser.parse_args(argv), []
    given = [args.input, args.output, *map(Path, extra)]
    return args, [song for song in given if song is not None]


def main(argv: Sequence[str] | None = None) -> int:  # pylint: disable=too-many-return-statements
    """Parse arguments, run the chosen mode, and return the process exit code."""
    # A double-clicked window opens in the old console; move to Windows Terminal
    if argv is None and launcher.relaunch_in_windows_terminal(sys.argv[1:]):
        return 0
    if _should_ask_interactively(argv):
        return _run_interactive()

    parser = create_parser()
    args, songs = _parse(parser, argv)
    configure_logging(args.verbose)

    if args.gui:
        from .gui import run_gui  # pylint: disable=import-outside-toplevel

        return run_gui(songs)

    painter = display.Painter(sys.stderr)
    try:
        plan = plan_from_args(args)
    except Audio8DError as exc:
        _explain(painter, exc)
        return 1

    if args.save_preset:
        code = _save_preset(args, plan.config)
        if code or args.input is None:
            return code
    if args.input is None:
        parser.error("the following arguments are required: input")

    if args.input.is_dir():
        if args.output is not None:
            parser.error("with a folder, choose where to save with --output-dir")
        if args.preview is not None or args.compare:
            parser.error("--preview and --compare work on one song, not a folder")
        return run_folder(args.input, plan)
    if args.compare:
        return run_compare(args.input, plan, args.output)
    if args.preview is not None:
        return run_preview(args.input, plan, args.preview, args.output)
    output = args.output if args.output is not None else _output_for(args.input, plan)
    return run_single(args.input, output, plan)


__all__ = ["create_parser", "default_output_for", "main", "resolve_config"]
