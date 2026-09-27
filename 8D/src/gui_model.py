# Developed by ::> Gehan Fernando
"""Everything the Audio8D window decides, kept apart from the widgets.

The window only reads and writes a GuiSettings. Turning that into the same
EffectConfig, ConvertOptions and output paths the command line uses, checking
it, and explaining it in plain words all happen here, where it can be tested
without a screen. Nothing here converts audio: that stays in pipeline/batch.
"""

import dataclasses
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from . import display
from .batch import MAX_JOBS, BatchItem, default_jobs
from .core.errors import InputValidationError
from .core.parsing import format_keyframes, format_time, parse_keyframes, parse_time
from .core.presets import PRESETS, RECOMMENDED_PRESET, Preset
from .core.settings import FORMAT_EXTENSIONS, EffectConfig, speaker_safe
from .core.types import AudioStreamInfo, Trim
from .core.user_presets import name_key
from .files import default_output_for
from .pipeline import ConvertOptions

# What the loudness choices in the window mean, in LUFS (None = natural level)
LOUDNESS_CHOICES = {
    "Spotify / YouTube (-14)": -14.0,
    "Apple Music (-16)": -16.0,
    "TV & radio (-23)": -23.0,
    "Same as original": "match",
    "Natural (off)": None,
    "Custom…": "custom",
}
BITRATE_CHOICES = ("Auto", "128", "160", "192", "224", "256", "320")
ORIGINAL_CHOICES = ("keep", "replace", "replace-8d")

# The command line's words for things, and the window's words for the same things
_GUI_WORDS = (
    (r"--rotation-seconds (-?[0-9]+(?:\.[0-9]+)?)", r"Spin \1 s (Sound page)"),
    (r"--intensity (-?[0-9]+(?:\.[0-9]+)?)", r"Movement \1 (Sound page)"),
    (r"--ambience (-?[0-9]+(?:\.[0-9]+)?)", r"Room \1 (Sound page)"),
    (r"--bitrate 320", "Bitrate 320 (Output page, Advanced)"),
    (r"--bitrate (-?[0-9]+(?:\.[0-9]+)?)", r"Bitrate \1 (Output page, Advanced)"),
    (
        r"--limiter-ceiling (-?[0-9]+(?:\.[0-9]+)?)",
        r"Peak roof \1 (Output page, Advanced)",
    ),
    (r"--loudness -14", "Loudness: Spotify / YouTube (Output page)"),
    (r"--loudness (-?[0-9]+(?:\.[0-9]+)?|match|off)", r"Loudness \1 (Output page)"),
    (r"--bass 120", "Keep the bass in the middle at 120 Hz (Sound page, Advanced)"),
    (r"--preset studio", "the Studio style (Sound page)"),
    (r"--speakers", "'Safe for speakers too' (Sound page, Advanced)"),
    (r"--quality (-?[0-9]+(?:\.[0-9]+)?)", r"MP3 quality \1 (Output page, Advanced)"),
    (r"--overwrite", "'Replace 8D files that already exist' (Output page, Advanced)"),
    (r"--vocals center", "'Keep the singer in the middle'"),
    (r"--recursive", "'Include songs in sub-folders' (Songs page)"),
    (r"--format", "the file type (Output page)"),
    (r"--start", "the trim times (Output page, Advanced)"),
    (r"--end", "the trim times (Output page, Advanced)"),
    (r"--verbose", "'Show technical details' (Settings)"),
    (r"with --save-preset", "on the Your styles page"),
    (r"--elevation (-?[0-9]+(?:\.[0-9]+)?)", r"Height \1 (Sound page, Advanced)"),
    (r"--fade (-?[0-9]+(?:\.[0-9]+)?)", r"Ease in and out \1 s (Sound page, Advanced)"),
    (r"--bpm (-?[0-9]+(?:\.[0-9]+)?)", r"Tempo \1 (Sound page, Advanced)"),
    (r'--speed-curve ("[^"]*")', r"\1 in 'Speed over time' (Sound page, Advanced)"),
    (
        r'--intensity-curve ("[^"]*")',
        r"\1 in 'Movement over time' (Sound page, Advanced)",
    ),
    (r"see --list-presets for where it is", "its place is shown on Your styles"),
    (
        r"type audio8d alone and drag the folder in",
        "drag the folder onto the window",
    ),
    (
        r"type audio8d alone, press Enter, drag the song in",
        "drag the song onto the window",
    ),
    # The curve checks name their settings the programmer's way
    (r"\bspeed_curve\b", "Speed over time"),
    (r"\bintensity_curve\b", "Movement over time"),
)


