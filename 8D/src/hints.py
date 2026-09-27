# Developed by ::> Gehan Fernando
"""Plain-word fixes for every error a user can hit, so nobody is left stuck."""

import re

from .core.errors import Audio8DError, DependencyError
from .core.presets import PRESETS, RECOMMENDED_PRESET

_BEST = PRESETS[RECOMMENDED_PRESET].config

# Matched against the start of each error message; the first match wins
_FIXES = (
    (
        "Missing required executable",
        "put ffmpeg.exe and ffprobe.exe in the bin\\executable folder of Audio8D.",
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
        "Output file must use the",
        "end the new name with the format's extension (.mp3, .flac, .wav, .m4a "
        'or .opus), e.g. "My Song (8D).mp3", or pick it with --format.',
    ),
    (
        "Input folder does not exist",
        "check the folder name. Easiest: type audio8d alone and drag the folder in.",
    ),
    (
        "No songs found",
        "that folder has no music files in it. Add --recursive to look in "
        "sub-folders too.",
    ),
    (
        "The chosen start and end",
        "make --start earlier than --end, and both inside the song, e.g. "
        "--start 1:00 --end 1:30.",
    ),
    (
        "Keeping vocals in the centre needs Demucs",
        "leave out --vocals center, or get Demucs as the message says.",
    ),
    (
        "Demucs could not split",
        "try again without --vocals center; the rest of Audio8D works as normal.",
    ),
    (
        "Could not remove the original",
        "your new song is saved. Close any program using the original, then delete "
        "it yourself.",
    ),
    (
        "Cannot read your styles file",
        "check the file isn't open elsewhere, or delete it to start fresh.",
    ),
    (
        "Cannot save your styles file",
        "check you can write to your user folder, then try again.",
    ),
    (
        "presets.toml",
        "fix that line in your styles file (see --list-presets for where it is).",
    ),
    (
        "already have a style called",
        "pick a name you haven't used yet, like PartyMix2.",
    ),
    (
        "style names",
        "use words with letters and numbers, like SunsetDrive or PartyMix2.",
    ),
    (
        "Style names start",
        "start the name with a letter, like Night2Day.",
    ),
    (
        "isn't a PascalCase name",
        "use words with letters and numbers, like SunsetDrive or PartyMix2.",
    ),
    (
        "This style file can't be imported",
        "choose a style file exported from Audio8D (Your styles, Export). Nothing "
        "was changed.",
    ),
    (
        "There is no saved style called",
        "check the name on the Your styles page.",
    ),
    (
        "style ",
        "fix that style in your styles file, or save it again with --save-preset.",
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
        "bitrate",
        "use 128, 160, 192, 224, 256 or 320 kbps, e.g. --bitrate 320 (best).",
    ),
    ("bass_hz", "use 0 (off) or a number from 40 to 250, e.g. --bass 120 (best)."),
    ("elevation", "use a number from 0 to 1, e.g. --elevation 0.5."),
    ("fade_seconds", "use 0 to 30 seconds, e.g. --fade 3."),
    ("bpm", "use a tempo from 40 to 240, e.g. --bpm 120, or leave it out."),
    (
        "speed_curve",
        'write TIME=SECONDS pairs going forwards, e.g. --speed-curve "0=10, 1:00=6".',
    ),
    (
        "intensity_curve",
        "write TIME=AMOUNT pairs going forwards, e.g. "
        '--intensity-curve "0=0.6, 1:00=0.95".',
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
        "quality",
        f"use a whole number from 0 to 9, e.g. --quality {_BEST.quality} (best).",
    ),
    (
        "loudness_target",
        "use a number from -30 to -5, e.g. --loudness -14 (best), or 'off'.",
    ),
    ("FFmpeg conversion failed", "try again with --verbose added to see more details."),
    ("Conversion cancelled", "no problem! Nothing was left behind."),
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


# Matched anywhere in an Audio8D error, after the start-of-message list above
_ANYWHERE_FIXES = (
    ("is not a time", "write times like 90 (seconds) or 1:30 (minutes:seconds)."),
    ("needs the form TIME=VALUE", 'write pairs like "0=8, 1:00=6, 2:30=8".'),
    ("TIME=VALUE", 'write pairs like "0=8, 1:00=6, 2:30=8".'),
    (
        "is not a number or a range",
        "type numbers like 1,3,5-7, or press Enter for all.",
    ),
    ("is outside 1 to", "only use numbers from the list, or press Enter for all."),
    ("is a built-in style", "pick another name for your own style."),
)


# Matched anywhere in argparse's message; the first match wins, so order matters
_USAGE_FIXES = (
    (
        "required: input",
        "you forgot the song or folder. "
        "Type its name after audio8d, or run audio8d alone for help.",
    ),
    (
        "--quality",
        "quality is a whole number from 0 to 9. "
        f"For the very best: --bitrate {_BEST.bitrate}",
    ),
    (
        "--bitrate",
        "bitrate must be 128, 160, 192, 224, 256, 320 or auto. Best: --bitrate 320",
    ),
    (
        "--preset",
        f"use one of: {', '.join(PRESETS)}. Best: --preset {RECOMMENDED_PRESET}",
    ),
    ("--loudness", "write a number such as -14 (best), or the word match or off."),
    ("--jobs", "write how many songs to make at once, from 1 to 16, e.g. --jobs 4."),
    ("--format", "use one of: mp3, flac, wav, m4a, opus. Best: mp3 (or flac)."),
    ("--path", "use one of: circle, arc, figure8, wander."),
    ("--direction", "use clockwise or counterclockwise."),
    ("--name", "use 8d (adds ' (8D)') or original (keeps the song's own name)."),
    ("--start", "write a time such as 90 or 1:30."),
    ("--end", "write a time such as 90 or 1:30."),
    ("--vocals", "use move (normal) or center (keeps the singer in the middle)."),
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


# Messages that carry FFmpeg's whole log after this start
_TOOL_FAILURES = ("FFmpeg conversion failed", "Command failed with exit code")


def short_message(error: BaseException) -> str:
    """The error in one readable line; FFmpeg's full log is kept for the log file."""
    message = str(error)
    if not message.startswith(_TOOL_FAILURES):
        return message
    # FFmpeg's last line says what went wrong, after a tag or a file name
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    reason = re.sub(r"^\[[^\]]*\]\s*", "", lines[-1])
    reason = re.sub(r"^.*[\\/][^:\\/]*:\s+", "", reason)
    if len(reason) > 160:
        reason = reason[:157] + "..."
    return f"FFmpeg stopped: {reason}"


def fix_for(error: Audio8DError) -> str | None:
    """The friendly fix for an Audio8D error, if we know one."""
    message = str(error)
    # A failing tool check means FFmpeg itself is broken, not the song
    if isinstance(error, DependencyError) and message.startswith(
        ("Command failed", "Failed to start")
    ):
        return (
            "FFmpeg would not run. Put the 'essentials' build from gyan.dev "
            "in bin\\executable."
        )
    if message.startswith("Failed to start"):
        return (
            "FFmpeg would not start. "
            "Put fresh copies of ffmpeg.exe and ffprobe.exe in bin\\executable."
        )
    # Windows and FFmpeg word this differently, but it always means a locked folder
    if any(clue in message for clue in ("Permission denied", "Access is denied")):
        return (
            "Audio8D isn't allowed to write there. Choose another folder, such as "
            "your Music folder, or close the program that has the file open."
        )
    for start, fix in _FIXES:
        if message.startswith(start):
            return fix
    for clue, fix in _ANYWHERE_FIXES:
        if clue in message:
            return fix
    return None


def usage_fix_for(message: str) -> str:
    """The friendly fix for a mistake in how the command was typed."""
    for clue, fix in _USAGE_FIXES:
        if clue in message:
            return fix
    return "check the spelling, or type audio8d --help to see every option."
