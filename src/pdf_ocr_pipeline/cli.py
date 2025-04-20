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

# Configure basic logging for library and CLI use
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
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
    parser.add_argument("--dpi", type=int, default=300, help="resolution for OCR")
    parser.add_argument("-l", "--lang", default="eng", help="tesseract language code")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose output"
    )
    args = parser.parse_args()

    # Configure verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # Check for file existence
    for pdf_path in args.pdfs:
        if not pdf_path.is_file():
            logger.error("File not found: %s", pdf_path)
            sys.exit(1)

    # Process files concurrently, but preserve input order in results
    results = []
    # Submit OCR tasks
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(ocr_pdf, pdf_path, args.dpi, args.lang): pdf_path
            for pdf_path in args.pdfs
        }
        # Collect results in completion order, then reorder
        completed = {}
        for future in as_completed(futures):
            pdf_path = futures[future]
            try:
                text = future.result()
                completed[pdf_path] = {"file": pdf_path.name, "ocr_text": text}
            except SystemExit:
                # Missing binary is fatal
                raise
            except Exception as e:
                logger.error("Error processing %s: %s", pdf_path, e)
                completed[pdf_path] = {"file": pdf_path.name, "error": str(e)}
        # Preserve original order
        for pdf_path in args.pdfs:
            results.append(completed[pdf_path])

    # Output results as JSON array
    print(json.dumps(results, ensure_ascii=False, indent=2 if args.verbose else None))


if __name__ == "__main__":
    main()
