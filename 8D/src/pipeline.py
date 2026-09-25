# Developed by Gehan Fernando
"""The end-to-end conversion: validate, probe, measure, render, publish."""

import logging
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .core.errors import ConversionError
from .core.settings import EffectConfig
from .core.types import AudioStreamInfo
from .effects import build_filter_chain, build_measure_chain, extra_filters_for, loudness_gain_db
from .ffmpeg import (
    FFmpegToolchain,
    LoudnessMeasurement,
    build_encode_command,
    measure_loudness,
    probe_audio,
)
from .files import (
    commit_output,
    create_temporary_output,
    ensure_different_files,
    resolve_input,
    resolve_output,
)

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LoudnessPlan:
    """What the loudness pass measured and the one volume change chosen from it."""

    measured: LoudnessMeasurement
    gain_db: float
    target_lufs: float
    exact: bool

    @property
    def expected_lufs(self) -> float:
        """Where the song lands; a pure volume change moves loudness by exactly the gain."""
        if self.measured.integrated_lufs <= -70.0:
            return self.measured.integrated_lufs
        return self.target_lufs if self.exact else self.measured.integrated_lufs + self.gain_db

    @property
    def held_back(self) -> bool:
        """True when the song stays below target so its loudest peaks never get squashed."""
        return not self.exact and self.expected_lufs < self.target_lufs - 0.05


def _render(command: list[str], temporary_file: Path) -> None:
    """Run the ffmpeg encode and confirm it actually produced audio."""
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        shell=False,
    )

    if result.returncode != 0:
        details = result.stderr.strip() or "FFmpeg returned no additional error information"
        raise ConversionError(
            f"FFmpeg conversion failed with exit code {result.returncode}: {details}"
        )

    if not temporary_file.is_file() or temporary_file.stat().st_size <= 0:
        raise ConversionError("FFmpeg reported success but did not create a valid output file")


def _plan_loudness(
    toolchain: FFmpegToolchain, input_file: Path, config: EffectConfig, source_rate: int | None
) -> LoudnessPlan:
    """Measure the finished 8D mix once, then work out the single exact volume change."""
    assert config.loudness_target is not None
    measured = measure_loudness(toolchain, input_file, build_measure_chain(config, source_rate))
    gain = loudness_gain_db(
        measured.integrated_lufs,
        measured.true_peak_db,
        config.loudness_target,
        config.limiter_ceiling,
        exact=config.exact_loudness,
    )
    return LoudnessPlan(
        measured=measured,
        gain_db=gain,
        target_lufs=config.loudness_target,
        exact=config.exact_loudness,
    )


def convert(
    input_path: Path,
    output_path: Path,
    config: EffectConfig,
    *,
    overwrite: bool = False,
    validate_toolchain: bool = True,
    on_loudness: Callable[[LoudnessPlan], None] | None = None,
) -> AudioStreamInfo:
    """Turn one audio file into an 8D-style stereo MP3 and return source details."""
    config.validate()

    toolchain = FFmpegToolchain.discover()
    if validate_toolchain:
        toolchain.validate_capabilities(extra_filters=extra_filters_for(config))

    input_file = resolve_input(input_path)
    output_file = resolve_output(output_path, overwrite=overwrite)
    ensure_different_files(input_file, output_file)

    source_info = probe_audio(toolchain, input_file)
    temporary_file = create_temporary_output(output_file)

    LOG.info(
        "Converting %s -> %s [codec=%s, channels=%d, sample_rate=%s]",
        input_file,
        output_file,
        source_info.codec_name,
        source_info.channels,
        source_info.sample_rate or "unknown",
    )

    try:
        gain_db = None
        if config.loudness_target is not None:
            plan = _plan_loudness(toolchain, input_file, config, source_info.sample_rate)
            gain_db = plan.gain_db
            LOG.info(
                "Loudness: measured %.1f LUFS / %.1f dBFS peak, applying %+.2f dB",
                plan.measured.integrated_lufs,
                plan.measured.true_peak_db,
                plan.gain_db,
            )
            if on_loudness is not None:
                on_loudness(plan)

        command = build_encode_command(
            toolchain.ffmpeg,
            input_file,
            temporary_file,
            filter_chain=build_filter_chain(config, source_info.sample_rate, gain_db),
            mp3_quality=config.mp3_quality,
            mp3_bitrate=config.mp3_bitrate,
        )
        _render(command, temporary_file)
        commit_output(temporary_file, output_file, overwrite=overwrite)
    except KeyboardInterrupt as exc:
        raise ConversionError("Conversion cancelled by user") from exc
    except OSError as exc:
        raise ConversionError(f"I/O error during conversion: {exc}") from exc
    finally:
        # Always sweep the scratch file; a cleanup hiccup must not mask the real error
        try:
            temporary_file.unlink(missing_ok=True)
        except OSError:
            LOG.warning("Could not remove temporary file: %s", temporary_file)

    LOG.info("Conversion completed: %s", output_file)
    return source_info
