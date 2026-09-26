# Developed by Gehan Fernando
"""Friendly, colourful terminal output for the `audio8d` command."""

import ctypes
import math
import os
from pathlib import Path
from typing import TextIO

from .core.presets import PRESETS, RECOMMENDED_PRESET
from .core.settings import EffectConfig
from .core.types import AudioStreamInfo
from .pipeline import LoudnessPlan

# Average bitrate LAME usually lands on for each --quality value from 0 to 9
_VBR_KBPS = (245, 225, 190, 175, 165, 130, 115, 100, 85, 65)

# The studio preset is what every "best:" hint in the panel points to
BEST = PRESETS[RECOMMENDED_PRESET].config

# ANSI colour codes; 38;5;141 is a soft violet from the 256-colour palette
_ANSI = {
    "bold": "1",
    "dim": "2",
    "cyan": "96",
    "pink": "95",
    "green": "92",
    "yellow": "93",
    "red": "91",
    "violet": "38;5;141",
}


def _enable_windows_ansi(stream: TextIO) -> bool:
    """Switch on colour codes in the classic Windows console; harmless elsewhere."""
    if os.name != "nt":
        return True
    try:
        # msvcrt only exists on Windows, so it is imported once we know we are there
        import msvcrt  # pylint: disable=import-outside-toplevel

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = msvcrt.get_osfhandle(stream.fileno())
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        # 0x0004 is ENABLE_VIRTUAL_TERMINAL_PROCESSING, which turns colour codes on
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError, ValueError):
        return False


class Painter:
    """Writes to one stream, adding colour and box lines only where they will render."""

    def __init__(self, stream: TextIO) -> None:
        """Decide once whether this stream can show colours and box lines."""
        self.stream = stream
        is_terminal = hasattr(stream, "isatty") and stream.isatty()
        # Respect NO_COLOR, the common way people ask tools for plain text
        self.color = (
            is_terminal
            and "NO_COLOR" not in os.environ
            and _enable_windows_ansi(stream)
        )
        self.fancy = self._can_encode("╭─╮│╰╯·")

    def _can_encode(self, sample: str) -> bool:
        """True when the stream's encoding can show these characters."""
        try:
            sample.encode(getattr(self.stream, "encoding", None) or "ascii")
        except (UnicodeEncodeError, LookupError):
            return False
        return True

    def paint(self, text: str, *styles: str) -> str:
        """Wrap text in colour codes when colour is on."""
        if not self.color or not styles:
            return text
        codes = ";".join(_ANSI[style] for style in styles)
        return f"\033[{codes}m{text}\033[0m"

    def line(self, text: str = "") -> None:
        """Print one line and flush so it appears before FFmpeg starts working."""
        print(text, file=self.stream, flush=True)

    def rule(self, width: int = 52) -> None:
        """A thin divider line."""
        self.line(self.paint("  " + ("─" if self.fancy else "-") * width, "dim"))


def describe_movement(intensity: float) -> str:
    """Plain-word label for --intensity."""
    if intensity == 0:
        return "off, stays in the middle"
    if intensity < 0.5:
        return "gentle"
    if intensity < 0.8:
        return "medium"
    if intensity < 0.95:
        return "strong"
    return "maximum"


def describe_room(ambience: float) -> str:
    """Plain-word label for --ambience."""
    if ambience == 0:
        return "off, completely dry"
    if ambience <= 0.35:
        return "subtle room"
    if ambience <= 0.6:
        return "large room"
    return "huge hall"


def describe_quality(quality: int, bitrate: int | None = None) -> str:
    """Plain-word label for --quality, or for --bitrate when one is set."""
    if bitrate:
        kind = "the maximum MP3 allows" if bitrate == 320 else "constant"
        return f"{bitrate} kbps CBR  ({kind})"
    if quality <= 1:
        verdict = "best"
    elif quality <= 3:
        verdict = "excellent"
    elif quality <= 6:
        verdict = "good"
    else:
        verdict = "small file"
    return f"V{quality}  (~{_VBR_KBPS[quality]} kbps, {verdict})"


def describe_ceiling(ceiling: float) -> str:
    """Limiter ceiling as both the raw value and dBFS."""
    return f"{ceiling:.2f}  ({20 * math.log10(ceiling):+.1f} dBFS)"


def describe_loudness(target: float | None) -> str:
    """Loudness target in words."""
    if target is None:
        return "off  (natural level, usually quieter than the original)"
    if round(target) == -14:
        return f"{target:g} LUFS  (Spotify / YouTube / Tidal standard)"
    if round(target) == -16:
        return f"{target:g} LUFS  (Apple Music standard)"
    return f"{target:g} LUFS"


