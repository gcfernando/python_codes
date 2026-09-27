# Developed by Gehan Fernando
"""Checks the window's decisions: settings to jobs, validation and plain words."""

import re
from pathlib import Path

import pytest

from src import PRESETS, InputValidationError
from src.cli import _output_for, create_parser, plan_from_args
from src.gui_model import (
    GuiSettings,
    config_for,
    describe,
    describe_curve,
    gui_words,
    items_for,
    options_for,
    problems,
    review,
    warnings,
)

_SONG = [(Path("music/a.mp3"), None)]


def _settings(style: str = "studio") -> GuiSettings:
    """Settings as the window starts: the chosen style applied."""
    settings = GuiSettings()
    settings.apply_style(PRESETS[style])
    return settings


def test_the_window_starts_with_the_best_style() -> None:
    settings = GuiSettings()
    settings.apply_style(PRESETS["studio"])

    assert config_for(settings) == PRESETS["studio"].config
    assert not settings.differs_from(PRESETS["studio"])
    assert not problems(settings, _SONG)


def test_every_style_is_usable_from_the_window() -> None:
    for name in PRESETS:
        assert config_for(_settings(name)) == PRESETS[name].config


def test_typed_curves_bpm_and_loudness_reach_the_config() -> None:
    settings = _settings()
    settings.speed_curve_text = "0=10, 1:00=6"
    settings.intensity_curve_text = "0=0.5, 1:00=0.9"
    settings.bpm_text = "128"
    settings.loudness_is_custom = True
    settings.custom_loudness_text = "-16"
    config = config_for(settings)

    assert config.speed_curve == ((0.0, 10.0), (60.0, 6.0))
    assert config.intensity_curve == ((0.0, 0.5), (60.0, 0.9))
    assert config.bpm == 128
    assert config.loudness_target == -16
    assert settings.differs_from(PRESETS["studio"])


@pytest.mark.parametrize(
    ("field", "text"),
    [
        ("speed_curve_text", "fast"),
        ("intensity_curve_text", "0=2"),
        ("bpm_text", "500"),
        ("bpm_text", "abc"),
    ],
)
def test_bad_typed_values_are_caught_before_converting(field: str, text: str) -> None:
    settings = _settings()
    setattr(settings, field, text)

    with pytest.raises(InputValidationError):
        config_for(settings)
    assert problems(settings, _SONG)


def test_custom_loudness_must_be_in_range() -> None:
    settings = _settings()
    settings.loudness_is_custom = True
    settings.custom_loudness_text = "-40"

    assert any("loudness" in text.lower() for _, text in problems(settings, _SONG))


def test_speakers_switch_uses_the_same_rules_as_the_command_line() -> None:
    settings = _settings("strong")
    settings.speakers = True
    config = config_for(settings)

    assert config.engine == "pan"
    assert config.intensity <= 0.6


def test_output_paths_match_the_command_line() -> None:
    settings = _settings()
    folder = Path("Music")
    songs = [(folder / "Rock" / "b.flac", folder)]
    settings.destination = "Out"

    assert items_for(settings, songs)[0].output == Path("Out/Rock/b (8D).mp3")
    settings.destination = ""
    settings.originals = "replace"
    assert items_for(settings, songs)[0].output == folder / "Rock" / "b.mp3"
    settings.originals = "replace-8d"
    assert items_for(settings, songs)[0].output == folder / "Rock" / "b (8D).mp3"
    assert options_for(settings).replace_original is True


def test_custom_name_only_for_one_song() -> None:
    settings = _settings("lossless")
    settings.name_style = "custom"
    settings.custom_name = "My version.mp3"

    assert items_for(settings, _SONG)[0].output == Path("music/My version.flac")
    two = _SONG + [(Path("music/b.mp3"), None)]
    assert any("one song" in text for _, text in problems(settings, two))
    settings.custom_name = "bad:name"
    assert any("can't contain" in text for _, text in problems(settings, _SONG))


def test_original_name_next_to_the_original_is_refused() -> None:
    settings = _settings()
    settings.name_style = "original"

    assert any("overwrite" in text for _, text in problems(settings, _SONG))
    settings.destination = "Elsewhere"
    assert not problems(settings, _SONG)


def test_trim_and_nothing_to_convert_are_explained() -> None:
    settings = _settings()
    settings.trim_start, settings.trim_end = "2:00", "1:00"

    found = problems(settings, [])
    pages = {page for page, _ in found}
    assert {"songs", "output"} <= pages
    settings.trim_start, settings.trim_end = "1:00", "1:30"
    trim = options_for(settings).trim
    assert trim is not None and (trim.start, trim.end) == (60, 90)


def test_warnings_use_the_windows_words() -> None:
    settings = _settings("whirlwind")
    settings.originals = "replace"
    notes = " ".join(warnings(settings))

    assert "dizzy" in notes
    assert "Recycle Bin" in notes
    assert "--" not in notes


def test_gui_words_replace_command_line_flags() -> None:
    assert gui_words("Try --intensity 0.8") == "Try Movement 0.8 (Sound page)"
    assert "Output page" in gui_words("Add --loudness -14 to fix it.")
    assert "--" not in gui_words("add --overwrite to replace it")


def test_a_curve_out_of_range_names_its_box() -> None:
    settings = GuiSettings(intensity_curve_text="0=0.5, 1:00=1.5")

    found = problems(settings, [(Path("a.mp3"), None)])

    assert found == [("sound", "Movement over time values must be between 0 and 1")]


