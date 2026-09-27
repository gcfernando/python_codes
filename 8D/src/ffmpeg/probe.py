# Developed by ::> Gehan Fernando
"""Reads source-stream metadata through FFprobe's JSON output."""

import json
from pathlib import Path
from typing import Any

from ..core.errors import InputValidationError
from ..core.types import AudioStreamInfo
from .runner import run_capture
from .toolchain import FFmpegToolchain


def _tag(tags: dict[str, Any], name: str) -> str | None:
    """A tag by name, whatever letter case the file used for it."""
    for key, value in tags.items():
        if key.lower() == name and str(value).strip():
            return str(value).strip()
    return None


def _optional_number(value: Any, kind: type) -> Any:
    """int/float from FFprobe text, or None for missing and 'N/A' values."""
    if value in (None, "", "N/A"):
        return None
    return kind(value)


def parse_probe_output(raw_json: str) -> AudioStreamInfo:
    """Turn FFprobe JSON into an AudioStreamInfo or reject unusable input."""
    try:
        payload: dict[str, Any] = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise InputValidationError("FFprobe returned malformed JSON") from exc

    streams = payload.get("streams") or []
    # Older callers only asked for audio streams, so a missing type means audio
    audio = [s for s in streams if s.get("codec_type", "audio") == "audio"]
    if not audio:
        raise InputValidationError(
            "The input file does not contain a usable audio stream"
        )

    stream = audio[0]
    container = payload.get("format") or {}
    tags = {**(container.get("tags") or {}), **(stream.get("tags") or {})}
    cover = any(
        s.get("codec_type") == "video"
        and (s.get("disposition") or {}).get("attached_pic") == 1
        for s in streams
    )

    try:
        channels = int(stream["channels"])
        sample_rate = _optional_number(stream.get("sample_rate"), int)
        # Raw streams and some live captures report "N/A" instead of a length
        duration = _optional_number(container.get("duration"), float)
        codec_name = str(stream.get("codec_name") or "unknown")
        # Some containers only store the whole file's bitrate, so fall back to that
        bit_rate = _optional_number(
            stream.get("bit_rate") or container.get("bit_rate"), int
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise InputValidationError(
            "FFprobe returned incomplete or invalid audio metadata"
        ) from exc

    if channels < 1:
        raise InputValidationError("The input audio reports an invalid channel count")

    return AudioStreamInfo(
        codec_name=codec_name,
        channels=channels,
        sample_rate=sample_rate,
        duration_seconds=duration,
        bit_rate=bit_rate,
        title=_tag(tags, "title"),
        has_cover_art=cover,
    )


def probe_audio(toolchain: FFmpegToolchain, input_file: Path) -> AudioStreamInfo:
    """Inspect the first audio stream of input_file, and whether it has album art."""
    result = run_capture(
        [
            str(toolchain.ffprobe),
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,channels,sample_rate,bit_rate"
            ":stream_disposition=attached_pic:stream_tags=title"
            ":format=duration,bit_rate:format_tags=title",
            "-of",
            "json",
            str(input_file),
        ],
        error_type=InputValidationError,
    )
    return parse_probe_output(result.stdout)
