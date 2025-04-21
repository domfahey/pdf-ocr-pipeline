"""
PDF OCR Pipeline - Extract text from PDF documents using OCR.

A command-line tool and library to process PDF files through OCR
(Optical Character Recognition) and output the results as JSON.
Includes AI-powered analysis capabilities using OpenAI's GPT-4o.
"""

__version__ = "0.1.0"

# Public surface
from pathlib import Path
from typing import Optional, Union, cast

from .ocr import ocr_pdf
from .types import OcrResult, SegmentationResult

# Optional GPT helper retained
try:
    from .summarize import process_with_gpt  # noqa: F401 (re-export)
except ImportError:  # pragma: no cover – summarization extras not installed
    process_with_gpt = None  # type: ignore

from .segmentation import segment_pdf
from .settings import settings as _settings  # internal singleton


def process_pdf(
    path: Union[str, Path],
    *,
    analyze: bool = False,
    dpi: Optional[int] = None,
    lang: Optional[str] = None,
    prompt: Optional[str] = None,
    model: Optional[str] = None,
) -> Union[SegmentationResult, OcrResult]:
    """High‑level convenience wrapper combining OCR and optional analysis.

    Parameters
    ----------
    path:
        Path to the PDF file.
    analyze:
        When *True* the function sends the OCR result to the segmentation LLM
        and returns its JSON output.  When *False* only OCR is performed.
    dpi, lang, prompt, model:
        Override defaults from :pymod:`pdf_ocr_pipeline.settings`.
    """

    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    dpi_val = dpi or _settings.dpi
    lang_val = lang or _settings.lang

    ocr_text = ocr_pdf(pdf_path, dpi=dpi_val, lang=lang_val)

    if not analyze:
        return cast(OcrResult, {"file": pdf_path.name, "ocr_text": ocr_text})

    prompt_val: str = prompt or _settings.prompt

    seg_json = segment_pdf(ocr_text, prompt_val, model=model or "gpt-4o")

    return cast(SegmentationResult, seg_json)


__all__ = [
    "ocr_pdf",
    "process_pdf",
]

if process_with_gpt is not None:
    __all__.append("process_with_gpt")
