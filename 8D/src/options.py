# Developed by Gehan Fernando
"""Every option the `audio8d` command understands, and how they become settings."""

import argparse
import dataclasses
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NoReturn

from . import __version__, display, hints
from .batch import MAX_JOBS, default_jobs
from .core.errors import Audio8DError, InputValidationError
from .core.locations import GUIDE_URL
from .core.parsing import parse_keyframes, parse_time
from .core.presets import PRESETS, RECOMMENDED_PRESET, Preset
from .core.settings import (
    BITRATES,
    DIRECTIONS,
    ENGINES,
    FORMAT_EXTENSIONS,
    PATHS,
    VOCAL_MODES,
    EffectConfig,
    speaker_safe,
)
from .core.user_presets import all_presets
from .files import NAME_STYLES, format_for_extension

LOG = logging.getLogger("audio8d")

# What `--loudness off` turns into, so it can switch off a preset's loudness target
LOUDNESS_OFF = "off"
# What `--loudness match` turns into: the same loudness as the original
LOUDNESS_MATCH = "match"
# --bitrate auto: no constant bitrate, so MP3 uses its variable --quality
BITRATE_AUTO = "auto"

_DEFAULTS = EffectConfig()
_BEST = PRESETS[RECOMMENDED_PRESET].config


def _columns(rows: Sequence[tuple[str, str]], width: int) -> str:
    """Line up commands and their explanations in two neat columns for --help."""
    return "\n".join(f"  {left:<{width}}{right}" for left, right in rows)


_QUICK_START = "\n".join(
    [
        "Turn any song (or a whole folder) into 3D / 8D music that moves around "
        "your head.",
        "Use headphones!",
        "",
        "QUICK START - just copy one of these:",
        _columns(
            [
                (
                    f'audio8d "My Song.mp3" --preset {RECOMMENDED_PRESET}',
                    "best quality, same loudness as Spotify",
                ),
                ('audio8d "My Song.mp3"', 'new file: "My Song (8D).mp3"'),
                (r'audio8d "C:\Music"', "every song in the folder"),
                ('audio8d "My Song.mp3" --preview', "hear a 30 s sample first"),
                ("audio8d", "step-by-step helper that asks you questions"),
                ("audio8d --gui", "a window with buttons instead of typing"),
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
                (f"--bitrate {_BEST.bitrate}", f"--loudness {_BEST.loudness_target:g}"),
                (
                    f"--quality {_BEST.quality}",
                    f"--bass {_BEST.bass_hz:g}  --engine 3d",
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
                (f"{_EXAMPLE_SONG} --preset lossless", "FLAC, nothing lost"),
                (f"{_EXAMPLE_SONG} --preset groove", "moves in time with the beat"),
                (f"{_EXAMPLE_SONG} --path figure8 --elevation 0.5", "loops and rises"),
                (f"{_EXAMPLE_SONG} --compare --play", "hear original, then 8D"),
                (
                    r'audio8d "C:\Music" --output-dir "D:\8D" --jobs 4',
                    "a folder, 4 at a time",
                ),
                (
                    r'audio8d "C:\Music" --replace',
                    "replace each song (old one to Recycle Bin)",
                ),
                (
                    f'{_EXAMPLE_SONG} --speed-curve "0=10, 1:00=6, 2:30=10"',
                    "faster in the chorus",
                ),
            ],
            width=52,
        ),
        "",
        "Developed by Gehan Fernando. Full guide: README.md, or " + GUIDE_URL,
    ]
)


def _bitrate_value(text: str) -> int | str:
    """Accept one of the constant bitrates, or 'auto' to use the MP3 quality."""
    word = text.strip().lower()
    if word == BITRATE_AUTO:
        return BITRATE_AUTO
    if word.isdigit() and int(word) in BITRATES:
        return int(word)
    raise argparse.ArgumentTypeError(f"use {', '.join(map(str, BITRATES))} or 'auto'")


def _jobs_value(text: str) -> int:
    """How many songs at once: a whole number from 1 to MAX_JOBS."""
    if text.strip().isdigit() and 1 <= int(text) <= MAX_JOBS:
        return int(text)
    raise argparse.ArgumentTypeError(f"use a whole number from 1 to {MAX_JOBS}")


def _loudness_value(text: str) -> float | str:
    """Accept a LUFS number like -14, or the words 'off' or 'match'."""
    word = text.strip().lower()
    if word in {"off", "none"}:
        return LOUDNESS_OFF
    if word in {"match", "original", "same"}:
        return LOUDNESS_MATCH
    try:
        return float(text)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "use a number like -14, 'match' or 'off'"
        ) from None