def gui_words(text: str) -> str:
    """Rewrite a command-line hint so it names the window's controls instead."""
    for pattern, replacement in _GUI_WORDS:
        text = re.sub(pattern, replacement, text)
    return text


@dataclass
class GuiSettings:  # pylint: disable=too-many-instance-attributes
    """Every choice on the window's pages, starting from a style."""

    style: str = RECOMMENDED_PRESET
    # The sound knobs; filled from the style, then changed by the controls
    sound: EffectConfig = field(default_factory=EffectConfig)
    speakers: bool = False
    # Typed values, kept as text until the conversion so mistakes can be shown
    speed_curve_text: str = ""
    intensity_curve_text: str = ""
    bpm_text: str = ""
    custom_loudness_text: str = "-14"
    loudness_is_custom: bool = False
    # Songs page
    recursive: bool = True
    # Output page
    destination: str = ""
    originals: str = "keep"
    name_style: str = "8d"
    custom_name: str = ""
    overwrite: bool = False
    keep_cover: bool = True
    tag_title: bool = True
    check: bool = True
    trim_start: str = ""
    trim_end: str = ""
    jobs: int = field(default_factory=default_jobs)
    play_when_done: bool = False
    preview_seconds: int = 30
    # Settings page
    verbose: bool = False
    # Songs that use a style of their own instead of the one for all songs
    song_styles: dict[Path, str] = field(default_factory=dict)

    def apply_style(self, preset: Preset) -> None:
        """Take every sound and format knob from a style."""
        self.style = preset.name
        self.sound = preset.config
        self.speed_curve_text = format_keyframes(preset.config.speed_curve)
        self.intensity_curve_text = format_keyframes(preset.config.intensity_curve)
        self.bpm_text = f"{preset.config.bpm:g}" if preset.config.bpm else ""
        self.loudness_is_custom = False

    def change(self, **knobs: object) -> None:
        """Change some sound knobs, keeping the rest."""
        self.sound = dataclasses.replace(self.sound, **knobs)

    def differs_from(self, preset: Preset) -> bool:
        """True when the knobs no longer match the chosen style exactly."""
        try:
            return (
                config_for(self, with_speakers=False) != preset.config or self.speakers
            )
        except InputValidationError:
            return True


def _typed_number(text: str, what: str, low: float, high: float) -> float | None:
    """A typed number in a range, or None when the box is empty."""
    if not text.strip():
        return None
    try:
        value = float(text.strip().replace(",", "."))
    except ValueError:
        raise InputValidationError(f"{what} must be a number") from None
    if not low <= value <= high:
        raise InputValidationError(f"{what} must be between {low:g} and {high:g}")
    return value


def config_for(settings: GuiSettings, *, with_speakers: bool = True) -> EffectConfig:
    """The exact EffectConfig the conversion will use (raises if something's wrong)."""
    config = settings.sound
    try:
        speed = (
            parse_keyframes(settings.speed_curve_text)
            if settings.speed_curve_text.strip()
            else ()
        )
        amount = (
            parse_keyframes(settings.intensity_curve_text)
            if settings.intensity_curve_text.strip()
            else ()
        )
    except InputValidationError as exc:
        raise InputValidationError(f"Changes over time: {exc}") from None
    bpm = _typed_number(settings.bpm_text, "The tempo (BPM)", 40, 240)
    config = dataclasses.replace(
        config, speed_curve=speed, intensity_curve=amount, bpm=bpm
    )
    if settings.loudness_is_custom:
        target = _typed_number(settings.custom_loudness_text, "The loudness", -30, -5)
        if target is None:
            raise InputValidationError("Type a loudness between -30 and -5, e.g. -14")
        config = dataclasses.replace(
            config, loudness_target=target, match_loudness=False
        )
    if with_speakers and settings.speakers:
        config = speaker_safe(config)
    config.validate()
    return config


