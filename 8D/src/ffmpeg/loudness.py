# Developed by Gehan Fernando
"""Measures loudness with FFmpeg's EBU R128 meter before the real encode."""

import re
from dataclasses import dataclass
from pathlib import Path

from ..core.errors import ConversionError
from .runner import run_capture
from .toolchain import FFmpegToolchain

# FFmpeg prints -inf for silence, so accept that as well as ordinary numbers
_NUMBER = r"(-?inf|-?\d+(?:\.\d+)?)"


@dataclass(frozen=True, slots=True)
class LoudnessMeasurement:
    """How loud the 8D mix is before any volume change."""

    integrated_lufs: float
    true_peak_db: float
    range_lu: float


def parse_ebur128_summary(log: str) -> LoudnessMeasurement:
    """Pull integrated loudness, true peak and loudness range out of FFmpeg's log."""
    start = log.rfind("Summary:")
    if start < 0:
        raise ConversionError("FFmpeg did not report a loudness measurement")
    summary = log[start:]

    def value(label: str, unit: str) -> float:
        """One number from the summary, e.g. the value after 'I:' ending in 'LUFS'."""
        match = re.search(rf"{label}:\s+{_NUMBER}\s+{unit}", summary)
        if match is None:
            raise ConversionError(f"FFmpeg's loudness summary is missing '{label}'")
        return float(match.group(1))

    return LoudnessMeasurement(
        integrated_lufs=value("I", "LUFS"),
        true_peak_db=value("Peak", "dBFS"),
        range_lu=value("LRA", "LU"),
    )


def measure_loudness(
    toolchain: FFmpegToolchain, input_file: Path, measure_chain: str
) -> LoudnessMeasurement:
    """Play the song through the 8D effect silently and measure the result."""
    result = run_capture(
        [
            str(toolchain.ffmpeg),
            "-hide_banner",
            "-nostdin",
            "-nostats",
            # The meter's summary is logged at info level, so -loglevel error hides it
            "-loglevel",
            "info",
            "-i",
            str(input_file),
            "-map",
            "0:a:0",
            "-vn",
            "-af",
            measure_chain,
            "-f",
            "null",
            "-",
        ],
        error_type=ConversionError,
    )
    return parse_ebur128_summary(result.stderr)