def test_review_and_status_describe_everything_in_words() -> None:
    settings = _settings()
    labels = [label for label, _ in review(settings)]

    for label in ("Style", "Sound", "Spin", "Bass", "File type", "Loudness",
                  "Save in", "Originals"):  # fmt: skip
        assert label in labels
    assert describe(settings).startswith("3D · circle · 8 s · MP3 · -14 LUFS")
    assert describe_curve("0=10, 1:00=6", " s") == "10 s at 0:00, then 6 s at 1:00"


# README checklist rows: a window change, then the terminal words that must match it
_PARITY = [
    ("spin", lambda s: s.change(rotation_seconds=12.0), ["--rotation-seconds", "12"]),
    ("movement", lambda s: s.change(intensity=0.6), ["--intensity", "0.6"]),
    ("room", lambda s: s.change(ambience=0.1), ["--ambience", "0.1"]),
    ("engine", lambda s: s.change(engine="pan"), ["--engine", "pan"]),
    ("path", lambda s: s.change(path="figure8"), ["--path", "figure8"]),
    (
        "direction",
        lambda s: s.change(direction="counterclockwise"),
        ["--direction", "counterclockwise"],
    ),
    ("bass off", lambda s: s.change(bass_hz=0.0), ["--bass", "off"]),
    ("bass below", lambda s: s.change(bass_hz=200.0), ["--bass", "200"]),
    ("height", lambda s: s.change(elevation=0.5), ["--elevation", "0.5"]),
    ("ease", lambda s: s.change(fade_seconds=0.0), ["--fade", "0"]),
    (
        "speed curve",
        lambda s: setattr(s, "speed_curve_text", "0=10, 1:00=6"),
        ["--speed-curve", "0=10, 1:00=6"],
    ),
    (
        "movement curve",
        lambda s: setattr(s, "intensity_curve_text", "0=0.5, 1:00=0.9"),
        ["--intensity-curve", "0=0.5, 1:00=0.9"],
    ),
    ("beat", lambda s: s.change(beat_sync=True), ["--beat-sync"]),
    (
        "tempo",
        lambda s: (s.change(beat_sync=True), setattr(s, "bpm_text", "128")),
        ["--beat-sync", "--bpm", "128"],
    ),
    ("singer", lambda s: s.change(vocals="center"), ["--vocals", "center"]),
    ("speakers", lambda s: setattr(s, "speakers", True), ["--speakers"]),
    ("file type", lambda s: s.change(output_format="flac"), ["--format", "flac"]),
    ("bitrate", lambda s: s.change(bitrate=192), ["--bitrate", "192"]),
    (
        "mp3 quality",
        lambda s: s.change(bitrate=None, quality=4),
        ["--bitrate", "auto", "--quality", "4"],
    ),
    (
        "apple loudness",
        lambda s: s.change(loudness_target=-16.0),
        ["--loudness", "-16"],
    ),
    (
        "same as original",
        lambda s: s.change(match_loudness=True, loudness_target=None),
        ["--loudness", "match"],
    ),
    ("natural", lambda s: s.change(loudness_target=None), ["--loudness", "off"]),
    (
        "custom loudness",
        lambda s: (
            setattr(s, "loudness_is_custom", True),
            setattr(s, "custom_loudness_text", "-12"),
        ),
        ["--loudness", "-12"],
    ),
    ("exact", lambda s: s.change(exact_loudness=True), ["--exact-loudness"]),
    (
        "peak roof",
        lambda s: s.change(limiter_ceiling=0.9),
        ["--limiter-ceiling", "0.9"],
    ),
    (
        "trim",
        lambda s: (setattr(s, "trim_start", "1:00"), setattr(s, "trim_end", "1:30")),
        ["--start", "1:00", "--end", "1:30"],
    ),
    ("folder", lambda s: setattr(s, "destination", "Out"), ["--output-dir", "Out"]),
    (
        "same name elsewhere",
        lambda s: (
            setattr(s, "destination", "Out"),
            setattr(s, "name_style", "original"),
        ),
        ["--output-dir", "Out", "--name", "original"],
    ),
    ("replace", lambda s: setattr(s, "originals", "replace"), ["--replace"]),
    (
        "replace keep 8d",
        lambda s: setattr(s, "originals", "replace-8d"),
        ["--replace", "--name", "8d"],
    ),
    ("overwrite", lambda s: setattr(s, "overwrite", True), ["--overwrite"]),
    ("no cover", lambda s: setattr(s, "keep_cover", False), ["--no-cover"]),
    ("keep title", lambda s: setattr(s, "tag_title", False), ["--keep-title"]),
    ("no check", lambda s: setattr(s, "check", False), ["--no-check"]),
    ("jobs", lambda s: setattr(s, "jobs", 3), ["--jobs", "3"]),
]


@pytest.mark.parametrize(
    ("window", "words"),
    [row[1:] for row in _PARITY],
    ids=[row[0] for row in _PARITY],
)
def test_every_window_control_matches_its_terminal_option(window, words) -> None:
    settings = _settings()
    settings.recursive = False
    window(settings)
    plan = plan_from_args(
        create_parser().parse_args(["music", "--preset", "studio", *words])
    )
    song = Path("music/Rock/b.flac")

    assert config_for(settings) == plan.config
    assert options_for(settings) == plan.options
    assert items_for(settings, [(song, Path("music"))])[0].output == _output_for(
        song, plan, Path("music")
    )
    assert settings.overwrite == plan.overwrite
    if "--jobs" in words:
        assert settings.jobs == plan.jobs


def test_no_hint_shows_terminal_words_in_the_window() -> None:
    # pylint: disable-next=import-outside-toplevel,protected-access
    from src.hints import _ANYWHERE_FIXES, _FIXES

    for _, fix in _FIXES + _ANYWHERE_FIXES:
        shown = gui_words(fix)
        assert not re.search(r"--[a-z]|audio8d |python -", shown), shown