def trim_for(settings: GuiSettings) -> Trim | None:
    """The chosen part of the song, or None for all of it."""
    start = parse_time(settings.trim_start) if settings.trim_start.strip() else None
    end = parse_time(settings.trim_end) if settings.trim_end.strip() else None
    if start is None and end is None:
        return None
    if start is not None and end is not None and end <= start:
        raise InputValidationError("The chosen start and end leave no sound to convert")
    return Trim(start, end)


def options_for(settings: GuiSettings) -> ConvertOptions:
    """What happens to the files, beyond the sound."""
    return ConvertOptions(
        trim=trim_for(settings),
        keep_cover=settings.keep_cover,
        tag_title=settings.tag_title,
        check=settings.check,
        replace_original=settings.originals != "keep",
    )


def destination_for(settings: GuiSettings) -> Path | None:
    """The chosen output folder, or None for 'next to each original'."""
    text = settings.destination.strip()
    return Path(text).expanduser() if text else None


def name_style_for(settings: GuiSettings) -> str:
    """'8d' or 'original' for the new file names (replacing implies original)."""
    if settings.originals == "replace":
        return "original"
    if settings.originals == "replace-8d":
        return "8d"
    return "original" if settings.name_style == "original" else "8d"


def style_for(
    settings: GuiSettings, song: Path, styles: Mapping[str, Preset]
) -> Preset | None:
    """The song's own style, or None when it uses the style for all songs."""
    name = settings.song_styles.get(song)
    return styles.get(name) if name else None


def song_config(
    settings: GuiSettings, song: Path, styles: Mapping[str, Preset] | None = None
) -> EffectConfig:
    """The exact settings one song gets: its own style as it is, or the shared ones."""
    own = style_for(settings, song, styles or {})
    return own.config if own else config_for(settings)


def items_for(
    settings: GuiSettings,
    songs: Sequence[tuple[Path, Path | None]],
    styles: Mapping[str, Preset] | None = None,
) -> list[BatchItem]:
    """(song, folder it was added from) pairs -> songs, output paths and settings."""
    shared = config_for(settings)
    output_dir = destination_for(settings)

    def own(song: Path) -> EffectConfig | None:
        """A song's own style's settings, if it has one."""
        style = style_for(settings, song, styles or {})
        return style.config if style else None

    if (
        settings.name_style == "custom"
        and len(songs) == 1
        and settings.originals == "keep"
    ):
        song = songs[0][0]
        name = settings.custom_name.strip()
        stem = (
            name[: -len(Path(name).suffix)]
            if Path(name).suffix.lower() in FORMAT_EXTENSIONS.values()
            else name
        )
        folder = output_dir or song.parent
        config = own(song) or shared
        return [BatchItem(song, folder / f"{stem}{config.extension}", own(song))]
    return [
        BatchItem(
            song,
            default_output_for(
                song,
                (own(song) or shared).extension,
                output_dir=output_dir,
                name_style=name_style_for(settings),
                relative_to=folder,
            ),
            own(song),
        )
        for song, folder in songs
    ]


_BAD_NAME = re.compile(r'[<>:"/\\|?*]')


def _missing_styles(
    settings: GuiSettings,
    songs: Sequence[tuple[Path, Path | None]],
    styles: Mapping[str, Preset] | None,
) -> list[tuple[str, str]]:
    """Songs whose own style no longer exists (deleted, or its file is broken)."""
    known = styles if styles is not None else PRESETS
    return [
        (
            "sound",
            f"'{song.stem}' uses the style '{name}', which no longer exists. "
            "Choose another style for it.",
        )
        for song, _folder in songs
        if (name := settings.song_styles.get(song)) and name not in known
    ]


