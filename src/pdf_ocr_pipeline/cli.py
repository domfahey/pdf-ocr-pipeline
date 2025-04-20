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
logger = logging.getLogger(__name__)


"""
Command-line interface entrypoint.
"""
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Parse arguments and perform OCR on one or more PDF files.
    Outputs a JSON array of {file, ocr_text} objects to stdout.
    """
    # Logging is configured at module load; adjust level based on verbosity

    # Configure detailed logging (default DEBUG)
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
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
    args = parser.parse_args()

    # Verbose flag is retained but default logging is already DEBUG
    if args.verbose:
        logger.debug("Verbose flag enabled (logging already at DEBUG level)")

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

        print(
            json.dumps(results, ensure_ascii=False, indent=2 if args.verbose else None)
        )

    except PipelineError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
