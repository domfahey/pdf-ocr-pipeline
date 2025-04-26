"""Simple wrapper around the LLM client to segment a PDF."""

from __future__ import annotations

from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Public helper *segment_pdf* relies on the shared OpenAI wrapper in
# *llm_client*.  We keep imports local to avoid pulling heavy dependencies at
# module import time when the function is never called (common in pure‑OCR
# workflows).
# ---------------------------------------------------------------------------

from .llm_client import send as llm_send
from .settings import settings

# Cache the template so we only read the resource file once even when
# *segment_pdf* is invoked multiple times within the same process.
_DEFAULT_SEGMENT_PROMPT: Optional[str] = None


def segment_pdf(
    text: str,
    prompt: Optional[str] = None,
    *,
    client: Optional[object] = None,
    model: str = "gpt-4o",
) -> Dict[str, Any]:
    """Return segmentation JSON for *text* using *prompt*.
    If no prompt is provided, the default segmentation template is used.

    The implementation is intentionally minimal – real logic lives in the LLM.
    """

    # ------------------------------------------------------------------
    # Resolve the prompt to send to the LLM.
    #
    # We used to re‑use ``settings.prompt`` for both the *summarize* **and**
    # *segment* helpers.  That turned out to be error‑prone because a project‑
    # local ``pdf-ocr-pipeline.ini`` (or a "--prompt" flag in the summarizer
    # CLI) could accidentally overwrite the segmentation template with a
    # generic *summarize* prompt such as
    #
    #     "Extract and summarize the key information from this OCR text …"
    #
    # When that happened the LLM would receive the wrong instruction set and
    # return a summary instead of the expected JSON segmentation output.  To
    # avoid these silent mis‑classifications we now **always** load the built‑
    # in segmentation template when no explicit *prompt* argument is passed.
    # ------------------------------------------------------------------

    if prompt is not None and prompt.strip():
        prompt_text = prompt
    else:
        global _DEFAULT_SEGMENT_PROMPT  # noqa: PLW0603 – allowed, local cache

        if _DEFAULT_SEGMENT_PROMPT is None:
            # Load bundled template on‑demand.  Import locally to keep the
            # module import‑time cheap and to avoid issues when the package is
            # embedded in an environment that strips resources (e.g.
            # PyInstaller).
            try:
                import importlib.resources as _resources

                _DEFAULT_SEGMENT_PROMPT = (
                    _resources.files("pdf_ocr_pipeline.templates")
                    .joinpath("segment_prompt.txt")
                    .read_text(encoding="utf-8")
                )
            except Exception:  # pragma: no cover – fallback, should not happen
                _DEFAULT_SEGMENT_PROMPT = settings.prompt  # best we can do

        prompt_text = _DEFAULT_SEGMENT_PROMPT
    messages = [
        {
            "role": "system",
            "content": "You segment multi‑page OCR text into separate real‑estate documents and return JSON.",
        },
        {"role": "user", "content": f"{prompt_text}\n\n{text}"},
    ]

    send_kwargs = {"model": model}
    if client is not None:
        send_kwargs["client"] = client  # type: ignore[arg-type]

    return llm_send(messages, **send_kwargs)  # type: ignore[return-value]
