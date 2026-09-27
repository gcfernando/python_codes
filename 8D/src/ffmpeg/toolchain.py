# Developed by ::> Gehan Fernando
"""Locates FFmpeg/FFprobe and checks the build has what the effect needs."""

import logging
import os
import re
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..core.errors import DependencyError
from ..core.locations import tools_dir
from ..effects.graph import GRAPH_FILTERS
from .runner import run_capture

# The filters every conversion uses; loudness adds its meter on top
REQUIRED_FILTERS = GRAPH_FILTERS
REQUIRED_ENCODER = "libmp3lame"
LOG = logging.getLogger(__name__)

# The bundled ffmpeg and ffprobe in bin/executable win over anything on PATH
BUNDLED_DIR = tools_dir()


def _find_executable(name: str) -> str | None:
    """Return the bundled copy of a tool if present, otherwise search PATH."""
    bundled = BUNDLED_DIR / (f"{name}.exe" if os.name == "nt" else name)
    if bundled.is_file() and os.access(bundled, os.X_OK):
        return str(bundled)
    return shutil.which(name)


def _has_filter(filters_output: str, name: str) -> bool:
    """Look for a filter row in the output of `ffmpeg -filters`."""
    # Rows start with flag columns such as 'TSC' or '...', then the filter name
    return (
        re.search(rf"(?m)^\s*[TSC\.]+\s+{re.escape(name)}\s+", filters_output)
        is not None
    )


def _has_audio_encoder(encoders_output: str, name: str) -> bool:
    """Look for an audio encoder row in the output of `ffmpeg -encoders`."""
    # Audio encoder rows start with 'A' followed by five more flag characters
    return (
        re.search(rf"(?m)^\s*A.....\s+{re.escape(name)}\s+", encoders_output)
        is not None
    )


@dataclass(frozen=True, slots=True)
class FFmpegToolchain:
    """Absolute paths to the ffmpeg and ffprobe executables."""

    ffmpeg: Path
    ffprobe: Path

    @classmethod
    def discover(cls) -> "FFmpegToolchain":
        """Find both tools (bin/executable first, then PATH) or say which is missing."""
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
                + f". Put ffmpeg and ffprobe in {BUNDLED_DIR}, or install FFmpeg "
                "and add it to PATH."
            )

        found = cls(ffmpeg=Path(ffmpeg).resolve(), ffprobe=Path(ffprobe).resolve())
        LOG.debug("Using %s and %s", found.ffmpeg, found.ffprobe)
        return found

    def validate_capabilities(
        self, extra_filters: Iterable[str] = (), encoder: str = REQUIRED_ENCODER
    ) -> None:
        """Fail early if this FFmpeg build lacks a filter or the chosen encoder."""
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

        if not _has_audio_encoder(encoders_output, encoder):
            raise DependencyError(
                f"This FFmpeg build does not include the {encoder} encoder."
            )
