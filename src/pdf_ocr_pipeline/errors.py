"""Common exception hierarchy for PDF‑OCR‑Pipeline.

Library code (functions that other modules call) should *raise* these custom
exceptions instead of calling :pyfunc:`sys.exit`.  The CLI entry points can
catch :class:`PipelineError` at the top‑level and exit with a non‑zero status
code, preserving the existing user‑facing behaviour while making the library
usable programmatically and easier to test.
"""

from __future__ import annotations


class PipelineError(Exception):
    """Base‑class for all custom exceptions raised by this package."""


class MissingBinaryError(PipelineError):
    """Required external command (e.g. *tesseract*) not found on *PATH*."""


class OcrError(PipelineError):
    """pdftoppm or tesseract failed when processing a document."""


class LlmError(PipelineError):
    """Errors returned from or triggered while calling the language model API."""