def problems(
    settings: GuiSettings,
    songs: Sequence[tuple[Path, Path | None]],
    styles: Mapping[str, Preset] | None = None,
) -> list[tuple[str, str]]:
    """(page, plain-word reason) for everything that stops a conversion starting."""
    found: list[tuple[str, str]] = []
    if not songs:
        found.append(("songs", "Add at least one song or folder first."))
    found += _missing_styles(settings, songs, styles)
    try:
        config_for(settings)
    except InputValidationError as exc:
        page = (
            "output"
            if "loudness" in str(exc).lower() or "bitrate" in str(exc)
            else "sound"
        )
        found.append((page, gui_words(str(exc))))
    try:
        trim_for(settings)
    except InputValidationError as exc:
        found.append(("output", f"Trim: {exc}. Write times like 90 or 1:30."))
    destination = destination_for(settings)
    if (
        settings.destination.strip() == ""
        and settings.name_style == "original"
        and settings.originals == "keep"
    ):
        found.append(
            (
                "output",
                "Keeping the original name next to the original would overwrite it. "
                "Choose a 'Save in' folder, or pick 'Replace them'.",
            )
        )
    if destination is not None and destination.exists() and not destination.is_dir():
        found.append(("output", "The 'Save in' place is a file, not a folder."))
    if settings.name_style == "custom":
        name = settings.custom_name.strip()
        if len(songs) != 1:
            found.append(
                ("output", "A custom file name only works with exactly one song.")
            )
        elif not name:
            found.append(
                ("output", "Type the custom file name, or choose another naming.")
            )
        elif _BAD_NAME.search(name):
            found.append(("output", "File names can't contain  < > : \" / \\ | ? *"))
    if not 1 <= settings.jobs <= MAX_JOBS:
        found.append(("output", f"Songs at once must be between 1 and {MAX_JOBS}."))
    if settings.originals not in ORIGINAL_CHOICES:
        found.append(("output", "Choose what happens to the originals."))
    return found


def warnings(settings: GuiSettings) -> list[str]:
    """Plain-word heads-ups (the same advice the terminal gives), in window words."""
    try:
        config = config_for(settings)
    except InputValidationError:
        return []
    notes = [gui_words(note) for note in display.advice(config)]
    if settings.originals != "keep":
        notes.append(
            "The original songs will be moved to the Recycle Bin after their 8D "
            "versions are saved (or renamed '<song> (original)' where there is none)."
        )
    if settings.overwrite:
        notes.append("8D files that already exist will be replaced.")
    if config.vocals == "center":
        notes.append("Keeping the singer in the middle takes a minute or two per song.")
    return notes


def style_label(name: str, styles: Mapping[str, Preset] | None = None) -> str:
    """How a style's name is shown: Studio, Streaming, or yours as you saved it."""
    preset = (styles or PRESETS).get(name) or PRESETS.get(name)
    return preset.label if preset else name


def own_styles_line(
    settings: GuiSettings,
    songs: Sequence[tuple[Path, Path | None]],
    styles: Mapping[str, Preset] | None = None,
) -> str | None:
    """'2 songs with their own style (City Lights: Lossless, …)', or None."""
    chosen = [
        (song, settings.song_styles[song])
        for song, _folder in songs
        if song in settings.song_styles
    ]
    if not chosen:
        return None
    shown = ", ".join(
        f"{song.stem}: {style_label(name, styles)}" for song, name in chosen[:3]
    )
    more = f", and {len(chosen) - 3} more" if len(chosen) > 3 else ""
    count = "1 song with its" if len(chosen) == 1 else f"{len(chosen)} songs with their"
    return f"{count} own style ({shown}{more})"


