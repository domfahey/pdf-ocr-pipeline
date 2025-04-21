#!/usr/bin/env python3
"""
Module for summarizing OCR text using OpenAI's GPT-4o model.
"""

import argparse
import json
import sys

# builtin
from typing import Dict, Any, List, cast, Optional
import logging

# project imports
from .logging_utils import get_logger
from .llm_client import send as llm_send, _get_client  # noqa: WPS437 (internal use)

# internal config/errors must be available before logger use
try:
    from .config import _config
except ImportError:
    _config = {}

from .errors import PipelineError, LlmError  # noqa: F401 (future use)
from .settings import settings

# Import litellm's OpenAI wrapper or fall back to the 'openai' package
try:
    from litellm import OpenAI
except ImportError:
    try:
        from openai import OpenAI
    except ImportError:
        OpenAI = None  # type: ignore

# Configure logger via central helper
logger = get_logger(__name__)


def setup_openai_client():  # noqa: D401 – kept for backward‑compatibility
    """Deprecated: use :pymod:`pdf_ocr_pipeline.llm_client` instead.

    The original public helper remains to avoid breaking external code and the
    *end‑to‑end* integration test.  Internally it simply delegates to the new
    LLM abstraction.
    """

    return _get_client()


def process_with_gpt(  # noqa: D401 – kept public for tests / external callers
    client: Optional[object],
    text: str,
    prompt: str,
    *,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Thin wrapper around :func:`pdf_ocr_pipeline.llm_client.send`.

    Parameters
    ----------
    client:
        Legacy parameter kept for backward compatibility with existing unit
        tests.  It is ignored by the new implementation **unless** the caller
        passes a mock object – in that case the mock is forwarded to
        :func:`llm_client.send` so that test assertions continue to work.
    text:
        OCR‑extracted text.
    prompt:
        Prompt template.
    model:
        Optional model override.
    """

    logger.info("Sending text to LLM for analysis (len=%s)", len(text))

    model_name = model or _config.get("model", "gpt-4o")

    combined_prompt = f"{prompt}\n\nHere is the text to analyze:\n\n{text}"

    # Load system prompt from external template
    try:
        import importlib.resources as _resources

        system_prompt = (
            _resources.files("pdf_ocr_pipeline.templates")
            .joinpath("gpt_system_prompt.txt")
            .read_text(encoding="utf-8")
        )
    except Exception:
        system_prompt = "You analyze OCR text and return structured JSON data."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_prompt},
    ]

    # Forward *client* only if supplied (primarily for unit‑tests).
    send_kwargs = {"model": model_name}
    if client is not None:
        send_kwargs["client"] = client  # type: ignore[arg-type]

    return cast(Dict[str, Any], llm_send(messages, **send_kwargs))


def read_input() -> List[Dict[str, Any]]:
    """
    Read input from stdin, supporting both raw text and JSON format.

    Returns:
        List of dictionaries containing file name and OCR text
    """
    try:
        # Read all input from stdin
        input_data = sys.stdin.read().strip()

        # Try to parse as JSON first
        try:
            data = json.loads(input_data)
            if isinstance(data, list):
                return data
            else:
                return [{"file": "unknown", "ocr_text": json.dumps(data)}]
        except json.JSONDecodeError:
            # Not JSON, treat as raw text
            return [{"file": "unknown", "ocr_text": input_data}]

    except Exception as e:
        logger.error(f"Error reading input: {e}")
        sys.exit(1)


def main() -> None:
    """
    Main function to process OCR text with GPT-4o and output results as JSON.
    """
    parser = argparse.ArgumentParser(
        description="Process OCR text with GPT-4o and output results as JSON"
    )
    # Defaults from settings (override with CLI flags)
    default_verbose = settings.verbose
    # Default prompt from settings (templates module provides fallback)
    default_prompt = settings.prompt
    # Large embedded prompt removed; see templates/segment_prompt.txt
    default_pretty = bool(getattr(settings, "pretty", False))

    parser.add_argument(
        "--prompt",
        default=default_prompt,
        help="The prompt to send to GPT-4o along with the OCR text",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=default_pretty,
        help="Format the JSON output with indentation for better readability",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=default_verbose,
        help="Enable verbose output",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress informational logs; only warnings and errors are shown",
    )
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Adjust root logging level once arguments are known
    # ------------------------------------------------------------------

    root_logger = logging.getLogger()

    if args.verbose and getattr(args, "quiet", False):
        parser.error("--verbose and --quiet are mutually exclusive")

    if getattr(args, "quiet", False):
        root_logger.setLevel(logging.WARNING)
    elif args.verbose:
        root_logger.setLevel(logging.DEBUG)
        logger.debug("Verbose flag enabled – root log‑level set to DEBUG")

    try:
        # Obtain (and thus validate) client once – kept for backward‑compatibility
        client = setup_openai_client()

        # Read input
        documents = read_input()
        logger.debug(f"Processing {len(documents)} document(s)")

        # Process each document
        results = []
        for doc in documents:
            file_name = doc.get("file", "unknown")
            ocr_text = doc.get("ocr_text", "")

            if not ocr_text:
                logger.warning(f"Empty OCR text for file: {file_name}")
                continue

            logger.info(f"Processing text from: {file_name}")

            # Process with GPT – *client* parameter kept as None for new API
            analysis = process_with_gpt(client, ocr_text, args.prompt)

            # Add file information to the result
            result = {"file": file_name, "analysis": analysis}

            results.append(result)

        # Output results as JSON
        indent = 2 if args.pretty else None
        print(json.dumps(results, ensure_ascii=False, indent=indent))

    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
