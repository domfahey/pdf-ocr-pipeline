"""
PDF OCR Pipeline - Extract text from PDF documents using OCR.

A command-line tool and library to process PDF files through OCR
(Optical Character Recognition) and output the results as JSON.
Includes AI-powered analysis capabilities using OpenAI's GPT-4o.
"""

__version__ = "0.1.0"

from .ocr import ocr_pdf

# Optional AI-powered analysis; requires OpenAI library
try:
    from .summarize import process_with_gpt
except ImportError:
    process_with_gpt = None  # type: ignore

__all__ = ["ocr_pdf"]
if process_with_gpt is not None:
    __all__.append("process_with_gpt")
