# Developed by Gehan Fernando
"""Write-then-publish helpers so a half-encoded MP3 is never visible."""

import os
import uuid
from pathlib import Path

from ..core.errors import ConversionError, InputValidationError


def create_temporary_output(output_file: Path) -> Path:
    """Pick a hidden, unique scratch name in the same folder as the destination."""
    # Same folder means same filesystem, which keeps the final rename atomic
    return output_file.with_name(f".{output_file.stem}.{uuid.uuid4().hex}.partial.mp3")


def _publish_without_overwrite(temporary_file: Path, output_file: Path) -> None:
    """Move the file into place, failing if something already sits there."""
    try:
        # A hard link fails if output_file appeared after validation, so no race
        os.link(temporary_file, output_file)
    except FileExistsError:
        raise
    except OSError:
        # FAT32/exFAT and some shares lack hard links; Windows rename never overwrites
        if os.name != "nt":
            raise
        os.rename(temporary_file, output_file)
        return

    temporary_file.unlink()


def commit_output(temporary_file: Path, output_file: Path, *, overwrite: bool) -> None:
    """Publish a finished encode under its real name."""
    try:
        if overwrite:
            os.replace(temporary_file, output_file)
        else:
            _publish_without_overwrite(temporary_file, output_file)
    except FileExistsError as exc:
        raise InputValidationError(
            f"Output appeared while conversion was running: {output_file}"
        ) from exc
    except OSError as exc:
        raise ConversionError(
            f"Unable to publish completed output to {output_file}: {exc}"
        ) from exc
