#!/usr/bin/env python3
"""
Module for summarizing OCR text using OpenAI's GPT-4o model.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, cast, Optional
import logging

# internal config/errors must be available before logger use
try:
    from .config import _config
except ImportError:
    _config = {}

from .errors import PipelineError, LlmError  # noqa: F401 (future use)
from .settings import settings
from .types import SegmentationResult

# Import litellm's OpenAI wrapper or fall back to the 'openai' package
try:
    from litellm import OpenAI
except ImportError:
    try:
        from openai import OpenAI
    except ImportError:
        OpenAI = None  # type: ignore

# Configure logging
logger = logging.getLogger(__name__)


def setup_openai_client() -> OpenAI:
    """
    Set up the OpenAI client with API key from environment variables.

    Returns:
        OpenAI client instance

    Raises:
        ValueError: If the OpenAI API key is not set
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    # ------------------------------------------------------------------
    # Validate API key
    # ------------------------------------------------------------------
    if not api_key or api_key.strip() == "":
        raise ValueError(
            "OpenAI API key not found. "
            "Please set the OPENAI_API_KEY environment variable."
        )

    # Guard against the common mistake of leaving a placeholder string in
    # the environment (e.g. "your_api_key" or "YOUR_API_KEY") which will
    # otherwise cause a confusing 401 error downstream.
    placeholder_values = {"your_api_key", "YOUR_API_KEY", "<your_api_key>"}
    if api_key in placeholder_values:
        raise ValueError(
            "The OPENAI_API_KEY environment variable contains a placeholder "
            "value (e.g. 'your_api_key').  Replace it with your real API key "
            "from https://platform.openai.com/account/api-keys."
        )

    # Instantiate client with API key
    client = OpenAI(api_key=api_key)
    # ------------------------------------------------------------------
    # Allow optional override of the API base URL and version.
    # Priority (highest → lowest):
    #   1. Explicit environment variables (OPENAI_BASE_URL, OPENAI_API_BASE,
    #      OPENAI_API_VERSION) so that users can control endpoints without a
    #      config file.
    #   2. Values from optional config file (pdf-ocr-pipeline.ini).
    # ------------------------------------------------------------------

    # Base URL
    api_base = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or _config.get("api_base")
    )
    if api_base:
        try:
            setattr(client, "base_url", api_base)
        except Exception:
            # Some client versions still use `api_base` – fall back.
            try:
                setattr(client, "api_base", api_base)
            except Exception:
                logger.debug("Failed to set api_base/base_url on client: %s", api_base)

    # API version (Azure‑style deployments)
    api_version = os.environ.get("OPENAI_API_VERSION") or _config.get("api_version")
    if api_version:
        try:
            setattr(client, "api_version", api_version)
        except Exception:
            logger.debug("Failed to set api_version on client: %s", api_version)
    return client


def process_with_gpt(
    client: OpenAI,
    text: str,
    prompt: str,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process OCR text with GPT-4o using the provided prompt.

    Args:
        client: OpenAI client instance
        text: The OCR text to process
        prompt: The prompt to guide GPT-4o's analysis

    Returns:
        The JSON response from the model
    """
    logger.info("Sending text to GPT-4o for analysis...")

    # Determine which model to use: CLI arg overrides config, fall back to default
    model_name = model or _config.get("model", "gpt-4o")
    combined_prompt = f"{prompt}\n\nHere is the text to analyze:\n\n{text}"

    messages = [
        {
            "role": "system",
            "content": "You analyze OCR text and return structured JSON data.",
        },
        {"role": "user", "content": combined_prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_format={"type": "json_object"},
            messages=messages,
        )

        # Extract the JSON content from the response
        try:
            content = response.choices[0].message.content
            if content:
                # json.loads returns Any, so cast to expected dict
                return cast(Dict[str, Any], json.loads(content))
            else:
                return {"error": "Empty response from GPT-4o"}
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Error parsing GPT-4o response: {e}")
            return {"error": f"Failed to parse response: {str(e)}"}
    except Exception as e:
        # Handle API errors (timeout, rate limit, etc.)
        error_msg = str(e)
        logger.error(f"Error calling OpenAI API: {error_msg}")
        return {"error": f"API error: {error_msg}"}


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
    args = parser.parse_args()

    # Configure detailed logging (default DEBUG)
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    if args.verbose:
        logger.debug("Verbose flag enabled (logging already at DEBUG level)")

    try:
        # Set up OpenAI client
        logger.debug("summarize.main loaded from: %s", __file__)
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

            # Process with GPT
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