def review(
    settings: GuiSettings, styles: Mapping[str, Preset] | None = None
) -> list[tuple[str, str]]:
    """(label, plain-word value) pairs describing every choice, for the Review page."""
    config = config_for(settings)
    rows = [
        (
            "Style",
            style_label(settings.style, styles)
            + ("  (changed)" if settings.speakers else ""),
        ),
        ("Sound", display.describe_sound(config)),
        ("Spin", display.describe_spin(config)),
        (
            "Movement",
            f"{config.intensity:.2f} ({display.describe_movement(config.intensity)})",
        ),
        ("Bass", display.describe_bass(config.bass_hz)),
        ("Room", f"{config.ambience:.2f} ({display.describe_room(config.ambience)})"),
        (
            "File type",
            display.describe_quality(
                config.quality, config.bitrate, config.output_format
            ),
        ),
        (
            "Loudness",
            "the same as the original song"
            if config.match_loudness
            else display.describe_loudness(config.loudness_target),
        ),
        ("Peak roof", display.describe_ceiling(config.limiter_ceiling)),
    ]
    extras = display.extras(config, trim_for(settings))
    if extras:
        rows.append(("Extras", ", ".join(extras)))
    destination = destination_for(settings)
    rows.append(
        ("Save in", str(destination) if destination else "next to each original song")
    )
    naming = {
        "8d": "'<song> (8D)'",
        "original": "the song's own name",
        "custom": f"'{settings.custom_name.strip()}'"
        if settings.custom_name.strip()
        else "a name of your own (not typed yet)",
    }[settings.name_style if settings.originals == "keep" else name_style_for(settings)]
    rows.append(("New names", naming))
    rows.append(
        (
            "Originals",
            {
                "keep": "kept as they are",
                "replace": "replaced (moved to the Recycle Bin)",
                "replace-8d": "moved to the Recycle Bin; new files keep '(8D)'",
            }[settings.originals],
        )
    )
    files = []
    if settings.keep_cover:
        files.append("album art kept")
    if settings.tag_title:
        files.append("' (8D)' added to titles")
    if settings.check:
        files.append("each song checked")
    if settings.overwrite:
        files.append("existing 8D files replaced")
    rows.append(("Files", ", ".join(files) or "nothing extra"))
    rows.append(
        ("Speed", f"{settings.jobs} song{'s' if settings.jobs != 1 else ''} at once")
    )
    return rows


def describe(settings: GuiSettings) -> str:
    """One line summing up the choices, for the status bar."""
    config = config_for(settings)
    parts = [
        "3D" if config.engine == "3d" else "panning",
        config.path,
        "beat sync"
        if config.beat_sync or config.bpm
        else f"{config.rotation_seconds:g} s",
        config.output_format.upper(),
    ]
    if config.match_loudness:
        parts.append("original loudness")
    elif config.loudness_target is not None:
        parts.append(f"{config.loudness_target:g} LUFS")
    if settings.speakers:
        parts.append("speaker-safe")
    own = len(settings.song_styles)
    if own:
        parts.append(f"{own} song{'s' if own != 1 else ''} with own style")
    return " · ".join(parts)


def describe_curve(text: str, unit: str) -> str:
    """'10 s from 0:00, 6 s from 1:00' - a typed curve read back in words."""
    frames = parse_keyframes(text)
    return ", then ".join(
        f"{value:g}{unit} at {format_time(time)}" for time, value in frames
    )


# ------------------------------------------------------ creating your own style

# Each question's choices: the words people see -> the answer kept
MUSIC_CHOICES = {
    "Strong beat": "beat",
    "Calm": "calm",
    "Big and loud": "big",
    "Talking": "talk",
    "A bit of everything": "mixed",
}
MOVEMENT_CHOICES = {"Gentle": "gentle", "Clear": "clear", "Big": "big"}
SPEED_CHOICES = {
    "Slow": "slow",
    "Normal": "normal",
    "Fast": "fast",
    "With the beat": "beat",
}
ROOM_CHOICES = {"None": "none", "A little": "little", "A big hall": "hall"}
PLACE_CHOICES = {"Headphones": "headphones", "Speakers or a car too": "speakers"}
FILE_CHOICES = {"MP3": "mp3", "FLAC": "flac", "M4A": "m4a"}
LEVEL_CHOICES = {
    "Like music apps": "apps",
    "Same as the song": "original",
    "Natural": "natural",
}

