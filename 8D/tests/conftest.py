# Developed by Gehan Fernando
"""Shared pytest fixtures."""

import subprocess
from pathlib import Path

import pytest

from src import DependencyError
from src.ffmpeg import FFmpegToolchain


def find_toolchain() -> FFmpegToolchain | None:
    """The same FFmpeg Audio8D itself would use, or None if there is none."""
    try:
        return FFmpegToolchain.discover()
    except DependencyError:
        return None


def _synthesize(path: Path, *lavfi_args: str) -> Path:
    """Render a short test signal with FFmpeg's built-in generators."""
    toolchain = find_toolchain()
    assert toolchain is not None
    subprocess.run(
        [
            str(toolchain.ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            *lavfi_args,
            str(path),
        ],
        check=True,
    )
    return path


@pytest.fixture
def stereo_tone(tmp_path: Path) -> Path:
    """Three seconds of a tagged stereo MP3 (440 Hz left, 660 Hz right)."""
    return _synthesize(
        tmp_path / "tone.mp3",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
        "-f", "lavfi", "-i", "sine=frequency=660:duration=3",
        "-filter_complex", "[0][1]amerge=inputs=2",
        "-metadata", "title=Test Tone",
        "-c:a", "libmp3lame", "-q:a", "2",
    )  # fmt: skip


@pytest.fixture
def mono_wav(tmp_path: Path) -> Path:
    """Two seconds of a mono WAV to make sure upmixing to stereo works."""
    return _synthesize(
        tmp_path / "mono.wav", "-f", "lavfi", "-i", "sine=frequency=220:duration=2"
    )


@pytest.fixture
def dynamic_song(tmp_path: Path) -> Path:
    """Twenty seconds of pink noise that swells and fades, so it has real dynamics."""
    return _synthesize(
        tmp_path / "dynamic.wav",
        "-f", "lavfi", "-i", "anoisesrc=color=pink:duration=20:amplitude=0.3",
        "-af", "volume='0.3+0.7*abs(sin(2*PI*t/10))':eval=frame", "-ac", "2",
    )  # fmt: skip
