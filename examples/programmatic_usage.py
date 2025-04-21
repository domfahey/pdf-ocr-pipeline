#!/usr/bin/env python3
"""
Example showing how to use the PDF OCR Pipeline programmatically.
"""

import sys
import json
from pathlib import Path

# Add the project directory to the Python path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_ocr_pipeline import process_pdf  # noqa: E402


# Note: examples kept minimal; process_pdf already includes OCR and optional
# segmentation when ``analyze=True``.


def main():
    """
    Process sample PDF files and output results.
    """
    # Process a sample PDF
    sample_pdf = "../test_scanned.pdf"  # Update this path to point to your PDF

    try:
        print(f"Processing {sample_pdf}...")
        result = process_pdf(sample_pdf, dpi=300, lang="eng")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("Processing complete!")
    except Exception as e:
        print(f"Error processing PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
