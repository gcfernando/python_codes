# Developed by Gehan Fernando
"""Ready-made sound styles, so nobody has to guess numbers."""

from dataclasses import dataclass, replace

from .settings import EffectConfig


@dataclass(frozen=True, slots=True)
class Preset:
    """A named combination of settings with a one-line description."""

    name: str
    summary: str
    config: EffectConfig


# Best of best: top MP3 bitrate, MP3-safe peak headroom, loudness without squashing
_STUDIO = EffectConfig(
    rotation_seconds=8.0,
    intensity=0.80,
    ambience=0.25,
    limiter_ceiling=0.84,
    mp3_quality=0,
    loudness_target=-14.0,
    mp3_bitrate=320,
)

# Shown in this order by --list-presets; studio first because it is the one to pick
_ALL_PRESETS = (
    Preset(
        name="studio",
        summary="Best of best: 320 kbps, -14 LUFS goal, dynamics untouched",
        config=_STUDIO,
    ),
    Preset(
        name="streaming",
        summary="Like studio, always exactly -14 LUFS (light peak limiting)",
        config=replace(_STUDIO, exact_loudness=True),
    ),
    Preset(
        name="classic",
        summary="The original default sound (used if you pick nothing)",
        config=EffectConfig(),
    ),
    Preset(
        name="smooth",
        summary="Slow and relaxed: lo-fi, acoustic, background",
        config=EffectConfig(rotation_seconds=12.0, intensity=0.75, ambience=0.20),
    ),
    Preset(
        name="strong",
        summary="Big, obvious movement: pop, EDM, '8D video' feel",
        config=EffectConfig(rotation_seconds=8.0, intensity=0.95, ambience=0.35),
    ),
    Preset(
        name="spacious",
        summary="Roomy and atmospheric: ambient, cinematic, slow",
        config=EffectConfig(rotation_seconds=10.0, intensity=0.82, ambience=0.50),
    ),
    Preset(
        name="voice",
        summary="Gentle and dry: podcasts, audiobooks, meditation",
        config=EffectConfig(rotation_seconds=16.0, intensity=0.60, ambience=0.0),
    ),
    Preset(
        name="whirlwind",
        summary="Very fast spin: short clips and ringtones",
        config=EffectConfig(rotation_seconds=3.0, intensity=1.0, ambience=0.30),
    ),
)

PRESETS: dict[str, Preset] = {preset.name: preset for preset in _ALL_PRESETS}
RECOMMENDED_PRESET = "studio"
