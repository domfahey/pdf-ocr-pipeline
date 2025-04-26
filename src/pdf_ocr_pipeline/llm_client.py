"""Abstraction layer over the OpenAI / Azure Chat Completion APIs.

The rest of the codebase should *only* interact with language models through
the :func:`send` helper defined in this module.  This shields callers from the
nuances of

* which third‑party SDK is available (``openai`` or ``litellm``),
* environment‑specific base URLs / API versions,
* error handling and JSON‑response normalisation.
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, List, Optional

from .logging_utils import get_logger


logger = get_logger(__name__)

# Lock to ensure thread-safe client instantiation
_client_lock = threading.Lock()
# Singleton client instance (protected by _client_lock)
_client: Optional[Any] = None


# ---------------------------------------------------------------------------
# SDK selection (prefer litellm because of its thin wrapper around Azure etc.)
# ---------------------------------------------------------------------------

try:  # pragma: no cover – depends on dev environment
    from litellm import OpenAI  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:  # pragma: no cover
        OpenAI = None  # type: ignore


class MissingApiKeyError(RuntimeError):
    """Raised when ``OPENAI_API_KEY`` is not configured in the environment."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_client() -> "OpenAI":
    """Instantiate and cache an *OpenAI* client.

    Environment variables inspected:
    * ``OPENAI_API_KEY`` **(required)**
    * ``OPENAI_BASE_URL`` / ``OPENAI_API_BASE`` (optional override)
    * ``OPENAI_API_VERSION``                (optional override)
    """

    global _client
    # Fast path: return existing client
    if _client is not None:
        return _client
    # Thread-safe client initialization
    with _client_lock:
        if OpenAI is None:  # pragma: no cover – import guard
            raise RuntimeError(
                "Neither 'litellm' nor 'openai' package is installed.  "
                "Install one of them via 'pip install openai' or 'pip install litellm'."
            )

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.lower().startswith("sk-xxxxxxxx"):
            raise MissingApiKeyError(
                "The OPENAI_API_KEY environment variable is missing or looks like a placeholder."
            )

        client = OpenAI(api_key=api_key)  # type: ignore[call-arg]

    # Optional endpoint overrides (e.g. Azure proxy / self‑hosted gateway)
    api_base = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
    if api_base:
        for attr in ("base_url", "api_base"):
            try:
                setattr(client, attr, api_base)
            except Exception:  # pragma: no cover – attribute names vary per SDK
                pass

    api_version = os.getenv("OPENAI_API_VERSION")
    if api_version:
        try:
            setattr(client, "api_version", api_version)
        except Exception:  # pragma: no cover – same reason as above
            pass

    logger.debug(
        "OpenAI client initialised (api_base=%s, api_version=%s)", api_base, api_version
    )

    # Cache singleton instance
    _client = client
    return client


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------


def send(
    messages: List[Dict[str, str]],
    *,
    model: str = "gpt-4o",
    client: Optional["OpenAI"] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Send *messages* to the chat completion endpoint and return JSON output.

    Parameters
    ----------
    messages:
        List of role/content dicts as expected by the OpenAI chat completion
        endpoint.
    model:
        Model name – defaults to ``gpt-4o``.
    client:
        Optional already‑initialised *OpenAI* client (mainly for tests).  When
        *None* the module‑level singleton returned by :func:`_get_client` is
        used.
    **kwargs:
        Additional keyword arguments passed straight through to
        ``chat.completions.create`` (e.g. ``max_tokens``).

    Returns
    -------
    dict
        Parsed JSON object produced by the model *or* a dict with an ``error``
        key when something went wrong.
    """

    cli = client or _get_client()

    # Perform the API call
    try:
        logger.info(
            "Calling LLM: model=%s, tokens~=%s",
            model,
            sum(len(m["content"]) for m in messages),
        )
        response = cli.chat.completions.create(  # type: ignore[attr-defined]
            model=model,
            response_format={"type": "json_object"},
            messages=messages,
            **kwargs,
        )
    except BaseException:
        # Re-raise interrupt and system-exit signals
        raise
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        return {"error": f"API error: {exc}"}

    # Validate response structure and extract content
    try:
        choices = response.choices  # type: ignore[attr-defined]
        if not choices:
            raise ValueError("No choices returned in LLM response")
        message = choices[0].message  # type: ignore[attr-defined]
        content = message.content  # type: ignore[attr-defined]
    except Exception as exc:
        logger.error("Malformed response from LLM: %s", exc)
        return {"error": f"Malformed response from LLM: {exc}"}

    if not content:
        return {"error": "Empty response from LLM"}

    # Parse and validate JSON output
    try:
        result = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse LLM JSON: %s", exc)
        return {"error": f"Invalid JSON in LLM response: {exc}"}
    # Ensure we have a JSON object (dict)
    if not isinstance(result, dict):
        logger.error(
            "Invalid response schema: expected JSON object, got %s",
            type(result).__name__,
        )
        return {
            "error": f"Invalid response schema: expected JSON object, got {type(result).__name__}"
        }
    return result
