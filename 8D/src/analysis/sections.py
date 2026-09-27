# Developed by ::> Gehan Fernando
"""Finds the loudest stretch of a song: usually the chorus, the best preview."""

import re
from pathlib import Path

from ..core.errors import ConversionError
from ..ffmpeg import FFmpegToolchain, ffmpeg_prefix, run_capture

# ebur128 logs a line every 100 ms: "t: 12.3  TARGET:-23 LUFS  M: -14.2 S: -15.0 ..."
_LINE = re.compile(r"t:\s*([\d.]+).*?\bS:\s*(-?[\d.]+|-inf)")


def short_term_loudness(log: str) -> list[tuple[float, float]]:
    """(time, short-term LUFS) pairs from an ebur128 log with framelog=info."""
    points = []
    for match in _LINE.finditer(log):
        value = match.group(2)
        points.append(
            (float(match.group(1)), -120.0 if value == "-inf" else float(value))
        )
    return points


def loudest_start(points: list[tuple[float, float]], length: float) -> float:
    """Where a window of `length` seconds has the most energy."""
    if not points:
        return 0.0
    powers = [(time, 10 ** (lufs / 10)) for time, lufs in points]
    best_time, best_total = 0.0, -1.0
    total = 0.0
    first = 0
    for index, (time, power) in enumerate(powers):
        total += power
        while powers[first][0] < time - length:
            total -= powers[first][1]
            first += 1
        if index and total > best_total:
            best_total = total
            best_time = powers[first][0]
    # The short-term meter looks 3 s back, so start the preview a little earlier
    return max(0.0, best_time - 3.0)


def find_loudest_section(
    toolchain: FFmpegToolchain, song: Path, length: float, duration: float | None
) -> float:
    """Start time (seconds) of the loudest `length`-second stretch of the song."""
    if duration is not None and duration <= length:
        return 0.0
    result = run_capture(
        [
            *ffmpeg_prefix(toolchain.ffmpeg, log="info"),
            "-i",
            str(song),
            "-map",
            "0:a:0",
            "-af",
            "aresample=22050,ebur128=framelog=info",
            "-f",
            "null",
            "-",
        ],
        error_type=ConversionError,
    )
    start = loudest_start(short_term_loudness(result.stderr), length)
    if duration is not None:
        start = min(start, max(0.0, duration - length))
    return start
