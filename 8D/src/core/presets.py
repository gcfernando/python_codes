# Developed by ::> Gehan Fernando
"""Ready-made sound styles, so nobody has to guess numbers."""

from dataclasses import dataclass, replace

from .settings import EffectConfig


@dataclass(frozen=True, slots=True)
class Preset:
    """A named combination of settings with a one-line description."""

    name: str
    summary: str
    config: EffectConfig
    # True for styles the user saved with --save-preset
    custom: bool = False

    @property
    def label(self) -> str:
        """The name people see: built-in styles capitalised (Studio), yours as saved."""
        return self.name if self.custom else self.name[:1].upper() + self.name[1:]


# Best of best: top MP3 bitrate, MP3-safe peak headroom, loudness without squashing
_STUDIO = EffectConfig(
    rotation_seconds=8.0,
    intensity=0.80,
    ambience=0.25,
    limiter_ceiling=0.84,
    quality=0,
    loudness_target=-14.0,
    bitrate=320,
)

# Shown in this order by --list-presets; studio first because it is the one to pick
_ALL_PRESETS = (
    Preset(
        name="studio",
        summary="Best of best: 3D sound, 320 kbps, -14 LUFS goal, dynamics untouched",
        config=_STUDIO,
    ),
    Preset(
        name="streaming",
        summary="Like Studio, always exactly -14 LUFS (light peak limiting)",
        config=replace(_STUDIO, exact_loudness=True),
    ),
    Preset(
        name="lossless",
        summary="Like Studio, saved as FLAC: nothing lost at all",
        # FLAC has no encoder overshoot, so the roof can sit at -1 dBFS
        config=replace(_STUDIO, output_format="flac", limiter_ceiling=0.89),
    ),
    Preset(
        name="hifi",
        summary="Most faithful: FLAC, the original's own loudness, gentle 3D",
        # Lossless, same rate and loudness as the song, a little less movement and room
        config=replace(
            _STUDIO,
            output_format="flac",
            limiter_ceiling=0.89,
            loudness_target=None,
            match_loudness=True,
            intensity=0.75,
            ambience=0.20,
        ),
    ),
    Preset(
        name="classic",
        summary="The everyday default (used if you pick nothing)",
        config=EffectConfig(),
    ),
    Preset(
        name="groove",
        summary="Loops round each ear in time with the beat: dance, pop, hip-hop",
        config=replace(_STUDIO, path="figure8", intensity=0.90, beat_sync=True),
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
        name="sky",
        summary="Drifts up over your head and back: chill, ambient",
        config=EffectConfig(
            rotation_seconds=12.0,
            intensity=0.80,
            ambience=0.45,
            elevation=0.7,
            path="wander",
        ),
    ),
    Preset(
        name="voice",
        summary="Gentle and dry: podcasts, audiobooks, meditation",
        config=EffectConfig(
            rotation_seconds=16.0, intensity=0.60, ambience=0.0, path="arc"
        ),
    ),
    Preset(
        name="whirlwind",
        summary="Very fast spin: short clips and ringtones",
        config=EffectConfig(rotation_seconds=3.0, intensity=1.0, ambience=0.30),
    ),
    Preset(
        name="speakers",
        summary="Safe for speakers and car stereos, not just headphones",
        config=EffectConfig(engine="pan", intensity=0.55, ambience=0.20),
    ),
    Preset(
        name="retro",
        summary="The old left-right ping-pong sound of the first Audio8D",
        config=EffectConfig(engine="pan", bass_hz=0.0, fade_seconds=0.0),
    ),
)

PRESETS: dict[str, Preset] = {preset.name: preset for preset in _ALL_PRESETS}
RECOMMENDED_PRESET = "studio"
