# Developed by Gehan Fernando
"""User-facing knobs for the 8D effect and the MP3 encoder."""

from dataclasses import dataclass

from .errors import InputValidationError

# The constant bitrates that make sense for music; 320 is the highest MP3 allows
MP3_BITRATES = (128, 160, 192, 224, 256, 320)


@dataclass(frozen=True, slots=True)
class EffectConfig:
    """Everything that shapes how the finished track sounds."""

    rotation_seconds: float = 8.0
    intensity: float = 0.85
    ambience: float = 0.30
    limiter_ceiling: float = 0.95
    mp3_quality: int = 2
    # None keeps the natural level; a LUFS value (e.g. -14) matches streaming loudness
    loudness_target: float | None = None
    # None uses the variable --quality scale; a kbps value locks a constant bitrate
    mp3_bitrate: int | None = None
    # True hits the loudness target even if the limiter must shave the loudest peaks
    exact_loudness: bool = False

    def validate(self) -> None:
        """Raise InputValidationError if any value is outside its safe range."""
        # apulsator only accepts 0.01-100 Hz, so the period is capped at 100 s
        if not 2.0 <= self.rotation_seconds <= 100.0:
            raise InputValidationError(
                "rotation_seconds must be between 2.0 and 100.0 seconds"
            )

        if not 0.0 <= self.intensity <= 1.0:
            raise InputValidationError("intensity must be between 0.0 and 1.0")

        if not 0.0 <= self.ambience <= 1.0:
            raise InputValidationError("ambience must be between 0.0 and 1.0")

        # 0.0625 is the lowest ceiling alimiter accepts (about -24 dBFS)
        if not 0.0625 <= self.limiter_ceiling <= 1.0:
            raise InputValidationError("limiter_ceiling must be between 0.0625 and 1.0")

        if not 0 <= self.mp3_quality <= 9:
            raise InputValidationError("mp3_quality must be an integer from 0 to 9")

        # -30 is whisper-quiet and -5 is louder than any real master
        if (
            self.loudness_target is not None
            and not -30.0 <= self.loudness_target <= -5.0
        ):
            raise InputValidationError(
                "loudness_target must be between -30 and -5 LUFS"
            )

        if self.mp3_bitrate is not None and self.mp3_bitrate not in MP3_BITRATES:
            raise InputValidationError(
                "mp3_bitrate must be one of "
                + ", ".join(map(str, MP3_BITRATES))
                + " kbps"
            )
