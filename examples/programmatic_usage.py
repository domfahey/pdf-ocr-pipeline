#!/usr/bin/env python3
"""
Example showing how to use the PDF OCR Pipeline programmatically.
"""

import sys
import json
from pathlib import Path

# Add the project directory to the Python path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_ocr_pipeline import ocr_pdf  # noqa: E402


def process_pdf(pdf_path: str, dpi: int = 300, lang: str = "eng") -> dict:
    """
    Process a PDF file and return the results as a dictionary.

    Args:
        pdf_path: Path to the PDF file
        dpi: Resolution for OCR processing
        lang: Language code for Tesseract

    Returns:
        Dictionary with file name and OCR text
    """
    path_obj = Path(pdf_path)

    if not path_obj.is_file():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    text = ocr_pdf(path_obj, dpi=dpi, lang=lang)

    return {
        "file": path_obj.name,
        "ocr_text": text,
    }


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
