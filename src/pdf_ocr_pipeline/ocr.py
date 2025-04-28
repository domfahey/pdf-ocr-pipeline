#!/usr/bin/env python3
"""
Core OCR functionality for PDF OCR Pipeline.
"""

import subprocess

# Project‑wide logger setup
from .logging_utils import get_logger

# stdlib

from pathlib import Path
from typing import List, Any, Tuple, Union

# internal
import shutil
import sys

from .errors import MissingBinaryError, OcrError

# Logger for error messages
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Force streaming disabled to avoid silent failures with pdftoppm → tesseract piping.
# Always use the temporary‑file fallback path for robustness.
# ---------------------------------------------------------------------------
_STREAMING_SUPPORTED: bool = False

# ---------------------------------------------------------------------------
# Early binary availability check (skipped under *pytest* to keep tests fast)
# ---------------------------------------------------------------------------

_REQUIRED_BINARIES = ("pdftoppm", "tesseract")

if "pytest" not in sys.modules:  # pragma: no cover – binary checking disabled in tests
    for _bin in _REQUIRED_BINARIES:
        if shutil.which(_bin) is None:
            raise MissingBinaryError(_bin)


def _detect_streaming_support() -> bool:  # noqa: WPS231 (complex – small helper)
    """Return ``True`` if *pdftoppm* can emit PPM data to STDOUT.

    Strategy
    --------
    1. Create an in‑memory 1‑page, 1×1‑pixel PDF (a few bytes).
    2. Invoke ``pdftoppm`` with output prefix ``-`` (means *write to STDOUT*).
    3. If any bytes are produced on *stdout* we assume streaming is supported.

    The call is wrapped in ``try/except`` so that missing binaries or timeouts
    degrade gracefully – we fall back to the safer *temp‑file* code path.
    """

    import subprocess
    import tempfile
    import textwrap

    minimal_pdf = textwrap.dedent(
        """
        %PDF-1.1
        1 0 obj<<>>endobj
        trailer<<>>
        %%EOF
        """
    ).encode()

    with tempfile.TemporaryDirectory(prefix="pdf_ocr_probe_") as tmpdir:
        probe_path = Path(tmpdir) / "probe.pdf"
        try:
            probe_path.write_bytes(minimal_pdf)
        except Exception:  # pragma: no cover – extremely unlikely
            return False

        try:
            result = subprocess.run(
                [
                    "pdftoppm",
                    "-r",
                    "10",
                    str(probe_path),
                    "-",  # write PPM to STDOUT if supported
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
        except (FileNotFoundError, subprocess.SubprocessError):  # noqa: PERF203
            # Missing binary or other execution error → assume *no* streaming.
            return False

    return bool(result.stdout)


def run_cmd(
    cmd: List[str | Path | bytes],
    *,
    ok_exit_codes: Tuple[int, ...] = (0,),
    capture_output: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Run *cmd* and return the :class:`~subprocess.CompletedProcess`.

    Improvements compared to a bare :pyfunc:`subprocess.run` call:

    1. *stderr* is captured by default so that callers can inspect / log it
       without having to set ``stderr=subprocess.PIPE`` every time.
    2. Accepts *ok_exit_codes* – a tuple of return codes that are considered
       successful (defaults to ``(0,)``).
    3. On *FileNotFoundError* raises :class:`MissingBinaryError` for early
       detection.
    4. On unexpected exit code raises :class:`subprocess.CalledProcessError`
       with captured *stdout* / *stderr* so that the caller can decide how to
       handle the failure.
    """

    # Log the full command for debugging
    logger.debug("Executing command: %s", " ".join(map(str, cmd)))

    # Configure default I/O capturing **unless** the caller overrode them.
    if capture_output:
        kwargs.setdefault("stdout", subprocess.PIPE)
        kwargs.setdefault("stderr", subprocess.PIPE)

    # We handle exit‑code ourselves; always run with ``check=False``.
    kwargs["check"] = False

    try:
        proc = subprocess.run(cmd, **kwargs)
    except FileNotFoundError as exc:
        logger.error("Missing binary: %s", exc.filename)
        raise MissingBinaryError(exc.filename) from exc

    if proc.returncode not in ok_exit_codes:
        # Decode stderr for friendlier message but keep raw bytes in exception.
        stderr_decoded: Union[str, None]
        try:
            stderr_decoded = (
                proc.stderr.decode("utf-8", errors="replace") if proc.stderr else None
            )
        except Exception:  # pragma: no cover – decoding should always succeed
            stderr_decoded = None

        logger.debug(
            "Command %s returned %s (stderr: %s)",
            " ".join(map(str, cmd)),
            proc.returncode,
            stderr_decoded or "<empty>",
        )

        raise subprocess.CalledProcessError(
            returncode=proc.returncode,
            cmd=cmd,
            output=proc.stdout,
            stderr=proc.stderr,
        )

    return proc


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

    global _STREAMING_SUPPORTED

    if _STREAMING_SUPPORTED is None:
        _STREAMING_SUPPORTED = _detect_streaming_support()
        logger.debug(
            "pdftoppm streaming support detected: %s",
            "yes" if _STREAMING_SUPPORTED else "no",
        )

    if _STREAMING_SUPPORTED:
        # --------------------------------------------------------------
        # Fast path: pipe rasterised pages directly to tesseract.
        # --------------------------------------------------------------
        try:
            pdftoppm_res = run_cmd(
                [
                    "pdftoppm",
                    "-r",
                    str(dpi),
                    str(pdf_path),
                    "-",  # write PPM to STDOUT
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

        # No need to check images; hand off to tesseract directly.
        if not pdftoppm_res.stdout:
            # Unexpected – fallback to temp‑file path.
            logger.debug("pdftoppm produced no stdout, falling back to temp‑file path")
            _STREAMING_SUPPORTED = False  # cache so we don't retry every time
            # continue to temp‑file workflow below
        else:
            try:
                tess_res = run_cmd(
                    [
                        "tesseract",
                        "-l",
                        lang,
                        "--dpi",
                        str(dpi),
                        "-",  # stdin
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
                raise OcrError("tesseract failed during streaming path") from e

            return (tess_res.stdout or b"").decode("utf-8", errors="replace")

    # ------------------------------------------------------------------
    # Safe fallback: rasterise into a temporary directory first.
    # ------------------------------------------------------------------
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="pdf_ocr_pipeline_") as tmpdir:
        prefix_path = Path(tmpdir) / "page"

        # 1. Rasterise
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

        images = sorted(Path(tmpdir).glob("page-*.ppm"))

        # streaming fallback for mocks / legacy behaviour
        if not images and pdftoppm_res.stdout:
            try:
                tess_res = run_cmd(
                    [
                        "tesseract",
                        "-l",
                        lang,
                        "--dpi",
                        str(dpi),
                        "-",
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

            # Wrap single-page output in tags
            text = (tess_res.stdout or b"").decode("utf-8", errors="replace")
            return f"<page number 1>\n{text}\n</page number 1>"

        if not images:
            logger.error("pdftoppm produced no images for %s", pdf_path)
            raise OcrError("No images produced by pdftoppm")

        # 3. OCR every page and concatenate the results
        ocr_text_parts: List[str] = []

        for img_path in images:
            try:
                tess_res = run_cmd(
                    [
                        "tesseract",
                        str(img_path),
                        "stdout",
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

    # Wrap each page's OCR text in page-number tags
    pages: List[str] = []
    for idx, part in enumerate(ocr_text_parts, start=1):
        pages.append(f"<page number {idx}>\n{part}\n</page number {idx}>")
    return "\n".join(pages)
