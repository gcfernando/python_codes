# Developed by Gehan Fernando
"""Assembles the exact ffmpeg argument list used for encoding."""

from pathlib import Path


def _quality_arguments(mp3_quality: int, mp3_bitrate: int | None) -> list[str]:
    """A constant bitrate when one is set, otherwise LAME's variable quality scale."""
    arguments = (
        ["-b:a", f"{mp3_bitrate}k"] if mp3_bitrate else ["-q:a", str(mp3_quality)]
    )
    # Top-quality requests also get LAME's slowest, most careful algorithm (LAME -q 0)
    if mp3_bitrate or mp3_quality == 0:
        arguments += ["-compression_level", "0"]
    return arguments


def build_encode_command(
    ffmpeg: Path,
    input_file: Path,
    output_file: Path,
    *,
    filter_chain: str,
    mp3_quality: int,
    mp3_bitrate: int | None = None,
) -> list[str]:
    """Return the argv that renders input_file through the effect into an MP3."""
    return [
        str(ffmpeg),
        "-hide_banner",
        "-nostdin",
        "-loglevel",
        "error",
        "-i",
        str(input_file),
        # First audio stream only, so cover art and video tracks never trip the encoder
        "-map",
        "0:a:0",
        # Carry over title, artist, album and friends from the source
        "-map_metadata",
        "0",
        "-vn",
        "-af",
        filter_chain,
        "-c:a",
        "libmp3lame",
        *_quality_arguments(mp3_quality, mp3_bitrate),
        "-ac",
        "2",
        # ID3v2.3 plus a v1 tag is what car stereos and older players read most reliably
        "-id3v2_version",
        "3",
        "-write_id3v1",
        "1",
        # Never let ffmpeg overwrite anything; publishing is handled by files.atomic
        "-n",
        str(output_file),
    ]
