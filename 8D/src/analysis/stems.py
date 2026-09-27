# Developed by Gehan Fernando
"""Splits a song into vocals and music with Demucs, so the singer can stay central.

Demucs is a free AI model from Meta that separates voices from instruments.
It is large (it brings PyTorch), so it is an optional extra:

    python -m pip install demucs

The split takes a minute or two per song on a normal computer, so the
results are kept in the cache and reused for the same song.
"""

import hashlib
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

from ..core.errors import ConversionError, DependencyError
from ..core.locations import cache_dir, is_packaged
from ..ffmpeg import FFmpegToolchain, ffmpeg_prefix, run_capture
from ..ffmpeg.runner import NO_WINDOW

MODEL = "htdemucs"


def demucs_available() -> bool:
    """True when the optional Demucs package is installed for this Python."""
    # The standalone exe has no Python to run Demucs with, so it never offers it
    return not is_packaged() and importlib.util.find_spec("demucs") is not None


def demucs_hint() -> str:
    """How to get Demucs here, in plain words."""
    if is_packaged():
        return (
            "not included in the standalone Audio8D.exe (it needs a 1 GB AI model); "
            "the Python version of Audio8D can use it"
        )
    return "install it once with  python -m pip install demucs  then restart Audio8D"


def _song_key(song: Path) -> str:
    """Changes whenever the song file itself changes."""
    stat = song.stat()
    identity = f"{song.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{MODEL}"
    return hashlib.sha1(identity.encode("utf-8")).hexdigest()[:20]


def separate_vocals(toolchain: FFmpegToolchain, song: Path) -> tuple[Path, Path]:
    """(vocals.wav, music.wav) for the whole song, from the cache when possible."""
    if not demucs_available():
        raise DependencyError(
            f"Keeping vocals in the centre needs Demucs: {demucs_hint()}."
        )
    folder = cache_dir() / "stems" / _song_key(song)
    vocals, music = folder / "vocals.wav", folder / "no_vocals.wav"
    if vocals.is_file() and music.is_file():
        return vocals, music

    work = folder / "work"
    work.mkdir(parents=True, exist_ok=True)
    try:
        # Demucs reads a plain WAV most reliably, whatever the song's own format
        source = work / "song.wav"
        run_capture(
            [
                *ffmpeg_prefix(toolchain.ffmpeg),
                "-y",
                "-i",
                str(song),
                "-map",
                "0:a:0",
                "-ac",
                "2",
                "-ar",
                "44100",
                "-c:a",
                "pcm_f32le",
                str(source),
            ],
            error_type=ConversionError,
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "demucs.separate",
                "-n",
                MODEL,
                "--two-stems",
                "vocals",
                "--float32",
                "-o",
                str(work),
                "--filename",
                "{stem}.{ext}",
                str(source),
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            creationflags=NO_WINDOW,
        )
        if result.returncode != 0:
            raise ConversionError(
                "Demucs could not split the vocals: "
                + (result.stderr.strip().splitlines() or ["unknown error"])[-1]
            )
        made = work / MODEL
        shutil.move(str(made / "vocals.wav"), str(vocals))
        shutil.move(str(made / "no_vocals.wav"), str(music))
    except OSError as exc:
        raise ConversionError(f"Could not save the separated vocals: {exc}") from exc
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return vocals, music
