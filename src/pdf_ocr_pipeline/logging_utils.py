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
    """
    Attaches a single StreamHandler with a consistent formatter to the root logger.
    
    Ensures the handler is only added once per interpreter session to prevent duplicate log lines, avoiding the use of logging.basicConfig. Does not modify the root logger's level.
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
    """
    Returns a logger with the specified name, ensuring global formatting is applied.
    
    On the first call, attaches a single global handler with consistent formatting to the root logger without modifying its level. If a level is provided, sets it on the returned logger instance. Prefer adjusting the root logger's level using `set_root_level` for consistent verbosity control across modules.
    
    Args:
        name: The name of the logger to retrieve.
        level: Optional log level to set on the returned logger.
    
    Returns:
        A logger instance with the specified name and global formatting.
    """

    # Ensure the global handler is attached.  Do not adjust root level here.
    _initialise_root_logger()

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger


def set_root_level(level: int) -> None:
    """
    Attaches the global logging handler if needed and sets the root logger's level.
    
    Args:
        level: The logging level to set for the root logger (e.g., logging.INFO).
    """
    # Attach handler if not already configured
    _initialise_root_logger()
    # Set root logger level
    logging.getLogger().setLevel(level)
