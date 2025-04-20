#!/usr/bin/env python3
"""
Script to process OCR text with OpenAI's GPT-4o model and output a JSON summary.

Usage:
    python ocr_pipe.py path/to/file.pdf | python summarize_text.py

Or:
    cat result.json | python summarize_text.py
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, Optional
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
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
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
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
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes OCR text and returns structured information in JSON format."},
            {"role": "user", "content": combined_prompt}
        ]
    )
    
    # Extract the JSON content from the response
    try:
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
        else:
            return {"error": "Empty response from GPT-4o"}
    except (json.JSONDecodeError, AttributeError) as e:
        logger.error(f"Error parsing GPT-4o response: {e}")
        return {"error": f"Failed to parse response: {str(e)}"}


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
    parser.add_argument(
        "--prompt", 
        default="Extract and summarize the key information from this OCR text. Include any names, dates, locations, and main topics. If there are any tables, extract their data in a structured format.",
        help="The prompt to send to GPT-4o along with the OCR text"
    )
    parser.add_argument(
        "--pretty", 
        action="store_true", 
        help="Format the JSON output with indentation for better readability"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
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
            result = {
                "file": file_name,
                "analysis": analysis
            }
            
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