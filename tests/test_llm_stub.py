"""Test that llm_client.send integrates correctly with an HTTP stub.

This test uses *pytest‑httpx* when available to intercept the outbound network
call.  When the library is missing the test is skipped automatically so that
CI environments without the extra dependency remain green.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Any

import pytest


# Skip if pytest_httpx is not installed
pytest_httpx = pytest.importorskip("pytest_httpx")  # noqa: WPS433 (dynamic import)


# Ensure local src/ is imported first
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, ROOT)


from pdf_ocr_pipeline.llm_client import send  # noqa: E402


def test_send_with_httpx_stub(httpx_mock: "pytest_httpx.HTTPXMock") -> None:  # type: ignore[name-defined]
    """send() should parse the JSON returned by the mocked endpoint."""

    # Fake OpenAI environment variables so _get_client() constructs the URL we expect
    os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")

    # Match any request to the completions endpoint
    httpx_mock.add_response(
        json={"choices": [{"message": {"content": json.dumps({"foo": "bar"})}}]}
    )

    messages = [{"role": "user", "content": "ping"}]

    response: Dict[str, Any] = send(messages, client=None, model="gpt-3.5-turbo")

    assert response == {"foo": "bar"}