def advice(config: EffectConfig) -> list[str]:
    """Plain-word warnings for settings that may not sound their best, with fixes."""
    notes = []
    if config.rotation_seconds < 5:
        notes.append(
            "A spin this fast can make people dizzy. Most people like 6 to 10 s."
        )
    elif config.rotation_seconds > 20:
        notes.append("A spin this slow is hard to notice. Most people like 6 to 10 s.")
    if 0 < config.intensity < 0.5:
        notes.append(
            "The movement is gentle and may be hard to hear. Try --intensity 0.8"
        )
    elif config.intensity > 0.95:
        notes.append(
            "One ear goes almost silent at times, which can tire your ears. Try 0.8"
        )
    if config.ambience > 0.6:
        notes.append("This much room sound can make voices blurry. Try --ambience 0.25")
    if config.mp3_bitrate is None and config.mp3_quality >= 6:
        notes.append("Lower quality: you may hear swishy sounds. Best is --bitrate 320")
    elif config.mp3_bitrate is not None and config.mp3_bitrate < 192:
        notes.append("Low bitrate: you may hear swishy sounds. Best is --bitrate 320")
    if config.limiter_ceiling > 0.95:
        best_roof = BEST.limiter_ceiling
        notes.append(f"Peaks this high may crackle on some phones. Best is {best_roof}")
    elif config.limiter_ceiling < 0.5:
        notes.append(
            "A peak roof this low makes the song very quiet. "
            f"Best is {BEST.limiter_ceiling}"
        )
    if config.loudness_target is None:
        notes.append(
            "Your 8D song will be quieter than normal music. "
            "Add --loudness -14 to fix it."
        )
    elif config.loudness_target > -9:
        notes.append(
            "That is very loud; music apps will turn it down anyway. Best is -14"
        )
    elif config.loudness_target < -20:
        notes.append(
            "Quieter than music apps (-23 is for TV and radio). Best for music is -14"
        )
    return notes


def describe_source(info: AudioStreamInfo) -> str:
    """What the file is, e.g. 'MP3, 320 kbps, 48 kHz, stereo (already compressed)'."""
    parts = [info.codec_name.upper().replace("PCM_", "WAV/PCM ")]
    if info.bit_rate and not info.is_lossless:
        parts.append(f"{round(info.bit_rate / 1000)} kbps")
    if info.sample_rate:
        parts.append(f"{info.sample_rate / 1000:g} kHz")
    parts.append(
        {1: "mono", 2: "stereo"}.get(info.channels, f"{info.channels} channels")
    )
    kind = "lossless, perfect source" if info.is_lossless else "already compressed"
    return ", ".join(parts) + f"  ({kind})"


def source_notes(info: AudioStreamInfo, config: EffectConfig) -> list[str]:
    """Plain-word facts about this particular file and how Audio8D treats it."""
    notes = []
    if info.is_lossless:
        notes.append(
            "Perfect source: the MP3 encode is the only step that loses anything."
        )
    else:
        notes.append("Already compressed, so a little detail is gone for good.")
        notes.append(
            "320 kbps keeps any extra loss tiny; a FLAC or WAV copy would sound best."
        )
        if config.mp3_bitrate != 320:
            notes.append(
                "For this kind of file, --bitrate 320 (or --preset studio) "
                "matters most."
            )
    if info.sample_rate and info.sample_rate > 48000:
        notes.append(
            f"MP3 stores at most 48 kHz, so this {info.sample_rate / 1000:g} kHz "
            "file is carefully resampled."
        )
    if info.channels == 1:
        notes.append(
            "Mono file: it is copied to both ears first, then the 8D movement starts."
        )
    elif info.channels > 2:
        notes.append("Surround file: it is folded down to left and right first.")
    return notes


def _banner(painter: Painter, version: str) -> None:
    """The title box at the top of every screen."""
    title = f"  Audio8D {version}  ·  developed by Gehan Fernando  "
    corners = (
        ("╭", "─", "╮", "│", "╰", "╯")
        if painter.fancy
        else ("+", "-", "+", "|", "+", "+")
    )
    if not painter.fancy:
        title = title.replace("·", "-")
    top_left, across, top_right, side, bottom_left, bottom_right = corners
    painter.line(painter.paint(top_left + across * len(title) + top_right, "violet"))
    painter.line(
        painter.paint(side, "violet")
        + painter.paint(title, "bold", "cyan")
        + painter.paint(side, "violet")
    )
    painter.line(
        painter.paint(bottom_left + across * len(title) + bottom_right, "violet")
    )


