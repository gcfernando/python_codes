# Developed by Gehan Fernando
"""The `audio8d` command-line tool."""

import argparse
import dataclasses
import logging
import runpy
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

if __name__ == "__main__" and not __package__:
    # `python cli.py` without installing: __main__.py sets up the package and runs it
    runpy.run_path(str(Path(__file__).with_name("__main__.py")), run_name="__main__")

# pylint: disable=wrong-import-position
from . import __version__, display, hints
from .core.errors import Audio8DError
from .core.presets import PRESETS, RECOMMENDED_PRESET
from .core.settings import MP3_BITRATES, EffectConfig
from .core.types import AudioStreamInfo
from .ffmpeg import FFmpegToolchain, probe_audio
from .files import resolve_input
from .pipeline import LoudnessPlan, convert

# pylint: enable=wrong-import-position

LOG = logging.getLogger("audio8d")

# What `--loudness off` turns into, so it can switch off a preset's loudness target
LOUDNESS_OFF = "off"

_DEFAULTS = EffectConfig()
_BEST = PRESETS[RECOMMENDED_PRESET].config


def _columns(rows: Sequence[tuple[str, str]], width: int) -> str:
    """Line up commands and their explanations in two neat columns for --help."""
    return "\n".join(f"  {left:<{width}}{right}" for left, right in rows)


_QUICK_START = "\n".join(
    [
        "Turn any song into an 8D song that moves around your head (use headphones!).",
        "",
        "QUICK START - just copy one of these:",
        _columns(
            [
                (
                    f'audio8d "My Song.mp3" --preset {RECOMMENDED_PRESET}',
                    "best quality, same loudness as Spotify",
                ),
                (
                    'audio8d "My Song.mp3"',
                    'classic sound, new file: "My Song (8D).mp3"',
                ),
                ("audio8d", "step-by-step helper that asks you questions"),
                ("audio8d --list-presets", "show every ready-made style"),
            ],
            width=41,
        ),
        "",
        f"BEST VALUES (this is exactly what --preset {RECOMMENDED_PRESET} uses):",
        _columns(
            [
                (
                    f"--rotation-seconds {_BEST.rotation_seconds:g}",
                    f"--intensity {_BEST.intensity:.2f}",
                ),
                (
                    f"--ambience {_BEST.ambience:.2f}",
                    f"--limiter-ceiling {_BEST.limiter_ceiling:.2f}",
                ),
                (
                    f"--bitrate {_BEST.mp3_bitrate}",
                    f"--loudness {_BEST.loudness_target:g}",
                ),
            ],
            width=26,
        ),
    ]
)

_EXAMPLE_SONG = 'audio8d "My Song.mp3"'
_EXAMPLES = "\n".join(
    [
        "MORE EXAMPLES:",
        _columns(
            [
                (
                    f"{_EXAMPLE_SONG} --preset {RECOMMENDED_PRESET} --loudness -16",
                    "Apple Music loudness",
                ),
                (
                    f"{_EXAMPLE_SONG} --preset {RECOMMENDED_PRESET} --intensity 0.95",
                    "stronger movement",
                ),
                (
                    f'{_EXAMPLE_SONG} "C:\\Music\\8D\\My Song.mp3"',
                    "choose where to save it",
                ),
            ],
            width=58,
        ),
        "",
        "Developed by Gehan Fernando. Full guide: README.md",
    ]
)


def _loudness_value(text: str) -> float | str:
    """Accept a LUFS number like -14, or the word 'off'."""
    if text.strip().lower() in {"off", "none"}:
        return LOUDNESS_OFF
    try:
        return float(text)
    except ValueError:
        raise argparse.ArgumentTypeError("use a number like -14, or 'off'") from None


class _ListPresetsAction(argparse.Action):
    """Print the preset table and stop, the same way --help does."""

    def __init__(
        self, option_strings: Sequence[str], dest: str, **kwargs: object
    ) -> None:
        """Take no value, like --help, so `audio8d --list-presets` works on its own."""
        super().__init__(
            option_strings,
            dest,
            nargs=0,
            default=argparse.SUPPRESS,
            help=str(kwargs.get("help")),
        )

    def __call__(self, parser: argparse.ArgumentParser, *_: object) -> None:
        """Show the style table, then stop before argparse asks for a song."""
        display.show_presets(display.Painter(sys.stdout), __version__)
        parser.exit()


