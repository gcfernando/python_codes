# Developed by Gehan Fernando
"""Validates source and destination paths before any audio work starts."""

import os
from pathlib import Path

from ..core.errors import InputValidationError


def resolve_input(path: Path) -> Path:
    """Return the absolute path of an existing, non-empty source file."""
    try:
        resolved = path.expanduser().resolve(strict=True)
    except OSError as exc:
        raise InputValidationError(
            f"Input file does not exist or cannot be accessed: {path}"
        ) from exc

    if not resolved.is_file():
        raise InputValidationError(f"Input path is not a regular file: {resolved}")

    try:
        if resolved.stat().st_size <= 0:
            raise InputValidationError(f"Input file is empty: {resolved}")
    except OSError as exc:
        raise InputValidationError(f"Cannot inspect input file: {resolved}") from exc

    return resolved


def resolve_output(path: Path, *, overwrite: bool) -> Path:
    """Return an absolute .mp3 destination, creating its folder if needed."""
    output = path.expanduser().resolve(strict=False)

    if output.suffix.lower() != ".mp3":
        raise InputValidationError("Output file must use the .mp3 extension")

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise InputValidationError(f"Cannot create output directory: {output.parent}") from exc

    if not output.parent.is_dir():
        raise InputValidationError(f"Output parent is not a directory: {output.parent}")

    if output.exists():
        if not output.is_file():
            raise InputValidationError(f"Output path exists but is not a regular file: {output}")
        if not overwrite:
            raise InputValidationError(
                f"Output already exists: {output}. Use --overwrite to replace it."
            )

    return output


def ensure_different_files(input_file: Path, output_file: Path) -> None:
    """Refuse to encode a file on top of itself."""
    # Windows ignores letter case in file names, so the comparison does too
    if os.path.normcase(str(input_file)) == os.path.normcase(str(output_file)):
        raise InputValidationError("Input and output paths must be different")
