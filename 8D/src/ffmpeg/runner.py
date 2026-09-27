# Developed by ::> Gehan Fernando
"""Runs external tools safely and turns failures into Audio8D errors."""

import os
import subprocess
import threading
from collections.abc import Callable, Sequence
from typing import TypeVar

from ..core.errors import Audio8DError, ConversionError

ErrorT = TypeVar("ErrorT", bound=Audio8DError)

# Stops a black console flashing up for every FFmpeg run when the window is used
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0

# Called with the share of the work done so far, from 0.0 to 1.0
ProgressCallback = Callable[[float], None]


def run_tool(
    command: Sequence[str], *, keep_stdout: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a tool without a shell and return its text output, whatever its exit code."""
    # shell=False means a song's file name can never be run as a shell command
    return subprocess.run(
        list(command),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE if keep_stdout else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        shell=False,
        creationflags=NO_WINDOW,
    )


def run_capture(
    command: Sequence[str],
    *,
    error_type: type[ErrorT],
) -> subprocess.CompletedProcess[str]:
    """Run a command without a shell and return its captured text output."""
    try:
        result = run_tool(command)
    except OSError as exc:
        raise error_type(f"Failed to start {command[0]!r}: {exc}") from exc

    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise error_type(
            f"Command failed with exit code {result.returncode}: {details}"
        )

    return result


def run_binary(command: Sequence[str], *, error_type: type[ErrorT]) -> bytes:
    """Run a tool and return its raw stdout bytes (for decoded audio samples)."""
    try:
        result = subprocess.run(
            list(command),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            shell=False,
            creationflags=NO_WINDOW,
        )
    except OSError as exc:
        raise error_type(f"Failed to start {command[0]!r}: {exc}") from exc
    if result.returncode != 0:
        details = result.stderr.decode("utf-8", "replace").strip() or "unknown error"
        raise error_type(
            f"Command failed with exit code {result.returncode}: {details}"
        )
    return result.stdout


def _progress_value(line: str, duration: float) -> float | None:
    """The share done, from one `-progress` line such as 'out_time_us=1234567'."""
    key, _, value = line.strip().partition("=")
    if key not in {"out_time_us", "out_time_ms"} or not value.lstrip("-").isdigit():
        return None
    # Despite its name, out_time_ms is in microseconds too
    seconds = int(value) / 1_000_000
    return max(0.0, min(1.0, seconds / duration))


def run_ffmpeg(
    command: Sequence[str],
    *,
    duration: float | None,
    on_progress: ProgressCallback | None = None,
    cancel: threading.Event | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run FFmpeg, reporting progress as it goes; the command gets -progress added.

    Returns the finished process (stdout is empty; stderr holds FFmpeg's log).
    """
    if on_progress is None and cancel is None:
        return run_tool(command, keep_stdout=False)

    # -progress writes "key=value" lines to stdout, which we read as they arrive
    full = [command[0], "-progress", "pipe:1", "-nostats", *command[1:]]
    try:
        process = subprocess.Popen(  # pylint: disable=consider-using-with
            full,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            creationflags=NO_WINDOW,
        )
    except OSError as exc:
        raise ConversionError(f"Failed to start {command[0]!r}: {exc}") from exc
    # Read the log on its own thread so a chatty FFmpeg can never fill the pipe
    log: list[str] = []
    reader = threading.Thread(
        target=lambda: log.append(process.stderr.read() if process.stderr else ""),
        daemon=True,
    )
    reader.start()
    try:
        assert process.stdout is not None
        for line in process.stdout:
            if cancel is not None and cancel.is_set():
                process.terminate()
                break
            if on_progress is not None and duration:
                share = _progress_value(line, duration)
                if share is not None:
                    on_progress(share)
        process.wait()
    except BaseException:
        # Ctrl+C or any other stop: never leave FFmpeg running in the background
        process.kill()
        process.wait()
        raise
    finally:
        reader.join(timeout=5)
    if cancel is not None and cancel.is_set():
        raise ConversionError("Conversion cancelled by user")
    if on_progress is not None and process.returncode == 0:
        on_progress(1.0)
    return subprocess.CompletedProcess(full, process.returncode, "", "".join(log))
