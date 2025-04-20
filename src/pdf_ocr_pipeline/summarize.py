#!/usr/bin/env python3
"""
Module for summarizing OCR text using OpenAI's GPT-4o model.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, cast
import logging

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
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. "
            "Please set the OPENAI_API_KEY environment variable."
        )

    return OpenAI(api_key=api_key)


def process_with_gpt(client: OpenAI, text: str, prompt: str) -> Dict[str, Any]:
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
            model="gpt-4o",
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

    default_prompt = (
        "Extract and summarize the key information from this OCR text. "
        "Include names, dates, locations, and main topics. "
        "If there are tables, extract their data in a structured format."
    )

    parser.add_argument(
        "--prompt",
        default=default_prompt,
        help="The prompt to send to GPT-4o along with the OCR text",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Format the JSON output with indentation for better readability",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        # Set up OpenAI client
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

            # Process with GPT-4o
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
