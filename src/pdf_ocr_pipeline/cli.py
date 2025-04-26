#!/usr/bin/env python3
"""
Command-line interface for PDF OCR Pipeline.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Local imports
from .logging_utils import get_logger, set_root_level
from .ocr import ocr_pdf
from .errors import PipelineError
from .types import OcrResult
from .settings import settings

try:
    from .config import _config
except ImportError:
    _config = {}

"""
Logging is configured at runtime to default to DEBUG level with detailed formatting.
"""
logger = get_logger(__name__)

LOG_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

"""
Command-line interface entrypoint.
"""
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Parse arguments and perform OCR on one or more PDF files.
    Outputs a JSON array of {file, ocr_text} objects to stdout.
    """
    # ------------------------------------------------------------------
    # CLI argument parsing
    # ------------------------------------------------------------------
    # Defaults pulled from typed settings
    default_dpi = settings.dpi
    default_lang = settings.lang
    default_verbose = settings.verbose
    parser = argparse.ArgumentParser(
        description="OCR PDF(s) to JSON on stdout",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "pdfs",
        nargs="+",
        type=Path,
        help="input PDF file(s)",
    )
    parser.add_argument(
        "--dpi", type=int, default=default_dpi, help="resolution for OCR"
    )
    parser.add_argument(
        "-l", "--lang", default=default_lang, help="tesseract language code"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=default_verbose,
        help="enable verbose output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="suppress informational output; only warnings and errors are shown",
    )
    parser.add_argument(
        "--log-level",
        choices=list(LOG_LEVELS.keys()),
        help="set root log level",
    )
    # ------------------------------------------------------------------
    # Apply logging level according to CLI flags
    # ------------------------------------------------------------------
    args = parser.parse_args()

    # Determine flags for logging, guard against mocks in tests
    log_level = args.log_level if args.log_level in LOG_LEVELS else None
    verbose = args.verbose if isinstance(args.verbose, bool) else False
    quiet = args.quiet if isinstance(args.quiet, bool) else False

    # Apply logging level according to CLI flags (--log-level supersedes verbose/quiet)
    if verbose and quiet:
        parser.error("--verbose and --quiet are mutually exclusive")
    if log_level and (verbose or quiet):
        parser.error("--log-level cannot be used with --verbose/--quiet")
    if log_level:
        set_root_level(LOG_LEVELS[log_level])
    elif quiet:
        set_root_level(logging.WARNING)
    elif verbose:
        set_root_level(logging.DEBUG)
        logger.debug("Verbose flag enabled – root log‑level set to DEBUG")

    try:
        # Check for file existence
        for pdf_path in args.pdfs:
            if not pdf_path.is_file():
                raise PipelineError(f"File not found: {pdf_path}")

        # ------------------------------------------------------------------
        # Parallel OCR
        # ------------------------------------------------------------------
        results: list[OcrResult] = []
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(ocr_pdf, pdf_path, args.dpi, args.lang): pdf_path
                for pdf_path in args.pdfs
            }

            completed = {}
            for future in as_completed(futures):
                pdf_path = futures[future]
                try:
                    text = future.result()
                    completed[pdf_path] = {
                        "file": pdf_path.name,
                        "ocr_text": text,
                    }
                except PipelineError as exc:
                    logger.error("Error processing %s: %s", pdf_path, exc)
                    completed[pdf_path] = {
                        "file": pdf_path.name,
                        "error": str(exc),
                    }
                except Exception as e:
                    logger.error("Error processing %s: %s", pdf_path, e)
                    completed[pdf_path] = {"file": pdf_path.name, "error": str(e)}

            for pdf_path in args.pdfs:
                results.append(completed[pdf_path])

        # Emit JSON to stdout.
        # If the downstream pipe closes early (e.g. `| head`), writing to
        # stdout raises BrokenPipeError.  Treat that as a normal termination
        # and exit silently.
        import contextlib

        with contextlib.suppress(BrokenPipeError):
            print(
                json.dumps(
                    results, ensure_ascii=False, indent=2 if args.verbose else None
                )
            )

    except PipelineError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
