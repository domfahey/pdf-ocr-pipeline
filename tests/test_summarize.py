#!/usr/bin/env python3
"""Unit tests for the LLM summarisation helpers (post‑abstraction)."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Any
from unittest.mock import MagicMock, patch


# Ensure local src/ is imported
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)  # type: ignore


from pdf_ocr_pipeline.summarize import (  # noqa: E402  (import after path tweak)
    process_with_gpt,
    main as summarize_main,
)


class TestSummarize:
    """High‑level unit‑tests for summarisation pipeline."""

    def setup_method(self):  # noqa: D401 (pytest style)
        # Patch llm_client.send to avoid real network calls
        send_patcher = patch("pdf_ocr_pipeline.summarize.llm_send")
        self.mock_send = send_patcher.start()
        self._send_patcher = send_patcher

        # Provide a default JSON response so individual tests can override
        self.mock_send.return_value = {
            "summary": "Test summary",
            "key_points": ["Point 1", "Point 2"],
        }

        # Patch logger to keep output clean
        logger_patcher = patch("pdf_ocr_pipeline.summarize.logger")
        self.mock_logger = logger_patcher.start()
        self._logger_patcher = logger_patcher

        # Patch deprecated setup_openai_client to avoid real client creation
        client_patcher = patch(
            "pdf_ocr_pipeline.summarize.setup_openai_client", return_value=MagicMock()
        )
        self._client_patcher = client_patcher
        client_patcher.start()

    def teardown_method(self):  # noqa: D401 (pytest style)
        self._send_patcher.stop()
        self._logger_patcher.stop()
        self._client_patcher.stop()

    # ------------------------------------------------------------------
    # Direct helper tests
    # ------------------------------------------------------------------

    def test_process_with_gpt_success(self):
        """process_with_gpt should forward to llm_client.send and return its value."""

        result = process_with_gpt(None, "Some OCR text", "Summarise")

        self.mock_send.assert_called_once()
        assert result["summary"] == "Test summary"

    def test_process_with_gpt_error_passthrough(self):
        """Errors returned by the client are passed through unchanged."""

        self.mock_send.return_value = {"error": "Boom"}

        result = process_with_gpt(None, "Text", "Prompt")

        assert result == {"error": "Boom"}

    # ------------------------------------------------------------------
    # CLI pipeline
    # ------------------------------------------------------------------

    def test_cli_json_roundtrip(self, monkeypatch):  # noqa: D401 (pytest fixture param)
        """Full CLI round‑trip with mocked LLM call."""

        input_payload = [
            {"file": "input.pdf", "ocr_text": "Hello world"},
        ]

        monkeypatch.setattr(sys, "argv", ["summarize", "--pretty"])
        import io

        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(input_payload)))

        printed: Dict[str, Any] = {}

        def fake_print(arg):  # noqa: D401 (inner helper)
            printed["data"] = json.loads(arg)

        monkeypatch.setattr("builtins.print", fake_print)

        summarize_main()

        # Ensure mocked send called & output propagated
        self.mock_send.assert_called_once()

        assert printed["data"][0]["file"] == "input.pdf"
        assert printed["data"][0]["analysis"]["summary"] == "Test summary"