class _FriendlyParser(argparse.ArgumentParser):
    """An argument parser that explains typing mistakes in plain words."""

    def error(self, message: str) -> NoReturn:
        """Keep argparse's usual message, then add a plain fix and a working example."""
        painter = display.Painter(sys.stderr)
        self.print_usage(sys.stderr)
        painter.line(f"{self.prog}: error: {message}")
        display.show_fix(painter, hints.usage_fix_for(message))
        painter.line(
            "  "
            + painter.paint("Example:", "bold")
            + f' audio8d "My Song.mp3" --preset {RECOMMENDED_PRESET}'
        )
        self.exit(2)


def create_parser() -> argparse.ArgumentParser:
    """Build the argument parser; kept separate so tests can poke at it."""
    parser = _FriendlyParser(
        prog="audio8d",
        description=_QUICK_START,
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "input", type=Path, help="the song you want to change (mp3, flac, wav, ...)"
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="where to save the 8D song, ending in .mp3 (leave out: '<song> (8D).mp3')",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS),
        metavar="NAME",
        help=f"a ready-made style: {', '.join(PRESETS)}. BEST: {RECOMMENDED_PRESET}",
    )
    # Knobs default to None, so "not typed" differs from "typed the default value"
    parser.add_argument(
        "--rotation-seconds",
        type=float,
        metavar="2..100",
        help="how FAST it spins: seconds for one full circle "
        f"(normal {_DEFAULTS.rotation_seconds:g}, BEST {_BEST.rotation_seconds:g})",
    )
    parser.add_argument(
        "--intensity",
        type=float,
        metavar="0..1",
        help="how FAR it moves between your ears "
        f"(normal {_DEFAULTS.intensity}, BEST {_BEST.intensity})",
    )
    parser.add_argument(
        "--ambience",
        type=float,
        metavar="0..1",
        help="how much ROOM sound, 0 = none "
        f"(normal {_DEFAULTS.ambience:.2f}, BEST {_BEST.ambience})",
    )
    parser.add_argument(
        "--limiter-ceiling",
        type=float,
        metavar="0.0625..1",
        help="the loudest a peak may get, stops crackles "
        f"(normal {_DEFAULTS.limiter_ceiling}, BEST {_BEST.limiter_ceiling})",
    )
    parser.add_argument(
        "--quality",
        type=int,
        choices=range(10),
        metavar="0..9",
        help="MP3 quality, 0 = best, 9 = smallest "
        f"(normal {_DEFAULTS.mp3_quality}, BEST {_BEST.mp3_quality})",
    )
    parser.add_argument(
        "--bitrate",
        type=int,
        choices=MP3_BITRATES,
        metavar="KBPS",
        help="constant MP3 bitrate, 320 = the most MP3 allows; replaces --quality "
        f"(normal off, BEST {_BEST.mp3_bitrate})",
    )
    parser.add_argument(
        "--loudness",
        type=_loudness_value,
        metavar="LUFS",
        help="final loudness: -14 = Spotify/YouTube, -16 = Apple Music, or off "
        f"(normal off, BEST {_BEST.loudness_target:g})",
    )
    parser.add_argument(
        "--exact-loudness",
        action="store_const",
        const=True,
        help="always hit the --loudness target exactly, even if the loudest peaks "
        "must be shaved a little (normal off)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="allow replacing a file that already has the output name",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="show extra technical details, useful when something goes wrong",
    )
    parser.add_argument(
        "--list-presets",
        action=_ListPresetsAction,
        help="show every ready-made style with its exact values, then stop",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"audio8d {__version__} - developed by Gehan Fernando",
        help="show the version number and who made it",
    )

    return parser


def resolve_config(args: argparse.Namespace) -> EffectConfig:
    """Start from the chosen preset (or the defaults), then apply any typed knobs."""
    base = PRESETS[args.preset].config if args.preset else EffectConfig()

    typed = {
        "rotation_seconds": args.rotation_seconds,
        "intensity": args.intensity,
        "ambience": args.ambience,
        "limiter_ceiling": args.limiter_ceiling,
        "mp3_quality": args.quality,
        "mp3_bitrate": args.bitrate,
        "exact_loudness": args.exact_loudness,
    }
    overrides: dict[str, object] = {
        key: value for key, value in typed.items() if value is not None
    }
    if args.loudness is not None:
        overrides["loudness_target"] = (
            None if args.loudness == LOUDNESS_OFF else args.loudness
        )

    return dataclasses.replace(base, **overrides)


