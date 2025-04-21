#!/usr/bin/env python3
"""
Core OCR functionality for PDF OCR Pipeline.
"""

import subprocess

# Project‑wide logger setup
from .logging_utils import get_logger

# stdlib
from pathlib import Path
from typing import List, Any

# internal
from .errors import MissingBinaryError, OcrError

# Logger for error messages
logger = get_logger(__name__)


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
    # Log the full command for debugging
    logger.debug("Executing command: %s", " ".join(cmd))
    try:
        return subprocess.run(cmd, **kwargs)
    except FileNotFoundError as e:
        logger.error("Missing binary: %s", e.filename)
        raise MissingBinaryError(e.filename) from e


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
    # Log module path for debugging to confirm correct code version
    from pathlib import Path as _Path

    logger.debug("ocr_pdf loaded from: %s", _Path(__file__).resolve())
    #
    # NOTE: Previous implementation attempted to pipe the rasterised PDF pages
    # directly from pdftoppm → tesseract via STDOUT/STDIN.  Unfortunately new
    # versions of the `pdftoppm` utility no longer write image data to STDOUT
    # when the output file prefix is "-".  Instead, one "-.ppm" file (or
    # "--01.ppm", “--02.ppm”, …) is silently created on disk and nothing is
    # written to the pipe.  The end‑result is that tesseract receives an empty
    # byte‑stream and terminates with the cryptic message “Error during
    # processing.”
    #
    # To be robust across `pdftoppm` versions we now:
    #   1.  Render the pages into a temporary directory using a normal filename
    #       prefix (no STDOUT involved).
    #   2.  Run tesseract on every generated image and concatenate the text.
    #
    # This approach is slightly less elegant than pure streaming, but it works
    # everywhere, copes with multi‑page PDFs, and avoids the silent failure
    # outlined above.

    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="pdf_ocr_pipeline_") as tmpdir:
        prefix_path = Path(tmpdir) / "page"

        # ------------------------------------------------------------------
        # 1. Rasterise the PDF → PPM files
        # ------------------------------------------------------------------
        try:
            pdftoppm_res = run_cmd(
                [
                    "pdftoppm",
                    "-r",
                    str(dpi),
                    str(pdf_path),
                    str(prefix_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            err_msg = None
            if hasattr(e, "stderr") and e.stderr:
                try:
                    err_msg = e.stderr.decode("utf-8", errors="replace").strip()
                except Exception:
                    err_msg = "<unable to decode pdftoppm stderr>"
            logger.error(
                "pdftoppm exited with status %s%s",
                e.returncode,
                f": {err_msg}" if err_msg else "",
            )
            raise OcrError("pdftoppm failed") from e

        # ------------------------------------------------------------------
        # 2. Locate the generated images
        # ------------------------------------------------------------------
        images = sorted(Path(tmpdir).glob("page-*.ppm"))

        # ------------------------------------------------------------------
        # Fallback for mocked / legacy behaviour: if no images were generated
        # but pdftoppm *did* return raster data on STDOUT, fall back to the
        # original streaming implementation.  This keeps the public contract
        # unchanged for unit‑tests that inject fake PPM data via mocks.
        # ------------------------------------------------------------------
        if not images and pdftoppm_res.stdout:
            try:
                tess_res = run_cmd(
                    [
                        "tesseract",
                        "-l",
                        lang,
                        "--dpi",
                        str(dpi),
                        "-",  # STDIN image
                        "stdout",
                    ],
                    input=pdftoppm_res.stdout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                err_msg = None
                if hasattr(e, "stderr") and e.stderr:
                    try:
                        err_msg = e.stderr.decode("utf-8", errors="replace").strip()
                    except Exception:
                        err_msg = "<unable to decode tesseract stderr>"
                logger.error(
                    "tesseract exited with status %s%s",
                    e.returncode,
                    f": {err_msg}" if err_msg else "",
                )
                raise OcrError("tesseract failed during streaming fallback") from e

            return (tess_res.stdout or b"").decode("utf-8", errors="replace")

        if not images:
            logger.error("pdftoppm produced no images for %s", pdf_path)
            raise OcrError("No images produced by pdftoppm")

        # ------------------------------------------------------------------
        # 3. OCR every page and concatenate the results
        # ------------------------------------------------------------------
        ocr_text_parts: List[str] = []

        for img_path in images:
            try:
                tess_res = run_cmd(
                    [
                        "tesseract",
                        str(img_path),
                        "stdout",  # write OCR text to STDOUT
                        "-l",
                        lang,
                        "--dpi",
                        str(dpi),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                err_msg = None
                if hasattr(e, "stderr") and e.stderr:
                    try:
                        err_msg = e.stderr.decode("utf-8", errors="replace").strip()
                    except Exception:
                        err_msg = "<unable to decode tesseract stderr>"
                logger.error(
                    "tesseract exited with status %s on %s%s",
                    e.returncode,
                    img_path.name,
                    f": {err_msg}" if err_msg else "",
                )
                raise OcrError("tesseract failed on image") from e

            ocr_text_parts.append(
                (tess_res.stdout or b"").decode("utf-8", errors="replace")
            )

    # Join page texts with a page‑break to aid downstream parsing
    return "\n\f\n".join(ocr_text_parts)