def _bass_value(text: str) -> float:
    """A split frequency in Hz, or 'off' (0) to let the bass move too."""
    if text.strip().lower() in {"off", "none", "0"}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        raise argparse.ArgumentTypeError("use a number like 120, or 'off'") from None


def _time_value(text: str) -> float:
    """A time like 90 or 1:30."""
    try:
        return parse_time(text)
    except InputValidationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def _curve_value(text: str) -> tuple[tuple[float, float], ...]:
    """TIME=VALUE pairs, e.g. '0=10, 1:00=6'."""
    try:
        return parse_keyframes(text)
    except InputValidationError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def _preset_name(text: str) -> str:
    """A style that exists: built-in, or saved with --save-preset."""
    name = text.strip().lower()
    known = known_presets()
    if name not in known:
        raise argparse.ArgumentTypeError(
            f"invalid choice: '{text}' (choose from {', '.join(known)})"
        )
    return name


def known_presets() -> dict[str, Preset]:
    """Built-in styles plus your own; a broken styles file only loses your own."""
    try:
        return all_presets()
    except Audio8DError as exc:
        LOG.warning(
            "Your styles file has a problem, so only built-in styles work: %s", exc
        )
        return dict(PRESETS)


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
        display.show_presets(display.Painter(sys.stdout), __version__, known_presets())
        parser.exit()


class _FriendlyParser(argparse.ArgumentParser):
    """An argument parser that explains typing mistakes in plain words."""

    def error(self, message: str) -> NoReturn:
        """Keep argparse's usual message, then add a plain fix and a working example."""
        painter = display.Painter(sys.stderr)
        # The full usage lists every option; one short line keeps the fix visible
        painter.line(
            f"usage: {self.prog} [options] SONG_OR_FOLDER [OUTPUT]"
            "   (all options: audio8d --help)"
        )
        painter.line(f"{self.prog}: error: {message}")
        display.show_fix(painter, hints.usage_fix_for(message))
        painter.line(
            "  "
            + painter.paint("Example:", "bold")
            + f' audio8d "My Song.mp3" --preset {RECOMMENDED_PRESET}'
        )
        self.exit(2)


def _add_sound_options(parser: argparse.ArgumentParser) -> None:
    """--preset and every knob that changes how the song sounds."""
    group = parser.add_argument_group("how it sounds")
    group.add_argument(
        "--preset",
        type=_preset_name,
        metavar="NAME",
        help="a ready-made style (see --list-presets), or one you saved. "
        f"BEST: {RECOMMENDED_PRESET}",
    )
    # Knobs default to None, so "not typed" differs from "typed the default value"
    group.add_argument(
        "--rotation-seconds",
        type=float,
        metavar="2..100",
        help="how FAST it spins: seconds for one full circle "
        f"(normal {_DEFAULTS.rotation_seconds:g}, BEST {_BEST.rotation_seconds:g})",
    )
    group.add_argument(
        "--intensity",
        type=float,
        metavar="0..1",
        help="how FAR it moves around your head "
        f"(normal {_DEFAULTS.intensity}, BEST {_BEST.intensity})",
    )
    group.add_argument(
        "--ambience",
        type=float,
        metavar="0..1",
        help="how much ROOM sound (reverb), 0 = none "
        f"(normal {_DEFAULTS.ambience:.2f}, BEST {_BEST.ambience})",
    )
    group.add_argument(
        "--engine",
        choices=ENGINES,
        help="3d = real 3D around your head (BEST); pan = simple left-right",
    )
    group.add_argument(
        "--path",
        choices=PATHS,
        help="the route it takes: circle (normal), arc (front only), "
        "figure8 (round each ear), wander",
    )
    group.add_argument("--direction", choices=DIRECTIONS, help="which way it turns")
    group.add_argument(
        "--bass",
        type=_bass_value,
        metavar="HZ",
        help="keep everything below this in the MIDDLE; off lets the bass move "
        f"(BEST {_BEST.bass_hz:g})",
    )
    group.add_argument(
        "--elevation",
        type=float,
        metavar="0..1",
        help="let the sound drift UP over your head (normal 0)",
    )
    group.add_argument(
        "--fade",
        type=float,
        metavar="SECONDS",
        help="ease the movement in at the start and out at the end "
        f"(normal {_DEFAULTS.fade_seconds:g})",
    )
    group.add_argument(
        "--speed-curve",
        type=_curve_value,
        metavar='"T=S,..."',
        help='change the spin over time, e.g. "0=10, 1:00=6, 2:30=10"',
    )
    group.add_argument(
        "--intensity-curve",
        type=_curve_value,
        metavar='"T=A,..."',
        help='change the movement over time, e.g. "0=0.6, 1:00=0.95"',
    )
    group.add_argument(
        "--beat-sync",
        action="store_const",
        const=True,
        help="find the song's tempo and make one circle last whole bars",
    )
    group.add_argument(
        "--bpm",
        type=float,
        metavar="TEMPO",
        help="the song's tempo if you know it (switches beat sync on)",
    )
    group.add_argument(
        "--vocals",
        choices=VOCAL_MODES,
        help="center keeps the SINGER in the middle (needs: pip install demucs)",
    )
    group.add_argument(
        "--speakers",
        action="store_true",
        help="make it sound right on speakers and car stereos too",
    )


