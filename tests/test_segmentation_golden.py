"""Golden JSON contract test for PDF segmentation helper."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from unittest.mock import patch

# Ensure local src first
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, ROOT)


from pdf_ocr_pipeline.segmentation import segment_pdf  # noqa: E402


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_segmentation_matches_golden():
    """LLM output should match the expected JSON structure for given text."""

    ocr_text = "(dummy OCR text)"

    golden_path = FIXTURE_DIR / "segmentation_golden.json"
    expected = json.loads(golden_path.read_text())

    # Mock llm_client.send to return the golden payload
    with patch(
        "pdf_ocr_pipeline.segmentation.llm_send", return_value=expected
    ) as mock_send:
        result = segment_pdf(ocr_text, "Prompt")

    mock_send.assert_called_once()

    assert result == expected
