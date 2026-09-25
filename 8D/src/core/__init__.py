# Developed by Gehan Fernando
"""Settings, presets, shared types, and exceptions used across the whole package."""

from .errors import Audio8DError, ConversionError, DependencyError, InputValidationError
from .presets import PRESETS, RECOMMENDED_PRESET, Preset
from .settings import EffectConfig
from .types import AudioStreamInfo

__all__ = [
    "PRESETS",
    "RECOMMENDED_PRESET",
    "Audio8DError",
    "AudioStreamInfo",
    "ConversionError",
    "DependencyError",
    "EffectConfig",
    "InputValidationError",
    "Preset",
]
