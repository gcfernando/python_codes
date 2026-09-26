# Developed by Gehan Fernando
"""Checks the ready-made styles, the loudness limits and the version number."""

from pathlib import Path

import pytest

import audio8d
from audio8d import PRESETS, RECOMMENDED_PRESET, EffectConfig, InputValidationError


@pytest.mark.parametrize("name", list(PRESETS))
def test_every_preset_is_valid(name: str) -> None:
    PRESETS[name].config.validate()


def test_classic_preset_is_the_default_sound() -> None:
    assert PRESETS["classic"].config == EffectConfig()


def test_studio_preset_is_the_best_of_best() -> None:
    studio = PRESETS[RECOMMENDED_PRESET].config

    assert RECOMMENDED_PRESET == "studio"
    assert studio.mp3_bitrate == 320
    assert studio.loudness_target == -14.0
    assert studio.exact_loudness is False
    # 0.84 is about -1.5 dBFS, the headroom mastering engineers leave for lossy formats
    assert studio.limiter_ceiling == 0.84


def test_streaming_preset_is_studio_with_exact_loudness() -> None:
    studio = PRESETS["studio"].config
    streaming = PRESETS["streaming"].config

    assert streaming.exact_loudness is True
    assert streaming.mp3_bitrate == studio.mp3_bitrate
    assert streaming.limiter_ceiling == studio.limiter_ceiling


@pytest.mark.parametrize("bitrate", [128, 192, 320, None])
def test_standard_bitrates_are_accepted(bitrate: int | None) -> None:
    EffectConfig(mp3_bitrate=bitrate).validate()


@pytest.mark.parametrize("bitrate", [64, 300, 400])
def test_odd_bitrates_are_rejected(bitrate: int) -> None:
    with pytest.raises(InputValidationError):
        EffectConfig(mp3_bitrate=bitrate).validate()


@pytest.mark.parametrize("target", [-30.0, -14.0, -5.0, None])
def test_loudness_target_accepts_sensible_values(target: float | None) -> None:
    EffectConfig(loudness_target=target).validate()


@pytest.mark.parametrize("target", [-31.0, -4.0, 0.0])
def test_loudness_target_rejects_silly_values(target: float) -> None:
    with pytest.raises(InputValidationError):
        EffectConfig(loudness_target=target).validate()


def test_version_matches_pyproject() -> None:
    # tomllib arrived in Python 3.11, so this one check is skipped on 3.10
    tomllib = pytest.importorskip("tomllib")
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
        "version"
    ]

    assert audio8d.__version__ == declared