def _loudness_setting(config: EffectConfig) -> str:
    """The loudness row of the settings panel, e.g. '-14 LUFS goal, dynamics kept'."""
    if config.loudness_target is None:
        return "off"
    how = (
        "exactly, light peak limiting"
        if config.exact_loudness
        else "goal, dynamics kept"
    )
    return f"{config.loudness_target:g} LUFS {how}"


def _best_note(painter: Painter, is_best: bool, best_text: str) -> str:
    """Green '(best)' for the recommended value, otherwise a hint naming the best."""
    if is_best:
        return painter.paint("  (best)", "green")
    return painter.paint(f"  best: {best_text}", "dim")


def show_settings(
    painter: Painter,
    *,
    version: str,
    song_in: Path,
    song_out: Path,
    preset: str | None,
    config: EffectConfig,
    banner: bool = True,
    source: AudioStreamInfo | None = None,
) -> None:
    """Print the banner and every setting in plain words, marking the best values."""
    # The guided mode has already shown the title box, so it can ask us to skip it
    if banner:
        _banner(painter, version)

    def row(label: str, value: str, note: str = "", color: str = "cyan") -> None:
        """One neat line: grey label, coloured value, then the best-value note."""
        label_text = painter.paint(f"{label:<11}", "dim")
        painter.line(
            f"  {label_text}{painter.paint(f'{value:<44}', color)}{note}".rstrip()
        )

    row("Song in", str(song_in), color="bold")
    row("Song out", str(song_out), color="bold")
    if source is not None:
        row("Source", describe_source(source), color="bold")
    if preset:
        style = f"{preset}  -  {PRESETS[preset].summary}"
        row(
            "Style",
            style,
            _best_note(painter, preset == RECOMMENDED_PRESET, RECOMMENDED_PRESET),
            "pink",
        )
    else:
        row("Style", "your own settings", color="pink")
    painter.rule()
    row(
        "Spin",
        f"{config.rotation_seconds:g} s per full circle",
        _best_note(painter, config.rotation_seconds == BEST.rotation_seconds, "8 s"),
    )
    row(
        "Movement",
        f"{config.intensity:.2f}  ({describe_movement(config.intensity)})",
        _best_note(
            painter, config.intensity == BEST.intensity, f"{BEST.intensity:.2f}"
        ),
    )
    row(
        "Room",
        f"{config.ambience:.2f}  ({describe_room(config.ambience)})",
        _best_note(painter, config.ambience == BEST.ambience, f"{BEST.ambience:.2f}"),
    )
    row(
        "Peak roof",
        describe_ceiling(config.limiter_ceiling),
        _best_note(
            painter,
            config.limiter_ceiling == BEST.limiter_ceiling,
            f"{BEST.limiter_ceiling:.2f}",
        ),
    )
    row(
        "Quality",
        describe_quality(config.mp3_quality, config.mp3_bitrate),
        _best_note(
            painter, config.mp3_bitrate == BEST.mp3_bitrate, f"{BEST.mp3_bitrate} kbps"
        ),
    )
    row(
        "Loudness",
        _loudness_setting(config),
        _best_note(
            painter,
            config.loudness_target == BEST.loudness_target
            and config.exact_loudness == BEST.exact_loudness,
            "-14 LUFS goal",
        ),
    )

    facts = source_notes(source, config) if source is not None else []
    if facts:
        painter.line()
        painter.line("  " + painter.paint("Good to know:", "bold", "cyan"))
        for fact in facts:
            painter.line("   " + painter.paint("- " + fact, "cyan"))

    notes = advice(config)
    if notes:
        painter.line()
        painter.line("  " + painter.paint("Heads-up:", "bold", "yellow"))
        for note in notes:
            painter.line("   " + painter.paint("- " + note, "yellow"))

    painter.line()
    if config.loudness_target is None:
        painter.line(
            painter.paint("  Working... this usually takes a few seconds.", "yellow")
        )
    else:
        painter.line(
            painter.paint(
                "  Working... measuring the loudness first, then making your song.",
                "yellow",
            )
        )


def show_done(painter: Painter, song_out: Path, seconds: float) -> None:
    """Celebrate a finished conversion with the time taken and the file size."""
    try:
        size = f"{song_out.stat().st_size / 1_048_576:.1f} MB"
    except OSError:
        size = "size unknown"
    painter.line(
        "  "
        + painter.paint(f"Conversion completed in {seconds:.1f} s", "bold", "green")
        + painter.paint(f"  ->  {song_out}  ({size})", "green")
    )
    painter.line(painter.paint("  Put on your headphones and press play!", "green"))


