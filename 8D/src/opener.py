# Developed by Gehan Fernando
"""Opens a finished song or a folder with the computer's usual app."""

import logging
import os
import subprocess
import sys
from pathlib import Path

LOG = logging.getLogger(__name__)


def open_path(path: Path) -> None:
    """Open a file or folder with whatever app the computer uses for it."""
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]  # pylint: disable=no-member
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])  # pylint: disable=consider-using-with
        else:
            subprocess.Popen(["xdg-open", str(path)])  # pylint: disable=consider-using-with
    except OSError as exc:
        LOG.warning("Could not open %s: %s", path, exc)
