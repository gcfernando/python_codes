# Developed by Gehan Fernando
"""Checks that song and output paths are validated before any work starts."""

from pathlib import Path

import pytest

from audio8d import InputValidationError
from audio8d.files import ensure_different_files, resolve_input, resolve_output


def test_missing_input_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputValidationError, match="does not exist"):
        resolve_input(tmp_path / "missing.mp3")


def test_empty_input_is_rejected(tmp_path: Path) -> None:
    empty = tmp_path / "empty.mp3"
    empty.touch()

    with pytest.raises(InputValidationError, match="empty"):
        resolve_input(empty)


def test_directory_input_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(InputValidationError, match="not a regular file"):
        resolve_input(tmp_path)


def test_valid_input_resolves_to_absolute_path(tmp_path: Path) -> None:
    song = tmp_path / "song.mp3"
    song.write_bytes(b"audio")

    assert resolve_input(song) == song.resolve()


def test_output_must_be_mp3(tmp_path: Path) -> None:
    with pytest.raises(InputValidationError):
        resolve_output(tmp_path / "result.wav", overwrite=False)


def test_output_extension_check_ignores_case(tmp_path: Path) -> None:
    assert resolve_output(tmp_path / "RESULT.MP3", overwrite=False).name == "RESULT.MP3"


def test_missing_output_folders_are_created(tmp_path: Path) -> None:
    output = resolve_output(tmp_path / "a" / "b" / "song.mp3", overwrite=False)

    assert output.parent.is_dir()


def test_existing_output_needs_overwrite_flag(tmp_path: Path) -> None:
    existing = tmp_path / "song_8d.mp3"
    existing.write_bytes(b"old")

    with pytest.raises(InputValidationError, match="--overwrite"):
        resolve_output(existing, overwrite=False)

    assert resolve_output(existing, overwrite=True) == existing.resolve()


def test_output_that_is_a_folder_is_rejected(tmp_path: Path) -> None:
    folder = tmp_path / "trap.mp3"
    folder.mkdir()

    with pytest.raises(InputValidationError, match="not a regular file"):
        resolve_output(folder, overwrite=True)


def test_input_and_output_cannot_be_the_same_file(tmp_path: Path) -> None:
    file_path = tmp_path / "song.mp3"
    file_path.write_bytes(b"audio")

    with pytest.raises(InputValidationError):
        ensure_different_files(file_path.resolve(), file_path.resolve())
