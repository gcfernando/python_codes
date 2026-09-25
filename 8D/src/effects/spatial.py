# Developed by Gehan Fernando
"""Builds the FFmpeg audio filter graph that creates the 8D movement."""

import math

from ..core.settings import EffectConfig

# Two early reflections at 55 ms and 110 ms give depth without smearing vocals
_ECHO_DELAYS_MS = "55|110"

# The only sample rates the MP3 format can store
MP3_SAMPLE_RATES = frozenset({8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000})

# ebur128 reports pure silence as -70 LUFS, so anything at or below it gets no gain
_SILENCE_LUFS = -70.0

# Extra room below the ceiling in exact-loudness mode, because MP3 decoding overshoots limited peaks
_EXACT_MODE_MARGIN_DB = 1.0


def mp3_sample_rate_for(source_rate: int | None) -> int:
    """Keep the source sample rate when MP3 can store it, otherwise pick the closest family."""
    if source_rate in MP3_SAMPLE_RATES:
        return source_rate
    # 88.2 and 176.4 kHz divide cleanly into 44.1 kHz; other hi-res rates land on 48 kHz
    if source_rate is not None and source_rate > 48000:
        return 44100 if source_rate % 44100 == 0 else 48000
    return 44100


def loudness_gain_db(
    measured_lufs: float,
    measured_peak_db: float,
    target_lufs: float,
    ceiling: float,
    *,
    exact: bool,
) -> float:
    """The one volume change that brings the 8D mix to its loudness target."""
    if measured_lufs <= _SILENCE_LUFS:
        return 0.0
    gain = target_lufs - measured_lufs
    if exact:
        return gain
    # Never lift the loudest moment past the ceiling, so the limiter never has to squash anything
    return min(gain, 20.0 * math.log10(ceiling) - measured_peak_db)


def _format_stage() -> str:
    """Force float stereo so mono and multichannel sources all pan the same way."""
    return "aformat=sample_fmts=fltp:channel_layouts=stereo"


def _resample_stage(source_rate: int | None) -> list[str]:
    """High-quality resampling, only for rates MP3 cannot store (e.g. 96 kHz)."""
    if source_rate is None or source_rate in MP3_SAMPLE_RATES:
        return []
    # A longer filter than FFmpeg's automatic one keeps the top octave clean
    return [f"aresample={mp3_sample_rate_for(source_rate)}:filter_size=64"]


def _ambience_stage(ambience: float) -> str:
    """Short room-style reflections that scale gently with the ambience setting."""
    # Kept deliberately modest because heavy echo quickly turns a mix to mud
    output_gain = 0.22 + (0.18 * ambience)
    first_decay = 0.08 + (0.24 * ambience)
    second_decay = 0.05 + (0.16 * ambience)

    return (
        "aecho="
        "in_gain=0.88:"
        f"out_gain={output_gain:.4f}:"
        f"delays={_ECHO_DELAYS_MS}:"
        f"decays={first_decay:.4f}|{second_decay:.4f}"
    )


def _panning_stage(intensity: float, rotation_seconds: float) -> str:
    """Sine auto-pan with the right channel half a cycle behind the left."""
    # apulsator wants a frequency, so one full L -> R -> L trip becomes 1 / period
    rotation_hz = 1.0 / rotation_seconds

    return (
        "apulsator="
        "mode=sine:"
        f"amount={intensity:.4f}:"
        "offset_l=0:"
        "offset_r=0.5:"
        "width=1:"
        "timing=hz:"
        f"hz={rotation_hz:.8f}"
    )


def _limiter_stage(ceiling: float) -> str:
    """Brick-wall limiter so panning and echo peaks never clip the encoder."""
    return f"alimiter=limit={ceiling:.4f}:attack=5:release=50:level=false:latency=true"


def _effect_stages(config: EffectConfig, source_rate: int | None) -> list[str]:
    """Everything that creates the 8D sound, before any volume change."""
    stages = [_format_stage(), *_resample_stage(source_rate)]

    # Zero ambience means a completely dry signal, so skip the echo entirely
    if config.ambience > 0.0:
        stages.append(_ambience_stage(config.ambience))

    stages.append(_panning_stage(config.intensity, config.rotation_seconds))
    return stages


def extra_filters_for(config: EffectConfig) -> tuple[str, ...]:
    """FFmpeg filters needed on top of the always-required set for this config."""
    return ("ebur128", "volume") if config.loudness_target is not None else ()


def build_measure_chain(config: EffectConfig, source_rate: int | None = None) -> str:
    """The 8D effect followed by an EBU R128 meter, used to measure before the real encode."""
    config.validate()
    # framelog=verbose keeps the per-frame lines quiet so only the final summary is printed
    return ",".join([*_effect_stages(config, source_rate), "ebur128=peak=true:framelog=verbose"])


def build_filter_chain(
    config: EffectConfig, source_rate: int | None = None, gain_db: float | None = None
) -> str:
    """Return the comma-separated -af graph for one conversion."""
    config.validate()

    stages = _effect_stages(config, source_rate)
    ceiling = config.limiter_ceiling

    # One exact volume change, measured beforehand, reaches the loudness target
    if gain_db is not None:
        stages.append(f"volume={gain_db:.2f}dB")
        if config.exact_loudness:
            ceiling = max(0.0625, ceiling * 10 ** (-_EXACT_MODE_MARGIN_DB / 20))

    # The limiter goes last so it guards exactly what reaches the MP3 encoder
    stages.append(_limiter_stage(ceiling))

    return ",".join(stages)
