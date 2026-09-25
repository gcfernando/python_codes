# Developed by Gehan Fernando
"""Runs external tools safely and turns failures into Audio8D errors."""

import subprocess
from collections.abc import Sequence
from typing import TypeVar

from ..core.errors import Audio8DError

ErrorT = TypeVar("ErrorT", bound=Audio8DError)


def run_capture(
    command: Sequence[str],
    *,
    error_type: type[ErrorT],
) -> subprocess.CompletedProcess[str]:
    """Run a command without a shell and return its captured text output."""
    try:
        # shell=False keeps user-supplied file names from ever being parsed as shell syntax
        result = subprocess.run(
            list(command),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            shell=False,
        )
    except OSError as exc:
        raise error_type(f"Failed to start {command[0]!r}: {exc}") from exc

    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise error_type(f"Command failed with exit code {result.returncode}: {details}")

    return result
