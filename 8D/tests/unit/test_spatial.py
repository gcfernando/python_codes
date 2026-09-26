# Developed by Gehan Fernando
"""Checks the exact FFmpeg filter recipe that creates the 8D sound."""

import pytest

from src import EffectConfig, InputValidationError
from src.effects import (
    build_filter_chain,
    build_measure_chain,
    extra_filters_for,
    loudness_gain_db,
    mp3_sample_rate_for,
)

# Golden string for the defaults; any change here changes how every track sounds
DEFAULT_CHAIN = (
    "aformat=sample_fmts=fltp:channel_layouts=stereo,"
    "aecho=in_gain=0.88:out_gain=0.2740:delays=55|110:decays=0.1520|0.0980,"
    "apulsator=mode=sine:amount=0.8500:offset_l=0:offset_r=0.5:width=1:"
    "timing=hz:hz=0.12500000,"
    "alimiter=limit=0.9500:attack=5:release=50:level=false:latency=true"
)


def test_default_chain_is_unchanged() -> None:
    assert build_filter_chain(EffectConfig()) == DEFAULT_CHAIN


def test_stages_run_in_the_right_order() -> None:
    chain = build_filter_chain(EffectConfig())
    names = [stage.split("=", 1)[0] for stage in chain.split(",")]

    assert names == ["aformat", "aecho", "apulsator", "alimiter"]


def test_zero_ambience_removes_echo_stage() -> None:
    chain = build_filter_chain(EffectConfig(ambience=0.0))

    assert "aecho=" not in chain
    assert "apulsator=" in chain
    assert "alimiter=" in chain


def test_rotation_period_is_converted_to_frequency() -> None:
    assert "hz=0.10000000" in build_filter_chain(EffectConfig(rotation_seconds=10.0))


def test_full_ambience_scales_echo_gains() -> None:
    chain = build_filter_chain(EffectConfig(ambience=1.0))

    assert "out_gain=0.4000" in chain
    assert "decays=0.3200|0.2100" in chain


def test_invalid_config_is_rejected_before_building() -> None:
    with pytest.raises(InputValidationError):
        build_filter_chain(EffectConfig(intensity=2.0))


def test_loudness_off_adds_no_extra_stages() -> None:
    assert "volume=" not in build_filter_chain(EffectConfig())
    assert not extra_filters_for(EffectConfig())


def test_volume_stage_sits_between_pan_and_limiter() -> None:
    config = EffectConfig(loudness_target=-14.0, limiter_ceiling=0.84)
    chain = build_filter_chain(config, 44100, gain_db=10.49)
    names = [stage.split("=", 1)[0] for stage in chain.split(",")]

    assert names == ["aformat", "aecho", "apulsator", "volume", "alimiter"]
    assert "volume=10.49dB" in chain
    assert "alimiter=limit=0.8400" in chain
    assert extra_filters_for(config) == ("ebur128", "volume")


def test_exact_mode_leaves_room_for_mp3_overshoot() -> None:
    config = EffectConfig(
        loudness_target=-14.0, limiter_ceiling=0.84, exact_loudness=True
    )

    assert "alimiter=limit=0.7487" in build_filter_chain(config, gain_db=13.0)


def test_measure_chain_is_the_effect_plus_a_meter() -> None:
    chain = build_measure_chain(EffectConfig(loudness_target=-14.0))

    assert chain.startswith("aformat=")
    assert chain.endswith("ebur128=peak=true:framelog=verbose")
    assert "alimiter" not in chain


def test_hi_res_sources_are_resampled_carefully_and_early() -> None:
    chain = build_filter_chain(EffectConfig(), 96000)
    names = [stage.split("=", 1)[0] for stage in chain.split(",")]

    assert names[:2] == ["aformat", "aresample"]
    assert "aresample=48000:filter_size=64" in chain
    assert "aresample" not in build_filter_chain(EffectConfig(), 44100)


def test_pure_gain_never_pushes_peaks_past_the_ceiling() -> None:
    # The song from testing: -27.4 LUFS with a -11.5 dBFS peak, roof at -1.5 dBFS
    gain = loudness_gain_db(-27.4, -11.5, -14.0, 0.84, exact=False)

    assert gain == pytest.approx(9.99, abs=0.01)


def test_pure_gain_reaches_the_target_when_peaks_allow() -> None:
    assert loudness_gain_db(-20.0, -12.0, -14.0, 0.84, exact=False) == pytest.approx(
        6.0
    )


def test_exact_mode_always_reaches_the_target() -> None:
    assert loudness_gain_db(-27.4, -11.5, -14.0, 0.84, exact=True) == pytest.approx(
        13.4
    )


def test_silence_gets_no_gain() -> None:
    assert loudness_gain_db(-70.0, float("-inf"), -14.0, 0.84, exact=False) == 0.0


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (44100, 44100),
        (48000, 48000),
        (22050, 22050),
        (96000, 48000),
        (88200, 44100),
        (192000, 48000),
        (176400, 44100),
        (37800, 44100),
        (None, 44100),
    ],
)
def test_sample_rate_is_kept_when_mp3_allows_it(
    source: int | None, expected: int
) -> None:
    assert mp3_sample_rate_for(source) == expected