# The built-in style each kind of music starts from (it brings the right path)
_BASE_STYLE = {
    "beat": "groove",
    "calm": "smooth",
    "big": "strong",
    "talk": "voice",
    "mixed": "studio",
}
_MOVEMENT = {"gentle": 0.6, "clear": 0.8, "big": 0.95}
_SPEED = {"slow": 12.0, "normal": 8.0, "fast": 5.0, "beat": 8.0}
_ROOM = {"none": 0.0, "little": 0.25, "hall": 0.5}
# Kept short, so a style name built from it stays readable
_MUSIC_WORD = {
    "beat": "Beat",
    "calm": "Calm",
    "big": "Big",
    "talk": "Voice",
    "mixed": "Everyday",
}


@dataclass
class StyleAnswers:  # pylint: disable=too-many-instance-attributes
    """The answers to 'Create your own style', each one a key from its choices."""

    music: str = "mixed"
    movement: str = "clear"
    speed: str = "normal"
    room: str = "little"
    place: str = "headphones"
    file_type: str = "mp3"
    level: str = "apps"


def suggested_answers(music: str) -> StyleAnswers:
    """Good answers for a kind of music, so a beginner can simply press Save."""
    answers = {
        "beat": StyleAnswers("beat", "big", "beat", "little"),
        "calm": StyleAnswers("calm", "gentle", "slow", "little"),
        "big": StyleAnswers("big", "big", "normal", "little"),
        "talk": StyleAnswers("talk", "gentle", "slow", "none"),
    }
    return answers.get(music, StyleAnswers())


def guided_config(answers: StyleAnswers) -> EffectConfig:
    """The exact settings a set of answers stands for (always valid)."""
    base = PRESETS[_BASE_STYLE.get(answers.music, "studio")].config
    file_type = (
        answers.file_type if answers.file_type in FILE_CHOICES.values() else "mp3"
    )
    lossless = file_type == "flac"
    config = dataclasses.replace(
        base,
        intensity=_MOVEMENT.get(answers.movement, 0.8),
        rotation_seconds=_SPEED.get(answers.speed, 8.0),
        beat_sync=answers.speed == "beat",
        bpm=None,
        speed_curve=(),
        intensity_curve=(),
        ambience=_ROOM.get(answers.room, 0.25),
        output_format=file_type,
        # 320 is the best MP3; M4A and FLAC choose their own best
        bitrate=320 if file_type == "mp3" else None,
        quality=0,
        limiter_ceiling=0.89 if lossless else 0.84,
        loudness_target=-14.0 if answers.level == "apps" else None,
        match_loudness=answers.level == "original",
        exact_loudness=False,
        vocals="move",
    )
    if answers.place == "speakers":
        config = speaker_safe(config)
    config.validate()
    return config


def suggested_description(answers: StyleAnswers) -> str:
    """A one-line description built from the answers, e.g. for the Description box."""
    music = {
        "beat": "Music with a strong beat",
        "calm": "Calm music",
        "big": "Big, loud music",
        "talk": "Talking",
    }.get(answers.music, "All kinds of music")
    movement = {"gentle": "gentle", "clear": "clear", "big": "big"}.get(
        answers.movement, "clear"
    )
    speed = {
        "slow": "slow spin",
        "fast": "fast spin",
        "beat": "spins with the beat",
    }.get(answers.speed, "normal spin")
    room = {"none": "no room", "hall": "a big hall"}.get(answers.room, "a little room")
    extras = ", safe for speakers" if answers.place == "speakers" else ""
    return (
        f"{music}: {movement} movement, {speed}, {room}{extras}, "
        f"{answers.file_type.upper()}"
    )


def suggested_name(answers: StyleAnswers, taken: Sequence[str]) -> str:
    """A free name built from the answers: Calm Mix, or Calm Mix 2 if that's taken."""
    stem = _MUSIC_WORD.get(answers.music, "My") + " Mix"
    # Compared the way style names are, so CalmMix and Calm Mix count as the same
    used = {name_key(name) for name in [*taken, *PRESETS]}
    name, number = stem, 2
    while name_key(name) in used:
        name, number = f"{stem} {number}", number + 1
    return name


