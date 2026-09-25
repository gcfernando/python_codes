# Developed by Gehan Fernando
"""Locates FFmpeg/FFprobe and checks the build has what the effect needs."""

import os
import re
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..core.errors import DependencyError
from .runner import run_capture

# The filters every conversion uses; loudness adds its own two on top
REQUIRED_FILTERS = frozenset({"aformat", "aecho", "apulsator", "alimiter"})
REQUIRED_ENCODER = "libmp3lame"

# Copies of ffmpeg.exe and ffprobe.exe placed in src win over whatever is on PATH
BUNDLED_DIR = Path(__file__).resolve().parent.parent


def _find_executable(name: str) -> str | None:
    """Return the bundled copy of a tool if present, otherwise search PATH."""
    bundled = BUNDLED_DIR / (f"{name}.exe" if os.name == "nt" else name)
    if bundled.is_file() and os.access(bundled, os.X_OK):
        return str(bundled)
    return shutil.which(name)


def _has_filter(filters_output: str, name: str) -> bool:
    """Look for a filter row in the output of `ffmpeg -filters`."""
    return re.search(rf"(?m)^\s*[TSC\.]+\s+{re.escape(name)}\s+", filters_output) is not None


def _has_audio_encoder(encoders_output: str, name: str) -> bool:
    """Look for an audio encoder row in the output of `ffmpeg -encoders`."""
    return re.search(rf"(?m)^\s*A.....\s+{re.escape(name)}\s+", encoders_output) is not None


@dataclass(frozen=True, slots=True)
class FFmpegToolchain:
    """Absolute paths to the ffmpeg and ffprobe executables."""

    ffmpeg: Path
    ffprobe: Path

    @classmethod
    def discover(cls) -> "FFmpegToolchain":
        """Find both tools (bundled first, then PATH) or explain which is missing."""
        ffmpeg = _find_executable("ffmpeg")
        ffprobe = _find_executable("ffprobe")

        if ffmpeg is None or ffprobe is None:
            missing = [
                name
                for name, executable in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe))
                if executable is None
            ]
            raise DependencyError(
                "Missing required executable(s): "
                + ", ".join(missing)
                + f". Copy them into {BUNDLED_DIR} or install FFmpeg and add it to PATH."
            )

        return cls(ffmpeg=Path(ffmpeg).resolve(), ffprobe=Path(ffprobe).resolve())

    def validate_capabilities(self, extra_filters: Iterable[str] = ()) -> None:
        """Fail early if this FFmpeg build lacks a filter or the LAME encoder."""
        filters_output = run_capture(
            [str(self.ffmpeg), "-hide_banner", "-filters"],
            error_type=DependencyError,
        ).stdout
        encoders_output = run_capture(
            [str(self.ffmpeg), "-hide_banner", "-encoders"],
            error_type=DependencyError,
        ).stdout

        missing_filters = sorted(
            name
            for name in REQUIRED_FILTERS | set(extra_filters)
            if not _has_filter(filters_output, name)
        )
        if missing_filters:
            raise DependencyError(
                "This FFmpeg build is missing required audio filter(s): "
                + ", ".join(missing_filters)
            )

        if not _has_audio_encoder(encoders_output, REQUIRED_ENCODER):
            raise DependencyError("This FFmpeg build does not include the libmp3lame encoder.")