def show_loudness(painter: Painter, plan: LoudnessPlan) -> None:
    """Explain the loudness pass: what was measured, what changed, where it landed."""
    measured = plan.measured
    direction = "up" if plan.gain_db >= 0 else "down"
    painter.line(
        "  "
        + painter.paint("Loudness:", "bold", "green")
        + painter.paint(
            f" measured {measured.integrated_lufs:.1f} LUFS, turned {direction}"
            f" {abs(plan.gain_db):.1f} dB  ->  about {plan.expected_lufs:.1f} LUFS",
            "green",
        )
    )
    if plan.held_back:
        painter.line(
            painter.paint(
                f"  Kept below {plan.target_lufs:g} so the loudest moments are not "
                "squashed. (--exact-loudness would force it.)",
                "dim",
            )
        )
    elif plan.exact:
        painter.line(
            painter.paint("  The loudest peaks were shaved lightly to reach it.", "dim")
        )


def show_tip(painter: Painter) -> None:
    """Nudge first-time users towards the best-sounding preset."""
    painter.line()
    painter.line(
        "  "
        + painter.paint("Tip:", "bold", "yellow")
        + " for world-standard quality add "
        + painter.paint(f"--preset {RECOMMENDED_PRESET}", "bold", "pink")
        + painter.paint("   (see every style: --list-presets)", "dim")
    )


def show_fix(painter: Painter, fix: str) -> None:
    """Tell the user, in plain words, how to solve the error they just hit."""
    painter.line("  " + painter.paint("What to do:", "bold", "yellow") + " " + fix)


def show_presets(painter: Painter, version: str) -> None:
    """Print every preset with its exact values, recommended one first."""
    _banner(painter, version)
    painter.line(
        painter.paint(
            "  Sound styles - use one with:  audio8d song.mp3 --preset NAME", "bold"
        )
    )
    painter.line()
    header = (
        f"  {'NAME':<12}{'SPIN':>6}{'MOVE':>7}{'ROOM':>7}{'ROOF':>7}  "
        f"{'QUALITY':<9}{'LOUDNESS':<11}WHAT IT IS FOR"
    )
    painter.line(painter.paint(header, "dim"))
    for name, preset in PRESETS.items():
        cfg = preset.config
        label = f"{name} *" if name == RECOMMENDED_PRESET else name
        quality = f"{cfg.mp3_bitrate}k" if cfg.mp3_bitrate else f"V{cfg.mp3_quality}"
        if cfg.loudness_target is None:
            loud = "off"
        else:
            loud = f"{cfg.loudness_target:g} " + (
                "exact" if cfg.exact_loudness else "LUFS"
            )
        numbers = (
            f"{cfg.rotation_seconds:>5g}s{cfg.intensity:>7.2f}{cfg.ambience:>7.2f}"
            f"{cfg.limiter_ceiling:>7.2f}  {quality:<9}{loud:<11}"
        )
        color = "pink" if name == RECOMMENDED_PRESET else "cyan"
        painter.line(
            f"  {painter.paint(f'{label:<12}', 'bold', color)}{numbers}{preset.summary}"
        )
    painter.line()
    painter.line(
        painter.paint(
            "  * recommended. Any knob you add (e.g. --intensity 0.9) "
            "overrides the style.",
            "dim",
        )
    )


def show_welcome(painter: Painter, version: str) -> None:
    """First screen of the guided mode."""
    _banner(painter, version)
    painter.line(
        "  "
        + painter.paint("Welcome! Let's make your song fly around your head.", "bold")
    )
    painter.line("  Just answer 2 quick questions. You can't break anything.")
    painter.line()


def show_step(painter: Painter, number: int, title: str, hint: str) -> None:
    """Heading for one step of the guided mode."""
    painter.line("  " + painter.paint(f"Step {number} of 2 - {title}", "bold", "cyan"))
    painter.line("  " + painter.paint(hint, "dim"))


def show_style_menu(painter: Painter) -> list[str]:
    """Numbered list of styles, best first; returns the names in menu order."""
    names = list(PRESETS)
    for number, name in enumerate(names, start=1):
        badge = (
            painter.paint("  BEST ", "bold", "green")
            if name == RECOMMENDED_PRESET
            else "       "
        )
        label = painter.paint(
            f"{name:<10}", "bold", "pink" if name == RECOMMENDED_PRESET else "cyan"
        )
        number_text = painter.paint(str(number), "bold")
        painter.line(f"   {number_text}  {label}{badge}{PRESETS[name].summary}")
    return names


def show_problem(painter: Painter, text: str) -> None:
    """A gentle, non-scary message when an answer can't be used."""
    painter.line("  " + painter.paint(text, "yellow"))
