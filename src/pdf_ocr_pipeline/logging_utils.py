"""Utility helpers for consistent logging setup across the project.

This centralises logger configuration so that *all* modules share the same
formatter/handler while still allowing command‑line entry points to tweak the
root log‑level via ``--verbose`` / ``--quiet`` flags.

Usage pattern
-------------
>>> from pdf_ocr_pipeline.logging_utils import get_logger, set_root_level
>>> logger = get_logger(__name__)

The *first* call to :func:`get_logger` attaches a single
:class:`logging.StreamHandler` to the root logger (if not already added),
but does *not* adjust the root logger's level.  To change the logging
verbosity use :func:`set_root_level` (e.g. from a CLI entry point).
"""

from __future__ import annotations

import logging
from typing import Final

_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s: %(message)s"
_DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Flag so we only touch the root logger once.
_INITIALISED: bool = False


def _initialise_root_logger() -> None:
    """Attach a single *StreamHandler* to the root logger.

    The handler is only added once per interpreter session.  We deliberately do
    **not** rely on :pyfunc:`logging.basicConfig` because re‑invoking it from
    multiple modules is a common source of duplicate log lines.
    """

    global _INITIALISED  # noqa: WPS420 (module‑level state is fine here)

    if _INITIALISED:
        return

    root = logging.getLogger()

    # Avoid attaching a second handler in interactive / test sessions where
    # another library may already have configured logging.
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))
        root.addHandler(handler)

    # Do not adjust root level here; leave it to set_root_level

    _INITIALISED = True


def get_logger(name: str, *, level: int | None = None) -> logging.Logger:  # noqa: D401
    """Return a module-level logger with our global formatting applied.

    The first call will attach the global handler to the root logger
    (without changing its level). Subsequent calls simply retrieve the
    named logger. A per-logger *level* may be provided but is rarely
    necessary—prefer using :func:`set_root_level` to adjust verbosity.
    """

    # Ensure the global handler is attached.  Do not adjust root level here.
    _initialise_root_logger()

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def set_root_level(level: int) -> None:
    """Ensure the global handler is attached and set the root logger level."""
    # Attach handler if not already configured
    _initialise_root_logger()
    # Set root logger level
    logging.getLogger().setLevel(level)
