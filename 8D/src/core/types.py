# Developed by Gehan Fernando
"""Plain data types passed between the Audio8D layers."""

from dataclasses import dataclass

# Codecs that store sound perfectly, so the MP3 encode is the only lossy step
LOSSLESS_CODECS = frozenset(
    {
        "flac",
        "alac",
        "wavpack",
        "ape",
        "tta",
        "truehd",
        "mlp",
        "shorten",
        "mp4als",
        "tak",
    }
)


@dataclass(frozen=True, slots=True)
class AudioStreamInfo:
    """What FFprobe told us about the first audio stream in the source file."""

    codec_name: str
    channels: int
    sample_rate: int | None
    duration_seconds: float | None
    # Bits per second of the source stream, when the file says so
    bit_rate: int | None = None

    @property
    def is_lossless(self) -> bool:
        """True for FLAC, ALAC, WAV/AIFF (PCM) and the other perfect-copy formats."""
        return self.codec_name in LOSSLESS_CODECS or self.codec_name.startswith("pcm_")
