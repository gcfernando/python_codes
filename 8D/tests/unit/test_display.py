# Developed by Gehan Fernando
"""Checks the terminal panel, the best-value markers and the heads-up warnings."""

import io
from pathlib import Path

from audio8d import PRESETS, AudioStreamInfo, EffectConfig, display
from audio8d.ffmpeg import LoudnessMeasurement
from audio8d.pipeline import LoudnessPlan


class _AsciiConsole(io.StringIO):
    """A fake old-style console that can only show plain ASCII."""

    encoding = "ascii"


def test_plain_ascii_consoles_get_a_safe_fallback() -> None:
    stream = _AsciiConsole()
    display.show_presets(display.Painter(stream), "9.9.9")

    shown = stream.getvalue()
    shown.encode("ascii")
    assert "+---" in shown
    assert "\033" not in shown


def test_colour_is_off_when_not_a_terminal() -> None:
    assert display.Painter(io.StringIO()).color is False


def test_settings_are_described_in_plain_words() -> None:
    assert display.describe_movement(0) == "off, stays in the middle"
    assert display.describe_movement(0.85) == "strong"
    assert display.describe_room(0) == "off, completely dry"
    assert display.describe_room(0.3) == "subtle room"
    assert display.describe_quality(0).startswith("V0  (~245 kbps, best")
    assert display.describe_ceiling(0.89) == "0.89  (-1.0 dBFS)"
    assert "Spotify" in display.describe_loudness(-14)
    assert "Apple" in display.describe_loudness(-16)
    assert display.describe_loudness(None).startswith("off")


def test_settings_panel_lists_every_knob() -> None:
    stream = io.StringIO()
    display.show_settings(
        display.Painter(stream),
        version="1.0.0",
        song_in=Path("in.mp3"),
        song_out=Path("out.mp3"),
        preset="studio",
        config=PRESETS["studio"].config,
    )
    shown = stream.getvalue()

    labels = ("Song in", "Song out", "Style", "Spin", "Movement", "Room", "Peak roof", "Quality")
    for label in (*labels, "Loudness"):
        assert label in shown
    assert "Gehan Fernando" in shown


def test_custom_settings_are_labelled_as_such() -> None:
    stream = io.StringIO()
    display.show_settings(
        display.Painter(stream),
        version="1.0.0",
        song_in=Path("in.mp3"),
        song_out=Path("out.mp3"),
        preset=None,
        config=EffectConfig(intensity=0.5),
    )

    assert "your own settings" in stream.getvalue()


def _panel(preset: str | None, config: EffectConfig) -> str:
    """Everything the settings panel prints for these settings, as plain text."""
    stream = io.StringIO()
    display.show_settings(
        display.Painter(stream),
        version="1.0.0",
        song_in=Path("in.mp3"),
        song_out=Path("out.mp3"),
        preset=preset,
        config=config,
    )
    return stream.getvalue()


def test_studio_values_are_all_marked_best() -> None:
    shown = _panel("studio", PRESETS["studio"].config)

    assert shown.count("(best)") == 7
    assert "Heads-up" not in shown


def test_other_values_show_what_the_best_would_be() -> None:
    shown = _panel("classic", EffectConfig())

    assert "best: 0.80" in shown
    assert "best: 0" in shown
    assert "best: -14 LUFS" in shown


def test_risky_values_get_a_heads_up_with_a_fix() -> None:
    notes = display.advice(
        EffectConfig(
            rotation_seconds=3,
            intensity=1.0,
            ambience=0.9,
            limiter_ceiling=1.0,
            mp3_quality=9,
            loudness_target=-6,
        )
    )
    joined = " ".join(notes)

    assert len(notes) == 6
    for words in ("dizzy", "tire your ears", "blurry", "swishy", "crackle", "very loud"):
        assert words in joined


def test_best_settings_need_no_heads_up() -> None:
    assert display.advice(PRESETS["studio"].config) == []


def test_style_menu_puts_the_best_first() -> None:
    stream = io.StringIO()
    names = display.show_style_menu(display.Painter(stream))

    assert names[0] == "studio"
    assert "BEST" in stream.getvalue().splitlines()[0]


_MP3 = AudioStreamInfo("mp3", 2, 48000, 292.4, 320000)
_HI_RES_FLAC = AudioStreamInfo("flac", 2, 96000, 200.0, 2_900_000)


def test_sources_are_described_in_plain_words() -> None:
    assert display.describe_source(_MP3) == "MP3, 320 kbps, 48 kHz, stereo  (already compressed)"
    assert (
        display.describe_source(_HI_RES_FLAC) == "FLAC, 96 kHz, stereo  (lossless, perfect source)"
    )


def test_lossy_sources_get_honest_advice() -> None:
    notes = " ".join(display.source_notes(_MP3, EffectConfig()))

    assert "Already compressed" in notes
    assert "--bitrate 320" in notes


def test_hi_res_sources_are_explained() -> None:
    notes = " ".join(display.source_notes(_HI_RES_FLAC, PRESETS["studio"].config))

    assert "Perfect source" in notes
    assert "96 kHz file is carefully resampled" in notes


def _plan(gain: float, exact: bool) -> LoudnessPlan:
    """A loudness plan for the Annie Lennox song measured during testing."""
    return LoudnessPlan(LoudnessMeasurement(-27.4, -11.5, 8.7), gain, -14.0, exact)


def test_loudness_report_explains_a_held_back_song() -> None:
    stream = io.StringIO()
    display.show_loudness(display.Painter(stream), _plan(9.99, exact=False))
    shown = stream.getvalue()

    assert "measured -27.4 LUFS, turned up 10.0 dB  ->  about -17.4 LUFS" in shown
    assert "not squashed" in shown


def test_loudness_report_for_exact_mode() -> None:
    stream = io.StringIO()
    display.show_loudness(display.Painter(stream), _plan(13.4, exact=True))

    assert "about -14.0 LUFS" in stream.getvalue()
    assert "shaved lightly" in stream.getvalue()


def test_panel_shows_the_source_and_good_to_know_facts() -> None:
    stream = io.StringIO()
    display.show_settings(
        display.Painter(stream),
        version="1.0.0",
        song_in=Path("in.mp3"),
        song_out=Path("out.mp3"),
        preset="studio",
        config=PRESETS["studio"].config,
        source=_MP3,
    )
    shown = stream.getvalue()

    assert "Source" in shown and "already compressed" in shown
    assert "Good to know" in shown
    assert "320 kbps CBR" in shown
