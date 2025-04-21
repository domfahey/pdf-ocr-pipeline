"""Unit tests for high‑level process_pdf helper."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch


from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings


SAMPLE_PDF = Path(__file__).parent / "fixtures" / "test_scanned.pdf"


def test_process_pdf_ocr_only():
    """process_pdf should return OcrResult when analyze=False."""

    with patch("pdf_ocr_pipeline.ocr_pdf", return_value="TEXT") as mock_ocr:
        result = process_pdf(SAMPLE_PDF, settings=ProcessSettings(analyze=False))

    mock_ocr.assert_called_once()
    assert result["file"] == SAMPLE_PDF.name
    assert result["ocr_text"] == "TEXT"


def test_process_pdf_with_analysis():
    """process_pdf should call segmentation when analyze=True."""

    fake_seg: Dict[str, Any] = {"documents": [], "total_pages": 0}

    with (
        patch("pdf_ocr_pipeline.ocr_pdf", return_value="TEXT") as mock_ocr,
        patch("pdf_ocr_pipeline.segment_pdf", return_value=fake_seg) as mock_seg,
    ):
        result = process_pdf(SAMPLE_PDF, settings=ProcessSettings(analyze=True))

    mock_ocr.assert_called_once()
    mock_seg.assert_called_once()
    assert result is fake_seg