def _add_output_options(parser: argparse.ArgumentParser) -> None:
    """Format, quality, loudness, and where the new files go."""
    group = parser.add_argument_group("the new file")
    group.add_argument(
        "--format",
        choices=list(FORMAT_EXTENSIONS),
        help="mp3 (normal), flac or wav (lossless), m4a (Apple), opus (small)",
    )
    group.add_argument(
        "--quality",
        type=int,
        choices=range(10),
        metavar="0..9",
        help="MP3 quality, 0 = best, 9 = smallest "
        f"(normal {_DEFAULTS.quality}, BEST {_BEST.quality})",
    )
    group.add_argument(
        "--bitrate",
        type=_bitrate_value,
        metavar="KBPS",
        help="constant bitrate for mp3/m4a/opus, 320 = the most MP3 allows; "
        f"'auto' uses --quality instead (BEST {_BEST.bitrate})",
    )
    group.add_argument(
        "--loudness",
        type=_loudness_value,
        metavar="LUFS",
        help="final loudness: -14 = Spotify/YouTube, -16 = Apple Music, "
        "match = the same as the original song, or off "
        f"(normal off, BEST {_BEST.loudness_target:g})",
    )
    group.add_argument(
        "--exact-loudness",
        action="store_const",
        const=True,
        help="always hit the --loudness target exactly (light peak limiting)",
    )
    group.add_argument(
        "--limiter-ceiling",
        type=float,
        metavar="0.0625..1",
        help="the loudest a peak may get, stops crackles "
        f"(normal {_DEFAULTS.limiter_ceiling}, BEST {_BEST.limiter_ceiling})",
    )
    group.add_argument(
        "--output-dir",
        type=Path,
        metavar="FOLDER",
        help="save the new songs in this folder (normal: next to each original)",
    )
    group.add_argument(
        "--name",
        choices=NAME_STYLES,
        help="8d = '<song> (8D).mp3' (normal); original = keep the song's own name",
    )
    group.add_argument(
        "--replace",
        action="store_true",
        help="after each 8D song is saved, move its ORIGINAL to the Recycle Bin, or "
        "rename it '<song> (original)' where there is none (the new file takes the "
        "original name unless --name 8d)",
    )
    group.add_argument(
        "--overwrite",
        action="store_true",
        help="allow replacing a file that already has the output name",
    )
    group.add_argument(
        "--start", type=_time_value, metavar="TIME", help="begin here, e.g. 1:30"
    )
    group.add_argument(
        "--end", type=_time_value, metavar="TIME", help="stop here, e.g. 2:00"
    )
    group.add_argument(
        "--no-cover", action="store_true", help="don't copy the album art"
    )
    group.add_argument(
        "--keep-title",
        action="store_true",
        help="don't add ' (8D)' to the song's title tag",
    )
    group.add_argument(
        "--no-check",
        action="store_true",
        help="skip measuring the finished file (loudness, peaks, mono)",
    )


