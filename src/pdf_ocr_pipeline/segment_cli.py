"""CLI tool to run the segmentation LLM on OCR text coming from *stdin*.

Typical usage – chain after the OCR CLI:

    python -m pdf_ocr_pipeline <file.pdf> | pdf-ocr-segment --pretty > segments.json

The program expects ``stdin`` to contain either raw text or the JSON array that
is produced by :pymod:`pdf_ocr_pipeline.cli`.  For each document object it will
invoke :func:`pdf_ocr_pipeline.segmentation.segment_pdf` and print the list of
results to *stdout*.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from .logging_utils import get_logger
from .segmentation import segment_pdf
from .settings import settings

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_input() -> List[Dict[str, Any]]:
    """Read JSON array or raw text from *stdin*.

    Returns a list of ``{"file": ..., "ocr_text": ...}`` dictionaries.
    """

    raw = sys.stdin.read().strip()
    if not raw:
        logger.error("No input data detected on stdin – aborting")
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Not JSON – treat entire stdin content as one OCR blob
        return [{"file": "unknown", "ocr_text": raw}]

    if isinstance(data, list):
        return data  # assume correct shape; downstream code will validate

    # Non‑list JSON – wrap into expected structure
    return [{"file": "unknown", "ocr_text": json.dumps(data)}]


# ---------------------------------------------------------------------------
# Main entry‑point
# ---------------------------------------------------------------------------


def main() -> None:  # noqa: WPS231 – CLI assembly is inevitably imperative
    """Segment OCR text(s) read from *stdin* and emit JSON to *stdout*."""

    default_verbose = settings.verbose
    default_prompt = None  # let segment_pdf load bundled template unless user overrides
    default_pretty = bool(getattr(settings, "pretty", False))

    parser = argparse.ArgumentParser(
        description="Segment OCR text using the built‑in real‑estate prompt",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--prompt",
        default=default_prompt,
        help="Custom segmentation prompt template (rarely needed)",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        default=default_pretty,
        help="Pretty‑print JSON output",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=default_verbose,
        help="Enable verbose / debug logging",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress info logging (warnings & errors only)",
    )

    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Configure root logger according to flags
    # ------------------------------------------------------------------

    root = logging.getLogger()

    if args.verbose and args.quiet:  # pragma: no cover – guarded by argparse
        parser.error("--verbose and --quiet cannot be used together")

    if args.quiet:
        root.setLevel(logging.WARNING)
    elif args.verbose:
        root.setLevel(logging.DEBUG)
        logger.debug("Verbose flag enabled – root log‑level set to DEBUG")

    # ------------------------------------------------------------------
    # Process stdin input
    # ------------------------------------------------------------------

    documents = _read_input()
    logger.debug("Processing %s input document(s)", len(documents))

    results: List[Dict[str, Any]] = []

    for doc in documents:
        file_name = doc.get("file", "unknown")
        text = doc.get("ocr_text", "")

        if not text:
            logger.warning("Empty OCR text for file: %s – skipping", file_name)
            continue

        logger.info("Segmenting OCR text from: %s", file_name)

        seg_json = segment_pdf(text, prompt=args.prompt)

        results.append({"file": file_name, "segmentation": seg_json})

    indent: Optional[int] = 2 if args.pretty else None
    print(json.dumps(results, ensure_ascii=False, indent=indent))


if __name__ == "__main__":  # pragma: no cover
    main()