@dataclass(frozen=True)
class StyleNote:
    """One line of the quality check: its level, what it says, and a fix if any."""

    level: str  # "error" stops saving, "warning" can be fixed, "tip" is a hint
    text: str
    fix: dict[str, object] = field(default_factory=dict)


def style_check(config: EffectConfig, summary: str) -> list[StyleNote]:
    """Everything that would make a saved style weak, most important first."""
    notes: list[StyleNote] = []
    moving = config.intensity > 0 or any(v > 0 for _t, v in config.intensity_curve)
    if not moving:
        notes.append(
            StyleNote(
                "error",
                "This style doesn't move the music at all, so there would be no 8D "
                "effect. Choose some movement.",
                {"intensity": 0.8, "intensity_curve": ()},
            )
        )
    for text, fix in display.advice_items(config):
        # The first sentence says what's weak; "Improve it for me" does the fixing
        notes.append(StyleNote("warning", text.split(". ")[0].rstrip(".") + ".", fix))
    if not summary.strip():
        notes.append(
            StyleNote(
                "tip", "Add a few words to the description so you remember its use."
            )
        )
    return notes


def improved(config: EffectConfig, notes: Sequence[StyleNote]) -> EffectConfig:
    """The settings with every suggested fix applied."""
    changes: dict[str, object] = {}
    for note in notes:
        changes.update(note.fix)
    return dataclasses.replace(config, **changes) if changes else config


def improve_answers(answers: StyleAnswers, notes: Sequence[StyleNote]) -> StyleAnswers:
    """The answers that follow the quality check's advice."""
    better = dataclasses.replace(answers)
    for note in notes:
        if "loudness_target" in note.fix:
            better.level = "apps"
        if "intensity" in note.fix:
            better.movement = "clear"
        if "rotation_seconds" in note.fix:
            better.speed = "normal"
        if "ambience" in note.fix:
            better.room = "little"
    return better


def style_summary(config: EffectConfig) -> str:
    """What a style does, in plain words, one part per line."""
    quality = display.describe_quality(
        config.quality, config.bitrate, config.output_format
    )
    kind = config.output_format.upper()
    loudness = (
        "the same loudness as each song"
        if config.match_loudness
        else display.describe_loudness(config.loudness_target)
    )
    return "\n".join(
        [
            f"Sound: {display.describe_sound(config)}",
            f"Spin: {display.describe_spin(config)}",
            f"Movement: {config.intensity:.2f} "
            f"({display.describe_movement(config.intensity)})",
            f"Room: {config.ambience:.2f} ({display.describe_room(config.ambience)})",
            f"File: {quality}" if kind in quality else f"File: {kind}, {quality}",
            f"Loudness: {loudness}",
        ]
    )


# Below this, an MP3 or AAC file has already lost detail the 8D version can't bring back
LOW_BITRATE = 192_000
# Below this, a recording (a phone or voice memo) has no high notes to move around
LOW_SAMPLE_RATE = 32_000


def source_notes(songs: Sequence[tuple[str, AudioStreamInfo]]) -> list[str]:
    """Heads-ups about the song files themselves, since they decide the best result."""

    def some(names: list[str], one: str, many: str) -> str:
        examples = ", ".join(names[:2]) + (" and others" if len(names) > 2 else "")
        return (one if len(names) == 1 else f"{len(names)} {many}") + f" ({examples})"

    notes = []
    low = [
        name
        for name, info in songs
        if not info.is_lossless and info.bit_rate and info.bit_rate < LOW_BITRATE
    ]
    if low:
        notes.append(
            some(low, "1 song is a low-quality file", "songs are low-quality files")
            + ", under 192 kbps. The 8D version can't sound better than the file you "
            "give it: use a better copy (FLAC, WAV or a 320 kbps MP3) if you have one."
        )
    thin = [
        name
        for name, info in songs
        if info.sample_rate and info.sample_rate < LOW_SAMPLE_RATE
    ]
    if thin:
        notes.append(
            some(
                thin,
                "1 song is a low-detail recording",
                "songs are low-detail recordings",
            )
            + ", like a phone or voice memo. Audio8D raises it so the 3D effect works, "
            "but it can't add the missing high notes."
        )
    return notes