def _add_extra_options(parser: argparse.ArgumentParser) -> None:
    """Folders, previews, styles and the other switches."""
    group = parser.add_argument_group("more")
    group.add_argument(
        "--recursive",
        action="store_true",
        help="with a folder: include songs in its sub-folders too",
    )
    group.add_argument(
        "--jobs",
        type=_jobs_value,
        metavar="N",
        help=f"with a folder: make N songs at once (normal {default_jobs()})",
    )
    group.add_argument(
        "--preview",
        type=float,
        nargs="?",
        const=30.0,
        metavar="SECONDS",
        help="only make a short sample from the loudest part (normal 30 s)",
    )
    group.add_argument(
        "--compare",
        action="store_true",
        help="make one file: original (A), then 8D (B), same loudness",
    )
    group.add_argument(
        "--play", action="store_true", help="open the new file in your music player"
    )
    group.add_argument(
        "--save-preset",
        metavar="NAME",
        help="save these settings as your own style (use it with --preset NAME)",
    )
    group.add_argument(
        "--gui", action="store_true", help="open the Audio8D window instead"
    )
    group.add_argument(
        "--verbose",
        action="store_true",
        help="show extra technical details, useful when something goes wrong",
    )
    group.add_argument(
        "--list-presets",
        action=_ListPresetsAction,
        help="show every ready-made style with its exact values, then stop",
    )
    group.add_argument(
        "--version",
        action="version",
        version=f"audio8d {__version__} - developed by Gehan Fernando",
        help="show the version number and who made it",
    )


def create_parser() -> argparse.ArgumentParser:
    """Build the argument parser; kept separate so tests can poke at it."""
    parser = _FriendlyParser(
        prog="audio8d",
        description=_QUICK_START,
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        help="the song (mp3, flac, wav, ...) or a FOLDER of songs",
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="where to save the 8D song (leave out: '<song> (8D).mp3')",
    )
    _add_sound_options(parser)
    _add_output_options(parser)
    _add_extra_options(parser)
    return parser


# The typed knobs and the EffectConfig field each one sets
_KNOBS = {
    "rotation_seconds": "rotation_seconds",
    "intensity": "intensity",
    "ambience": "ambience",
    "limiter_ceiling": "limiter_ceiling",
    "quality": "quality",
    "bitrate": "bitrate",
    "exact_loudness": "exact_loudness",
    "engine": "engine",
    "path": "path",
    "direction": "direction",
    "bass": "bass_hz",
    "elevation": "elevation",
    "fade": "fade_seconds",
    "speed_curve": "speed_curve",
    "intensity_curve": "intensity_curve",
    "beat_sync": "beat_sync",
    "bpm": "bpm",
    "vocals": "vocals",
    "format": "output_format",
}


def resolve_config(
    args: argparse.Namespace, presets: dict[str, Preset] | None = None
) -> EffectConfig:
    """Start from the chosen preset (or the defaults), then apply any typed knobs."""
    known = presets if presets is not None else known_presets()
    if args.preset and args.preset not in known:
        raise InputValidationError(
            f"There is no style called '{args.preset}'. Choose from: {', '.join(known)}"
        )
    base = known[args.preset].config if args.preset else EffectConfig()

    overrides: dict[str, object] = {
        field: getattr(args, option)
        for option, field in _KNOBS.items()
        if getattr(args, option, None) is not None
    }
    if overrides.get("bitrate") == BITRATE_AUTO:
        overrides["bitrate"] = None
    if args.loudness is not None:
        overrides["loudness_target"] = (
            None if args.loudness in (LOUDNESS_OFF, LOUDNESS_MATCH) else args.loudness
        )
        overrides["match_loudness"] = args.loudness == LOUDNESS_MATCH
    # An output name like "song.flac" chooses the format when --format doesn't
    output = getattr(args, "output", None)
    if args.format is None and output is not None:
        inferred = format_for_extension(output)
        if inferred is not None:
            overrides["output_format"] = inferred

    config = dataclasses.replace(base, **overrides)
    if args.speakers:
        config = speaker_safe(config)
    return config


def used_only_defaults(args: argparse.Namespace) -> bool:
    """True when the user typed no preset and no sound knobs at all."""
    typed = [getattr(args, option) for option in _KNOBS] + [args.preset, args.loudness]
    return all(value is None for value in typed) and not args.speakers
