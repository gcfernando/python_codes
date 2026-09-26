# Developed by Gehan Fernando
"""Real conversions through FFmpeg, from test tones to finished 8D MP3s."""

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from audio8d import (
    PRESETS,
    DependencyError,
    EffectConfig,
    InputValidationError,
    convert,
)
from audio8d.ffmpeg.toolchain import BUNDLED_DIR, FFmpegToolchain

# conftest has already loaded audio8d, so this discovery matches the app's own
try:
    TOOLCHAIN: FFmpegToolchain | None = FFmpegToolchain.discover()
except DependencyError:
    TOOLCHAIN = None

# These tests drive real FFmpeg binaries, so skip cleanly on machines without them
pytestmark = pytest.mark.skipif(TOOLCHAIN is None, reason="ffmpeg/ffprobe not found")


def _probe(path: Path) -> dict:
    """Return FFprobe's view of the finished file."""
    assert TOOLCHAIN is not None
    result = subprocess.run(
        [
            str(TOOLCHAIN.ffprobe), "-v", "error",
            "-show_entries", "stream=codec_name,channels:format_tags=title",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    return json.loads(result.stdout)


def _leftover_scratch_files(folder: Path) -> list[Path]:
    """Hidden half-finished files that a clean run must never leave behind."""
    return list(folder.glob(".*.partial.mp3"))


def test_stereo_source_becomes_tagged_stereo_mp3(
    stereo_tone: Path, tmp_path: Path
) -> None:
    output = tmp_path / "out" / "tone_8d.mp3"

    info = convert(stereo_tone, output, EffectConfig())

    assert info.channels == 2
    probed = _probe(output)
    assert probed["streams"][0]["codec_name"] == "mp3"
    assert probed["streams"][0]["channels"] == 2
    assert probed["format"]["tags"]["title"] == "Test Tone"
    assert not _leftover_scratch_files(output.parent)


def test_mono_source_is_upmixed_to_stereo(mono_wav: Path, tmp_path: Path) -> None:
    output = tmp_path / "mono_8d.mp3"

    info = convert(mono_wav, output, EffectConfig(ambience=0.0, mp3_quality=0))

    assert info.channels == 1
    assert _probe(output)["streams"][0]["channels"] == 2


def test_existing_output_is_protected_until_overwrite(
    stereo_tone: Path, tmp_path: Path
) -> None:
    output = tmp_path / "tone_8d.mp3"
    output.write_bytes(b"keep me")

    with pytest.raises(InputValidationError):
        convert(stereo_tone, output, EffectConfig())
    assert output.read_bytes() == b"keep me"

    convert(stereo_tone, output, EffectConfig(), overwrite=True)
    assert output.read_bytes() != b"keep me"
    assert not _leftover_scratch_files(tmp_path)


def test_non_audio_input_is_rejected(tmp_path: Path) -> None:
    junk = tmp_path / "notes.txt"
    junk.write_text("definitely not audio")

    with pytest.raises(InputValidationError):
        convert(junk, tmp_path / "out.mp3", EffectConfig())


def test_bundled_binaries_win_over_path() -> None:
    bundled = BUNDLED_DIR / "ffmpeg.exe"
    if not bundled.is_file():
        pytest.skip("no ffmpeg.exe bundled in 8D/src")

    assert TOOLCHAIN is not None
    assert TOOLCHAIN.ffmpeg == bundled.resolve()
    assert TOOLCHAIN.ffprobe == (BUNDLED_DIR / "ffprobe.exe").resolve()
    TOOLCHAIN.validate_capabilities()


def test_standalone_run_from_src_converts_a_song(stereo_tone: Path) -> None:
    src = BUNDLED_DIR
    # Not installed, started from inside src, and only the song name given
    result = subprocess.run(
        [sys.executable, "-S", ".", str(stereo_tone)],
        cwd=src,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = stereo_tone.with_name("tone (8D).mp3")
    assert _probe(output)["streams"][0]["channels"] == 2


def _loudness(path: Path) -> tuple[float, float]:
    """Integrated loudness (LUFS) and true peak (dBFS) measured by FFmpeg's ebur128."""
    assert TOOLCHAIN is not None
    result = subprocess.run(
        [str(TOOLCHAIN.ffmpeg), "-hide_banner", "-nostats", "-i", str(path),
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    summary = result.stderr[result.stderr.rindex("Summary:") :]
    integrated = float(summary.split("I:")[1].split("LUFS")[0])
    peak = float(summary.split("Peak:")[1].split("dBFS")[0])
    return integrated, peak


def test_studio_preset_hits_streaming_loudness(
    stereo_tone: Path, tmp_path: Path
) -> None:
    output = tmp_path / "tone_studio.mp3"
    convert(stereo_tone, output, PRESETS["studio"].config)

    integrated, peak = _loudness(output)
    # Within 1.5 LU of -14 LUFS, with peaks under the ceiling plus a little MP3 slack
    assert -15.5 <= integrated <= -12.5
    assert peak <= -0.3
    probed = _probe(output)["streams"][0]
    assert probed["channels"] == 2


def _loudness_range(path: Path) -> float:
    """Loudness range (LRA) in LU, which only changes if the dynamics are squashed."""
    assert TOOLCHAIN is not None
    result = subprocess.run(
        [str(TOOLCHAIN.ffmpeg), "-hide_banner", "-nostats", "-i", str(path),
         "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, check=True,
    )  # fmt: skip
    summary = result.stderr[result.stderr.rindex("Summary:") :]
    return float(summary.split("LRA:")[1].split("LU")[0])


def test_studio_changes_volume_but_never_the_dynamics(
    dynamic_song: Path, tmp_path: Path
) -> None:
    song = dynamic_song
    studio = PRESETS["studio"].config
    loud = tmp_path / "studio.mp3"
    natural = tmp_path / "natural.mp3"
    plans = []

    convert(song, loud, studio, on_loudness=plans.append)
    convert(song, natural, replace(studio, loudness_target=None))

    assert plans and plans[0].gain_db != 0
    assert _loudness_range(loud) == pytest.approx(_loudness_range(natural), abs=0.3)
    integrated, peak = _loudness(loud)
    assert integrated == pytest.approx(plans[0].expected_lufs, abs=0.6)
    assert peak <= -0.9
