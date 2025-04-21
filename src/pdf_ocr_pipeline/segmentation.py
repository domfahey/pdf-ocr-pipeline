"""Simple wrapper around the LLM client to segment a PDF."""

from __future__ import annotations

from typing import Any, Dict, Optional


from .llm_client import send as llm_send


def segment_pdf(
    text: str,
    prompt: str,
    *,
    client: Optional[object] = None,
    model: str = "gpt-4o",
) -> Dict[str, Any]:
    """Return segmentation JSON for *text* using *prompt*.

    The implementation is intentionally minimal – real logic lives in the LLM.
    """

    messages = [
        {
            "role": "system",
            "content": "You segment multi‑page OCR text into separate real‑estate documents and return JSON.",
        },
        {"role": "user", "content": f"{prompt}\n\n{text}"},
    ]

    send_kwargs = {"model": model}
    if client is not None:
        send_kwargs["client"] = client  # type: ignore[arg-type]

    return llm_send(messages, **send_kwargs)  # type: ignore[return-value]
