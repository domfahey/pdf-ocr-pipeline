#!/usr/bin/env python3
"""
Main entry point for running the package as a module.
Allows running with `python -m pdf_ocr_pipeline`.
"""

from .cli import main

if __name__ == "__main__":
    main()
