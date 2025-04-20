#!/usr/bin/env python3
"""
Core OCR functionality for PDF OCR Pipeline.
"""

import subprocess
import sys
import logging
from pathlib import Path
from typing import List, Any

# Logger for error messages
logger = logging.getLogger(__name__)


def run_cmd(cmd: List[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """
    Run a subprocess command, exiting if the executable is not found.

    Args:
        cmd: List of command arguments.
        **kwargs: Additional options for subprocess.run.

    Returns:
        subprocess.CompletedProcess: The completed process result.

    Exits:
        1 if the executable is not found.
    """
    try:
        return subprocess.run(cmd, **kwargs)
    except FileNotFoundError as e:
        logger.error("Missing binary: %s", e.filename)
        sys.exit(1)


def ocr_pdf(pdf_path: Path, dpi: int = 300, lang: str = "eng") -> str:
    """
    Perform OCR on a PDF file using pdftoppm and tesseract.

    Args:
        pdf_path: Path of the PDF file to process.
        dpi: Resolution in DPI for conversion and OCR.
        lang: Tesseract language code.

    Returns:
        The recognized text as a Unicode string.

    Exits:
        1 if pdftoppm or tesseract fails.
    """
    # Convert PDF to PPM image stream
    try:
        ppm = run_cmd(
            ["pdftoppm", "-r", str(dpi), str(pdf_path), "-"],
            stdout=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error("pdftoppm exited with non-zero status")
        sys.exit(e.returncode)

    if ppm.stdout is None:
        logger.error("Failed to capture stdout from pdftoppm")
        sys.exit(1)

    # Run Tesseract OCR on image data
    try:
        tess = run_cmd(
            ["tesseract", "stdin", "stdout", "-l", lang, "--dpi", str(dpi)],
            input=ppm.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error("tesseract exited with non-zero status")
        sys.exit(e.returncode)

    text_bytes = tess.stdout or b""
    return text_bytes.decode("utf-8", errors="replace")
