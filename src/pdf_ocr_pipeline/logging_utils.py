"""Utility helpers for consistent logging setup across the project.

This centralises logger configuration so that *all* modules share the same
formatter/handler while still allowing command‑line entry points to tweak the
root log‑level via ``--verbose`` / ``--quiet`` flags.

Usage pattern
-------------
>>> from pdf_ocr_pipeline.logging_utils import get_logger
>>> logger = get_logger(__name__)

The *first* call to :func:`get_logger` configures the *root* logger with a
simple :class:`logging.StreamHandler`.  Subsequent calls merely return
``logging.getLogger(name)``.
"""

from __future__ import annotations

import logging
from typing import Final

_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s: %(message)s"
_DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"

# Flag so we only touch the root logger once.
_INITIALISED: bool = False


def _initialise_root_logger(level: int) -> None:
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

    root.setLevel(level)

    _INITIALISED = True


def get_logger(name: str, *, level: int | None = None) -> logging.Logger:  # noqa: D401
    """Return a module‑level logger with our global formatting applied.

    The *first* call will configure the root logger.  Additional calls simply
    retrieve the named logger.  A per‑logger *level* may be provided but is
    rarely necessary—prefer adjusting the root level instead.
    """

    # If the library is used programmatically root logging is silent except
    # for *warnings* and *errors*.  Command‑line tools then elevate the level
    # to INFO or DEBUG as requested by the user.
    default_level = logging.WARNING

    _initialise_root_logger(default_level)

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)

    return logger
