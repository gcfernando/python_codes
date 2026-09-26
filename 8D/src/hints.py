# Developed by Gehan Fernando
"""Plain-word fixes for every error a user can hit, so nobody is left stuck."""

from .core.errors import Audio8DError, DependencyError
from .core.presets import PRESETS, RECOMMENDED_PRESET

_BEST = PRESETS[RECOMMENDED_PRESET].config

# Matched against the start of each error message; the first match wins
_FIXES = (
    (
        "Missing required executable",
        "put ffmpeg.exe and ffprobe.exe inside the src folder (README part 5, Step 2).",
    ),
    (
        "This FFmpeg build",
        "download the 'essentials' build from gyan.dev "
        "and copy ffmpeg.exe + ffprobe.exe into src.",
    ),
    (
        "Input file does not exist",
        "check the name and folder. "
        "Easiest: type audio8d alone, press Enter, drag the song in.",
    ),
    (
        "Input path is not a regular file",
        "that is a folder. Give a song file inside it instead.",
    ),
    (
        "Input file is empty",
        "the file is empty (0 bytes). Copy or download the song again.",
    ),
    (
        "Cannot inspect input file",
        "make sure the song isn't open in another program, then try again.",
    ),
    (
        "Command failed with exit code",
        "this file doesn't look like music. Check that it plays in your music app.",
    ),
    (
        "The input file does not contain a usable audio stream",
        "this file has no sound in it. Pick a file that plays music.",
    ),
    ("FFprobe returned", "this file looks damaged. Try another copy of the song."),
    (
        "The input audio reports",
        "this file looks damaged. Try another copy of the song.",
    ),
    (
        "Output file must use the .mp3 extension",
        'end the new name with .mp3, e.g. "My Song (8D).mp3".',
    ),
    (
        "Cannot create output directory",
        "save somewhere you are allowed to write, like your Music folder.",
    ),
    (
        "Output parent is not a directory",
        "save into a normal folder, like your Music folder.",
    ),
    (
        "Output path exists but is not a regular file",
        "a folder has that name. Pick another name.",
    ),
    (
        "Output already exists",
        "add --overwrite to replace it, or give the new song a different name.",
    ),
    (
        "Input and output paths must be different",
        "give the new song a different name, or just leave the second name out.",
    ),
    (
        "rotation_seconds",
        "use a number from 2 to 100, "
        f"e.g. --rotation-seconds {_BEST.rotation_seconds:g} (best).",
    ),
    (
        "intensity",
        f"use a number from 0 to 1, e.g. --intensity {_BEST.intensity:.2f} (best).",
    ),
    (
        "ambience",
        f"use a number from 0 to 1, e.g. --ambience {_BEST.ambience:.2f} (best).",
    ),
    (
        "limiter_ceiling",
        f"use 0.0625 to 1, e.g. --limiter-ceiling {_BEST.limiter_ceiling:.2f} (best).",
    ),
    (
        "mp3_bitrate",
        "use 128, 160, 192, 224, 256 or 320 kbps, e.g. --bitrate 320 (best).",
    ),
    (
        "FFmpeg did not report a loudness",
        "try again with --verbose; if it keeps happening, add --loudness off.",
    ),
    (
        "FFmpeg's loudness summary",
        "try again with --verbose; if it keeps happening, add --loudness off.",
    ),
    (
        "mp3_quality",
        f"use a whole number from 0 to 9, e.g. --quality {_BEST.mp3_quality} (best).",
    ),
    (
        "loudness_target",
        "use a number from -30 to -5, e.g. --loudness -14 (best), or 'off'.",
    ),
    ("FFmpeg conversion failed", "try again with --verbose added to see more details."),
    (
        "FFmpeg reported success",
        "try again; if it keeps happening, try with --verbose.",
    ),
    (
        "Output appeared while conversion was running",
        "try again with a different name for the new song.",
    ),
    (
        "Conversion cancelled by user",
        "no problem! Nothing was left behind. Run it again whenever you like.",
    ),
    (
        "Unable to publish",
        "check the disk has free space and the drive is still plugged in.",
    ),
    ("I/O error", "check the disk has free space and the drive is still plugged in."),
)


# Matched anywhere in argparse's message; the first match wins, so order matters
_USAGE_FIXES = (
    (
        "required: input",
        "you forgot the song. "
        "Type its name after audio8d, or run audio8d alone for help.",
    ),
    (
        "--quality",
        "quality is a whole number from 0 to 9. "
        f"For the very best: --bitrate {_BEST.mp3_bitrate}",
    ),
    (
        "--bitrate",
        "bitrate must be 128, 160, 192, 224, 256 or 320. Best: --bitrate 320",
    ),
    (
        "--preset",
        f"use one of: {', '.join(PRESETS)}. Best: --preset {RECOMMENDED_PRESET}",
    ),
    ("--loudness", "write a number such as -14 (best), or the word off."),
    (
        "unrecognized arguments",
        'one word was not understood. Put song names with spaces inside "quotes".',
    ),
    (
        "expected one argument",
        "that option needs a value after it, e.g. --intensity 0.8",
    ),
    ("invalid float value", "that option needs a number, e.g. --intensity 0.8"),
)


def fix_for(error: Audio8DError) -> str | None:
    """The friendly fix for an Audio8D error, if we know one."""
    message = str(error)
    # A failing tool check means FFmpeg itself is broken, not the song
    if isinstance(error, DependencyError) and message.startswith(
        ("Command failed", "Failed to start")
    ):
        return (
            "FFmpeg would not run. "
            "Download the 'essentials' build from gyan.dev into src."
        )
    if message.startswith("Failed to start"):
        return (
            "FFmpeg would not start. "
            "Put fresh copies of ffmpeg.exe and ffprobe.exe in src."
        )
    for start, fix in _FIXES:
        if message.startswith(start):
            return fix
    return None


def usage_fix_for(message: str) -> str:
    """The friendly fix for a mistake in how the command was typed."""
    for clue, fix in _USAGE_FIXES:
        if clue in message:
            return fix
    return "check the spelling, or type audio8d --help to see every option."
