#!/usr/bin/env python3
"""Thin wrapper CLI kept for backward‑compatibility.

It simply delegates to ``pdf_ocr_pipeline.cli.main`` so that existing shell
scripts calling ``bin/ocr_pipe.py`` continue to work after the packaging
re‑organisation.
"""

from pdf_ocr_pipeline.cli import main


if __name__ == "__main__":  # pragma: no cover
    main()
