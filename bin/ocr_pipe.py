#!/usr/bin/env python3
"""
Standalone script for PDF OCR Pipeline.
Provided for backward compatibility.

Usage:
    python ocr_pipe.py path/to/file1.pdf [path/to/file2.pdf ...] > output.json
"""

import sys
import os

# Add the parent directory to path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_ocr_pipeline.cli import main  # noqa: E402

if __name__ == "__main__":
    main()