def _used_only_defaults(args: argparse.Namespace) -> bool:
    """True when the user typed no preset and no knobs at all."""
    knobs = (
        args.preset,
        args.rotation_seconds,
        args.intensity,
        args.ambience,
        args.limiter_ceiling,
        args.quality,
        args.loudness,
        args.bitrate,
        args.exact_loudness,
    )
    return all(value is None for value in knobs)


def configure_logging(verbose: bool) -> None:
    """Short messages normally; timestamps and pipeline details with --verbose."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
        if verbose
        else "%(levelname)s %(name)s: %(message)s",
    )
    # The settings panel already says what is happening, so hide duplicate INFO lines
    logging.getLogger(convert.__module__).setLevel(
        logging.NOTSET if verbose else logging.WARNING
    )


def default_output_for(input_path: Path) -> Path:
    """Place the 8D copy beside the original, e.g. `song.flac` -> `song (8D).mp3`."""
    return input_path.with_name(f"{input_path.stem} (8D).mp3")


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


def _run_conversion(
    input_path: Path,
    output_path: Path,
    config: EffectConfig,
    overwrite: bool,
    *,
    preset: str | None = None,
    show_tip: bool = False,
    banner: bool = True,
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
        preset=preset,
        config=config,
        banner=banner,
        source=_peek_source(input_path),
    )

    plans: list[LoudnessPlan] = []
    started = time.perf_counter()
    try:
        convert(
            input_path=input_path,
            output_path=output_path,
            config=config,
            overwrite=overwrite,
            on_loudness=plans.append,
        )
    except Audio8DError as exc:
        _explain(painter, exc)
        return 1

    display.show_done(painter, output_path, time.perf_counter() - started)
    for plan in plans:
        display.show_loudness(painter, plan)
    if show_tip:
        display.show_tip(painter)
    return 0


def _clean_typed_path(answer: str) -> str:
    """Strip the quotes, spaces and '& ' that drag-and-drop or 'Copy as path' add."""
    cleaned = answer.strip()
    if cleaned.startswith("& "):
        cleaned = cleaned[2:]
    return cleaned.strip().strip("\"'").strip()


def _ask_for_song(painter: display.Painter) -> Path | None:
    """Keep asking until we get a real file, or the user presses Enter to stop."""
    display.show_step(
        painter, 1, "Which song?", "Drag your song into this window, then press Enter."
    )
    while True:
        answer = _clean_typed_path(input("  Song: "))
        if not answer:
            return None
        song = Path(answer).expanduser()
        if song.is_file():
            return song
        if song.is_dir():
            display.show_problem(
                painter, "That is a folder. Please drag in one song file."
            )
        else:
            display.show_problem(
                painter,
                "I can't find that file. Try dragging it in (or press Enter to stop).",
            )


def _ask_for_style(painter: display.Painter) -> str:
    """Numbered style menu; pressing Enter picks the best one."""
    painter.line()
    display.show_step(
        painter,
        2,
        "Which style?",
        f"Just press Enter for the BEST one ({RECOMMENDED_PRESET}).",
    )
    names = display.show_style_menu(painter)
    while True:
        answer = input("  Style [1]: ").strip().lower()
        if not answer:
            return names[0]
        if answer.isdigit() and 1 <= int(answer) <= len(names):
            return names[int(answer) - 1]
        if answer in names:
            return answer
        display.show_problem(
            painter, f"Please type a number from 1 to {len(names)}, or press Enter."
        )


def _run_interactive() -> int:
    """Walk a first-time user through two questions, e.g. after double-clicking."""
    configure_logging(verbose=False)
    painter = display.Painter(sys.stdout)
    display.show_welcome(painter, __version__)

    try:
        song = _ask_for_song(painter)
        if song is None:
            painter.line("  No song given, nothing to do.")
            code = 2
        else:
            style = _ask_for_style(painter)
            painter.line()
            code = _run_conversion(
                song,
                default_output_for(song),
                PRESETS[style].config,
                overwrite=False,
                preset=style,
                banner=False,
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


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run one conversion, and return the process exit code."""
    if _should_ask_interactively(argv):
        return _run_interactive()

    args = create_parser().parse_args(argv)
    configure_logging(args.verbose)

    output = args.output if args.output is not None else default_output_for(args.input)
    only_defaults = _used_only_defaults(args)

    return _run_conversion(
        args.input,
        output,
        resolve_config(args),
        args.overwrite,
        # Typing nothing is the same as choosing the classic style, so say so
        preset="classic" if only_defaults else args.preset,
        show_tip=only_defaults,
    )
