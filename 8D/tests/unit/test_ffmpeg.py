# Developed by Gehan Fernando
"""Checks how Audio8D finds FFmpeg, builds its command and reads song details."""

import json
import os
from pathlib import Path

import pytest

from audio8d import ConversionError, DependencyError, InputValidationError
from audio8d.ffmpeg import (
    build_encode_command,
    parse_ebur128_summary,
    parse_probe_output,
    toolchain,
)
from audio8d.ffmpeg.toolchain import FFmpegToolchain, _has_audio_encoder, _has_filter


def test_encode_command_is_exact() -> None:
    command = build_encode_command(
        Path("ffmpeg"),
        Path("in.wav"),
        Path("out.mp3"),
        filter_chain="anull",
        mp3_quality=2,
    )

    assert command == [
        "ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error",
        "-i", "in.wav",
        "-map", "0:a:0", "-map_metadata", "0", "-vn",
        "-af", "anull",
        "-c:a", "libmp3lame", "-q:a", "2", "-ac", "2",
        "-id3v2_version", "3", "-write_id3v1", "1",
        "-n", "out.mp3",
    ]  # fmt: skip


def test_probe_parses_a_normal_stream() -> None:
    payload = {
        "streams": [{"codec_name": "flac", "channels": 2, "sample_rate": "48000"}],
        "format": {"duration": "12.5"},
    }
    info = parse_probe_output(json.dumps(payload))

    assert info.codec_name == "flac"
    assert info.channels == 2
    assert info.sample_rate == 48000
    assert info.duration_seconds == 12.5


def test_probe_tolerates_unknown_duration_and_rate() -> None:
    payload = {"streams": [{"channels": 1}], "format": {"duration": "N/A"}}
    info = parse_probe_output(json.dumps(payload))

    assert info.codec_name == "unknown"
    assert info.sample_rate is None
    assert info.duration_seconds is None


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        json.dumps({"streams": []}),
        json.dumps({"streams": [{"codec_name": "mp3"}]}),
        json.dumps({"streams": [{"channels": 0}]}),
        json.dumps({"streams": [{"channels": "two"}]}),
    ],
)
def test_probe_rejects_unusable_output(raw: str) -> None:
    with pytest.raises(InputValidationError):
        parse_probe_output(raw)


def test_capability_regexes_match_real_ffmpeg_listings() -> None:
    filters = (
        " TSC apulsator         A->A       Audio pulsator.\n"
        " ... aecho             A->A       Add echoing to the audio.\n"
    )
    encoders = " A....D libmp3lame           libmp3lame MP3 (MPEG audio layer 3)\n"

    assert _has_filter(filters, "apulsator")
    assert _has_filter(filters, "aecho")
    assert not _has_filter(filters, "alimiter")
    assert _has_audio_encoder(encoders, "libmp3lame")
    assert not _has_audio_encoder(encoders, "libshine")


def _fake_binary(folder: Path, name: str) -> Path:
    """An empty, executable stand-in for ffmpeg or ffprobe."""
    path = folder / (f"{name}.exe" if os.name == "nt" else name)
    path.write_bytes(b"")
    path.chmod(0o755)
    return path


def test_discover_prefers_bundled_binaries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(toolchain, "BUNDLED_DIR", tmp_path)
    ffmpeg = _fake_binary(tmp_path, "ffmpeg")
    ffprobe = _fake_binary(tmp_path, "ffprobe")

    found = FFmpegToolchain.discover()

    assert found.ffmpeg == ffmpeg.resolve()
    assert found.ffprobe == ffprobe.resolve()


def test_discover_explains_what_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(toolchain, "BUNDLED_DIR", tmp_path)
    monkeypatch.setattr(toolchain.shutil, "which", lambda _name: None)
    _fake_binary(tmp_path, "ffmpeg")

    with pytest.raises(DependencyError, match="ffprobe"):
        FFmpegToolchain.discover()


def test_top_quality_encodes_use_lames_most_careful_mode() -> None:
    cbr = build_encode_command(
        Path("ffmpeg"),
        Path("in.wav"),
        Path("out.mp3"),
        filter_chain="anull",
        mp3_quality=0,
        mp3_bitrate=320,
    )
    vbr = build_encode_command(
        Path("ffmpeg"),
        Path("in.wav"),
        Path("out.mp3"),
        filter_chain="anull",
        mp3_quality=0,
    )

    assert cbr[cbr.index("-b:a") + 1] == "320k"
    assert "-q:a" not in cbr
    assert cbr[cbr.index("-compression_level") + 1] == "0"
    assert vbr[vbr.index("-q:a") + 1] == "0"
    assert "-compression_level" in vbr


def test_meter_summary_is_read_correctly() -> None:
    log = """[Parsed_ebur128_3 @ 0000] t: 1.0 M: -30.0 S: -30.0 I: -99.0 LUFS
[Parsed_ebur128_3 @ 0000] Summary:

  Integrated loudness:
    I:         -27.4 LUFS
    Threshold: -37.9 LUFS

  Loudness range:
    LRA:         8.7 LU

  True peak:
    Peak:      -11.5 dBFS
"""
    measured = parse_ebur128_summary(log)

    assert measured.integrated_lufs == -27.4
    assert measured.true_peak_db == -11.5
    assert measured.range_lu == 8.7


def test_meter_summary_handles_silence() -> None:
    log = "Summary:\n    I:  -70.0 LUFS\n    LRA:  0.0 LU\n    Peak:  -inf dBFS\n"

    assert parse_ebur128_summary(log).true_peak_db == float("-inf")


def test_missing_meter_summary_is_a_conversion_error() -> None:
    with pytest.raises(ConversionError):
        parse_ebur128_summary("no summary here")


def test_probe_reads_the_source_bitrate() -> None:
    payload = {
        "streams": [
            {
                "codec_name": "mp3",
                "channels": 2,
                "sample_rate": "48000",
                "bit_rate": "320000",
            }
        ],
        "format": {"duration": "292.4"},
    }
    info = parse_probe_output(json.dumps(payload))

    assert info.bit_rate == 320000
    assert info.is_lossless is False


def test_probe_falls_back_to_the_file_bitrate() -> None:
    payload = {
        "streams": [{"codec_name": "flac", "channels": 2}],
        "format": {"bit_rate": "1411000"},
    }
    info = parse_probe_output(json.dumps(payload))

    assert info.bit_rate == 1411000
    assert info.is_lossless is True
