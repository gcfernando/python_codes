# Developed by Gehan Fernando
"""Where Audio8D finds its own files, and where it keeps your styles, cache and log."""

import os
import sys
from pathlib import Path

# Tests (and people who want a portable setup) can point everything somewhere else
HOME_OVERRIDE = "AUDIO8D_HOME"


def is_packaged() -> bool:
    """True inside the standalone Audio8D.exe built with PyInstaller."""
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """The folder Audio8D runs from: next to Audio8D.exe, or the project folder."""
    if is_packaged():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


def tools_dir() -> Path:
    """bin/executable, where the bundled ffmpeg and ffprobe live."""
    return app_dir() / "bin" / "executable"


def guide_file() -> Path:
    """The README that 'Open the full guide' shows."""
    return app_dir() / "README.md"


def config_dir() -> Path:
    """%APPDATA%\\Audio8D on Windows, ~/Library/... on macOS, ~/.config/... else."""
    override = os.environ.get(HOME_OVERRIDE)
    if override:
        return Path(override)
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "Audio8D"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Audio8D"
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "audio8d"


def cache_dir() -> Path:
    """A folder for measurements that are safe to delete at any time."""
    override = os.environ.get(HOME_OVERRIDE)
    if override:
        return Path(override) / "cache"
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "Audio8D" / "cache"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "Audio8D"
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "audio8d"


def presets_file() -> Path:
    """The TOML file that holds styles saved with --save-preset."""
    return config_dir() / "presets.toml"


def log_file() -> Path:
    """The technical log: %LOCALAPPDATA%\\Audio8D\\logs on Windows."""
    override = os.environ.get(HOME_OVERRIDE)
    if override:
        return Path(override) / "logs" / "audio8d.log"
    if os.name == "nt":
        return cache_dir().parent / "logs" / "audio8d.log"
    return config_dir() / "logs" / "audio8d.log"
