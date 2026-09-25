# Developed by Gehan Fernando
"""Reads source-stream metadata through FFprobe's JSON output."""

import json
from pathlib import Path
from typing import Any

from ..core.errors import InputValidationError
from ..core.types import AudioStreamInfo
from .runner import run_capture
from .toolchain import FFmpegToolchain


def parse_probe_output(raw_json: str) -> AudioStreamInfo:
    """Turn FFprobe JSON into an AudioStreamInfo or reject unusable input."""
    try:
        payload: dict[str, Any] = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise InputValidationError("FFprobe returned malformed JSON") from exc

    streams = payload.get("streams") or []
    if not streams:
        raise InputValidationError("The input file does not contain a usable audio stream")

    stream = streams[0]

    try:
        channels = int(stream["channels"])

        sample_rate_value = stream.get("sample_rate")
        sample_rate = int(sample_rate_value) if sample_rate_value else None

        # Raw streams and some live captures report "N/A" instead of a length
        duration_value = (payload.get("format") or {}).get("duration")
        duration = float(duration_value) if duration_value not in (None, "N/A") else None

        codec_name = str(stream.get("codec_name") or "unknown")

        # Some containers only store the bitrate for the whole file, so fall back to that
        bit_rate_value = stream.get("bit_rate") or (payload.get("format") or {}).get("bit_rate")
        bit_rate = int(bit_rate_value) if bit_rate_value not in (None, "", "N/A") else None
    except (KeyError, TypeError, ValueError) as exc:
        raise InputValidationError("FFprobe returned incomplete or invalid audio metadata") from exc

    if channels < 1:
        raise InputValidationError("The input audio reports an invalid channel count")

    return AudioStreamInfo(
        codec_name=codec_name,
        channels=channels,
        sample_rate=sample_rate,
        duration_seconds=duration,
        bit_rate=bit_rate,
    )


def probe_audio(toolchain: FFmpegToolchain, input_file: Path) -> AudioStreamInfo:
    """Inspect the first audio stream of input_file."""
    result = run_capture(
        [
            str(toolchain.ffprobe),
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,channels,sample_rate,bit_rate:format=duration,bit_rate",
            "-of",
            "json",
            str(input_file),
        ],
        error_type=InputValidationError,
    )
    return parse_probe_output(result.stdout)
