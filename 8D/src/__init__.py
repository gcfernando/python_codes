# Developed by Gehan Fernando
"""Audio8D: turn any audio file into an 8D-style headphone MP3."""

from .core import (
    PRESETS,
    RECOMMENDED_PRESET,
    Audio8DError,
    AudioStreamInfo,
    ConversionError,
    DependencyError,
    EffectConfig,
    InputValidationError,
    Preset,
)
from .pipeline import convert

__author__ = "Gehan Fernando"
# Must match `version` in pyproject.toml; test_presets.py checks that they agree
__version__ = "1.0.0"

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
    "convert",
]
