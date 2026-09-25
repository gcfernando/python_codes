# Developed by Gehan Fernando
"""Checks that every error and typing mistake comes with a plain fix."""

import pytest

from audio8d import ConversionError, DependencyError, EffectConfig, InputValidationError, hints


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (DependencyError("Missing required executable(s): ffmpeg"), "src folder"),
        (DependencyError("Command failed with exit code 1: boom"), "FFmpeg would not run"),
        (InputValidationError("Input file does not exist or cannot be accessed: a.mp3"), "drag"),
        (
            InputValidationError("Command failed with exit code 1: bad data"),
            "doesn't look like music",
        ),
        (InputValidationError("Output already exists: a.mp3"), "--overwrite"),
        (InputValidationError("Output file must use the .mp3 extension"), ".mp3"),
        (ConversionError("Conversion cancelled by user"), "Nothing was left behind"),
        (ConversionError("I/O error during conversion: disk full"), "free space"),
    ],
)
def test_every_common_error_has_a_plain_fix(error: Exception, expected: str) -> None:
    fix = hints.fix_for(error)

    assert fix is not None and expected in fix


@pytest.mark.parametrize(
    "bad",
    [
        EffectConfig(rotation_seconds=1),
        EffectConfig(intensity=2),
        EffectConfig(ambience=-1),
        EffectConfig(limiter_ceiling=2),
        EffectConfig(mp3_quality=12),
        EffectConfig(loudness_target=0),
        EffectConfig(mp3_bitrate=999),
    ],
)
def test_every_out_of_range_knob_points_to_the_best_value(bad: EffectConfig) -> None:
    with pytest.raises(InputValidationError) as error_info:
        bad.validate()

    fix = hints.fix_for(error_info.value)
    assert fix is not None and "(best)" in fix


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("the following arguments are required: input", "you forgot the song"),
        ("argument --quality: invalid choice: '11'", "0 to 9"),
        ("argument --preset: invalid choice: 'x'", "studio"),
        ("argument --bitrate: invalid choice: 999", "320"),
        ("argument --loudness: use a number like -14, or 'off'", "-14"),
        ("unrecognized arguments: Song.mp3", "quotes"),
        ("something new", "--help"),
    ],
)
def test_typing_mistakes_have_a_plain_fix(message: str, expected: str) -> None:
    assert expected in hints.usage_fix_for(message)
