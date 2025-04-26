"""
PDF OCR Pipeline - Extract text from PDF documents using OCR.

A command-line tool and library to process PDF files through OCR
(Optical Character Recognition) and output the results as JSON.
Includes AI-powered analysis capabilities using OpenAI's GPT-4o.
"""

__version__ = "0.1.0"

# Public surface
from pathlib import Path
import importlib
from typing import Union, cast

from .types import ProcessSettings, OcrResult, SegmentationResult
from .settings import settings as _settings  # internal singleton
from .ocr import ocr_pdf
from .segmentation import segment_pdf


def process_pdf(
    path: Union[str, Path],
    settings: ProcessSettings = ProcessSettings(),
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

    opts = settings  # local alias for brevity (does not shadow module)

    dpi_val = opts.dpi or _settings.dpi
    lang_val = opts.lang or _settings.lang

    ocr_text = ocr_pdf(pdf_path, dpi=dpi_val, lang=lang_val)

    if not opts.analyze:
        return cast(OcrResult, {"file": pdf_path.name, "ocr_text": ocr_text})

    # Only forward a prompt if the caller explicitly supplied one **and** it
    # is non‑empty.  Otherwise let *segment_pdf* fall back to its built‑in
    # template to avoid accidentally re‑using a generic summarization prompt
    # that may be present in ``settings.prompt`` (e.g. from a local INI file).

    prompt_val = opts.prompt or ""

    if prompt_val:
        prompt_arg = prompt_val
    else:
        prompt_arg = None  # let segment_pdf pick default template

    seg_json = segment_pdf(
        ocr_text,
        prompt_arg,
        model=opts.model or "gpt-4o",
    )

    return cast(SegmentationResult, seg_json)


def __getattr__(name: str):
    if name == "process_with_gpt":
        try:
            value = importlib.import_module(".summarize", __name__).process_with_gpt
        except ImportError:
            value = None  # summarization extras not installed
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    names = ["process_pdf", "ocr_pdf", "segment_pdf"]
    try:
        summarize = importlib.import_module(".summarize", __name__)
        if hasattr(summarize, "process_with_gpt"):
            names.append("process_with_gpt")
    except ImportError:
        pass
    return names[:]


__all__ = __dir__()[:]
