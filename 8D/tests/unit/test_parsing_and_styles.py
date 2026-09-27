# Developed by Gehan Fernando
"""Checks times, keyframes, song picking, saved styles and speaker safety."""

from pathlib import Path

import pytest

from src import PRESETS, EffectConfig, InputValidationError
from src.core.parsing import (
    format_keyframes,
    format_time,
    parse_keyframes,
    parse_selection,
    parse_time,
)
from src.core.settings import speaker_safe
from src.core.user_presets import (
    all_presets,
    delete_user_preset,
    dump_toml,
    load_user_presets,
    parse_toml,
    save_user_preset,
)


@pytest.mark.parametrize(
    ("text", "seconds"),
    [("90", 90.0), ("1:30", 90.0), ("1:02:03", 3723.0), ("0:05.5", 5.5)],
)
def test_times_are_read_like_a_music_player(text: str, seconds: float) -> None:
    assert parse_time(text) == seconds


@pytest.mark.parametrize("text", ["", "abc", "1:75", "-5", "1:2:3:4"])
def test_bad_times_are_refused(text: str) -> None:
    with pytest.raises(InputValidationError):
        parse_time(text)


def test_times_are_shown_like_a_music_player() -> None:
    assert format_time(90) == "1:30"
    assert format_time(3723) == "1:02:03"


def test_keyframes_round_trip() -> None:
    frames = parse_keyframes("0=10, 1:00=6; 2:30=10")

    assert frames == ((0.0, 10.0), (60.0, 6.0), (150.0, 10.0))
    assert parse_keyframes(format_keyframes(frames)) == frames


@pytest.mark.parametrize("text", ["fast", "1:00", "0=abc", " , "])
def test_bad_keyframes_are_refused(text: str) -> None:
    with pytest.raises(InputValidationError):
        parse_keyframes(text)


def test_keyframes_must_go_forwards_and_stay_in_range() -> None:
    with pytest.raises(InputValidationError):
        EffectConfig(speed_curve=((60.0, 8.0), (0.0, 8.0))).validate()
    with pytest.raises(InputValidationError):
        EffectConfig(intensity_curve=((0.0, 1.5),)).validate()


def test_song_selection() -> None:
    assert parse_selection("", 4) == [0, 1, 2, 3]
    assert parse_selection("all", 4) == [0, 1, 2, 3]
    assert parse_selection("1,3-4", 4) == [0, 2, 3]
    assert parse_selection("2 2 1", 4) == [0, 1]
    for bad in ("0", "5", "2-1", "x"):
        with pytest.raises(InputValidationError):
            parse_selection(bad, 4)


def test_toml_subset_round_trips() -> None:
    tables = {"mine": {"based_on": "studio", "intensity": 0.9, "beat_sync": True}}
    text = dump_toml(tables)

    assert parse_toml(text) == tables
    assert parse_toml('[a]\nsummary = "has # inside" # comment\n') == {
        "a": {"summary": "has # inside"}
    }
    with pytest.raises(InputValidationError):
        parse_toml("key = 1\n")


def test_saved_style_only_stores_differences(tmp_path: Path) -> None:
    file = tmp_path / "presets.toml"
    config = PRESETS["studio"].config.__class__(
        **{
            **{
                name: getattr(PRESETS["studio"].config, name)
                for name in PRESETS["studio"].config.__dataclass_fields__
            },
            "intensity": 0.95,
            "speed_curve": ((0.0, 10.0), (60.0, 6.0)),
            "loudness_target": None,
        }
    )
    save_user_preset("party", config, based_on="studio", summary="loud", path=file)
    text = file.read_text(encoding="utf-8")

    assert "intensity = 0.95" in text
    assert 'loudness_target = "off"' in text
    assert "bitrate" not in text
    loaded = load_user_presets(file)["party"]
    assert loaded.config == config
    assert loaded.custom and loaded.summary == "loud"


def test_saved_styles_join_the_built_in_ones() -> None:
    save_user_preset("chill_2", EffectConfig(ambience=0.5))
    presets = all_presets()

    assert list(presets)[: len(PRESETS)] == list(PRESETS)
    assert presets["chill_2"].config.ambience == 0.5


@pytest.mark.parametrize("name", ["studio", "Has Space", "x" * 30])
def test_bad_style_names_are_refused(name: str, tmp_path: Path) -> None:
    with pytest.raises(InputValidationError):
        save_user_preset(name, EffectConfig(), path=tmp_path / "p.toml")


def test_broken_style_file_is_explained(tmp_path: Path) -> None:
    file = tmp_path / "presets.toml"
    file.write_text('[mine]\nbased_on = "nope"\n', encoding="utf-8")
    with pytest.raises(InputValidationError, match="does not exist"):
        load_user_presets(file)
    file.write_text("[mine]\nwobble = 3\n", encoding="utf-8")
    with pytest.raises(InputValidationError, match="unknown setting"):
        load_user_presets(file)


def test_speaker_safe_softens_any_style() -> None:
    safe = speaker_safe(
        EffectConfig(
            intensity=0.95, elevation=0.8, bass_hz=0, intensity_curve=((0, 1.0),)
        )
    )

    assert safe.engine == "pan"
    assert safe.intensity == 0.6
    assert safe.intensity_curve == ((0, 0.6),)
    assert safe.elevation == 0.0
    assert safe.bass_hz == 120.0


def test_every_built_in_style_is_valid() -> None:
    for preset in PRESETS.values():
        preset.config.validate()
    assert PRESETS["lossless"].config.output_format == "flac"
    assert PRESETS["groove"].config.beat_sync is True
    assert PRESETS["retro"].config.engine == "pan"


def test_saving_styles_never_leaves_a_half_written_file(tmp_path: Path) -> None:
    file = tmp_path / "presets.toml"
    save_user_preset("first", PRESETS["studio"].config, based_on="studio", path=file)
    save_user_preset("second", PRESETS["groove"].config, based_on="groove", path=file)
    delete_user_preset("first", path=file)

    assert list(tmp_path.iterdir()) == [file]
    assert list(load_user_presets(file)) == ["second"]
