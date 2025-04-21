"""End‑to‑end integration test that exercises the full OCR → LLM pipeline.

The test is *conditionally* executed only when a valid ``OPENAI_API_KEY`` is
present in the environment.  This prevents automated CI pipelines without
network credentials from making outbound requests while allowing developers
to run a real‑world check locally:

    $ export OPENAI_API_KEY="sk‑…"
    $ pytest -q tests/test_end_to_end_llm.py

The test intentionally keeps the prompt and input extremely small to minimise
latency and token usage.  It asserts that the LLM returns valid JSON.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Any

import pytest

# Ensure local source tree is imported instead of any globally installed version
ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

from pdf_ocr_pipeline.ocr import ocr_pdf  # noqa: E402
from pdf_ocr_pipeline.summarize import (  # noqa: E402
    setup_openai_client,
    process_with_gpt,
)


# ---------------------------------------------------------------------------
# Skip test automatically if no API key available (default CI behaviour)
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not configured"
)


def test_end_to_end_llm(tmp_path: Path) -> None:
    """Run OCR on a sample PDF and feed the result to the real LLM."""

    sample_pdf = Path(__file__).parent / "fixtures" / "test_scanned.pdf"

    # 1. OCR — use low DPI to speed up (input file is tiny)
    ocr_text: str = ocr_pdf(sample_pdf, dpi=600, lang="eng")
    assert ocr_text.strip(), "OCR returned empty text"

    # 2. LLM call — use a *very* small prompt to save tokens
    prompt = "Return the first three words of the text as JSON array under key 'words'."

    client = setup_openai_client()

    response: Dict[str, Any] = process_with_gpt(
        client, ocr_text, prompt, model="gpt-3.5-turbo"
    )  # type: ignore[arg-type]

    # Should be valid JSON object with the key 'words'
    assert isinstance(response, dict), "LLM did not return a JSON object"
    assert "words" in response, "Expected key 'words' missing in response"

    # Basic sanity: list of strings
    words = response["words"]
    assert isinstance(words, list) and all(
        isinstance(w, str) for w in words
    ), "'words' should be list[str]"

    # At least one word returned
    assert words, "LLM returned empty word list"
