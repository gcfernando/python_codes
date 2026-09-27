# Developed by Gehan Fernando
"""Validates source and destination paths before any audio work starts."""

import os
from pathlib import Path

from ..core.errors import InputValidationError
from ..core.settings import FORMAT_EXTENSIONS

# How the new file is named: "<song> (8D).mp3", or the original name kept
NAME_STYLES = ("8d", "original")
SUFFIX_8D = " (8D)"


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


def format_for_extension(path: Path) -> str | None:
    """'flac' for 'song.flac', or None when the extension is not an output format."""
    suffix = path.suffix.lower()
    for name, extension in FORMAT_EXTENSIONS.items():
        if extension == suffix:
            return name
    return None


def resolve_output(path: Path, *, overwrite: bool, extension: str = ".mp3") -> Path:
    """Return an absolute destination with the right extension, making its folder."""
    output = path.expanduser().resolve(strict=False)

    if output.suffix.lower() != extension:
        raise InputValidationError(f"Output file must use the {extension} extension")

    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise InputValidationError(
            f"Cannot create output directory: {output.parent}"
        ) from exc

    if not output.parent.is_dir():
        raise InputValidationError(f"Output parent is not a directory: {output.parent}")

    if output.exists():
        if not output.is_file():
            raise InputValidationError(
                f"Output path exists but is not a regular file: {output}"
            )
        if not overwrite:
            raise InputValidationError(
                f"Output already exists: {output}. Use --overwrite to replace it."
            )

    return output


def same_file(first: Path, second: Path) -> bool:
    """True when two paths name the same file (Windows ignores letter case)."""
    return os.path.normcase(str(first.expanduser().resolve(strict=False))) == (
        os.path.normcase(str(second.expanduser().resolve(strict=False)))
    )


def output_name(input_path: Path, extension: str, name_style: str = "8d") -> str:
    """'song (8D).mp3', or 'song.mp3' when the original name is kept."""
    suffix = "" if name_style == "original" else SUFFIX_8D
    return f"{input_path.stem}{suffix}{extension}"


def default_output_for(
    input_path: Path,
    extension: str = ".mp3",
    *,
    output_dir: Path | None = None,
    name_style: str = "8d",
    relative_to: Path | None = None,
) -> Path:
    """Where the 8D copy goes: beside the original, or inside output_dir.

    With relative_to (the folder a batch started from), sub-folders are mirrored
    inside output_dir, so 'Rock/a.mp3' lands in '<output_dir>/Rock/a (8D).mp3'.
    """
    name = output_name(input_path, extension, name_style)
    if output_dir is None:
        return input_path.with_name(name)
    folder = output_dir
    if relative_to is not None:
        try:
            folder = output_dir / input_path.parent.relative_to(relative_to)
        except ValueError:
            folder = output_dir
    return folder / name
