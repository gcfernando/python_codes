# Developed by Gehan Fernando
"""The technical log file, and hooks that record any crash before it is lost."""

import logging
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .core.locations import log_file

LOG = logging.getLogger("audio8d")

_FORMAT = "%(asctime)s %(levelname)s %(threadName)s %(name)s: %(message)s"


def start_log_file() -> Path | None:
    """Write DEBUG and up to the log file; None when the file can't be opened."""
    root = logging.getLogger()
    for handler in root.handlers:
        if getattr(handler, "audio8d_file", False):
            return Path(handler.baseFilename)  # type: ignore[attr-defined]
    path = log_file()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(
            path, maxBytes=1_000_000, backupCount=2, encoding="utf-8", delay=True
        )
    except OSError:
        # A read-only or missing profile folder must never stop the app itself
        return None
    handler.audio8d_file = True  # type: ignore[attr-defined]
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(_FORMAT))
    root.addHandler(handler)
    if root.level > logging.INFO:
        root.setLevel(logging.INFO)
    _catch_crashes()
    return path


def _catch_crashes() -> None:
    """Log errors nobody caught, on the main thread and on helper threads."""
    # Each hook passes the error on, so other tools' hooks keep working too
    if not getattr(sys.excepthook, "audio8d", False):
        previous = sys.excepthook

        def on_crash(kind, error, trace) -> None:  # type: ignore[no-untyped-def]
            if not issubclass(kind, KeyboardInterrupt):
                LOG.critical("Unexpected error", exc_info=(kind, error, trace))
            previous(kind, error, trace)

        on_crash.audio8d = True  # type: ignore[attr-defined]
        sys.excepthook = on_crash

    if not getattr(threading.excepthook, "audio8d", False):
        previous_thread_hook = threading.excepthook

        def on_thread_crash(args: threading.ExceptHookArgs) -> None:
            where = args.thread.name if args.thread else "a helper thread"
            LOG.critical("Unexpected error in %s", where, exc_info=args.exc_value)
            previous_thread_hook(args)

        on_thread_crash.audio8d = True  # type: ignore[attr-defined]
        threading.excepthook = on_thread_crash
