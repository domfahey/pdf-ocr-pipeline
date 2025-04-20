#!/usr/bin/env python3
"""
Unit tests for the PDF OCR Pipeline summarization functionality.
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from pdf_ocr_pipeline.summarize import (  # noqa: E402
    process_with_gpt,
    setup_openai_client,
    read_input,
    main,
)


class TestSummarize(unittest.TestCase):
    """Test cases for the summarization functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenAI client
        self.openai_patcher = patch("pdf_ocr_pipeline.summarize.OpenAI")
        self.mock_openai = self.openai_patcher.start()

        # Create a mock client instance
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client

        # Mock completions
        self.mock_completions = MagicMock()
        self.mock_client.chat.completions.create.return_value = self.mock_completions

        # Set up a default mock response
        mock_message = MagicMock()
        msg_content = (
            '{"summary": "Test summary", "key_points": ["Point 1", "Point 2"]}'
        )
        mock_message.content = msg_content
        self.mock_completions.choices = [MagicMock(message=mock_message)]

        # Mock logger
        self.logger_patcher = patch("pdf_ocr_pipeline.summarize.logger")
        self.mock_logger = self.logger_patcher.start()

        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
        self.env_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.openai_patcher.stop()
        self.logger_patcher.stop()
        self.env_patcher.stop()

    def test_setup_openai_client(self):
        """Test setting up the OpenAI client."""
        client = setup_openai_client()
        self.assertEqual(client, self.mock_client)
        self.mock_openai.assert_called_once_with(api_key="test-api-key")

    def test_setup_openai_client_missing_api_key(self):
        """Test error handling when API key is missing."""
        # Remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                setup_openai_client()

            self.assertIn("OpenAI API key not found", str(context.exception))

    def test_process_with_gpt(self):
        """Test processing text with GPT-4o."""
        result = process_with_gpt(
            self.mock_client, "Sample OCR text", "Summarize this text"
        )

        # Check if OpenAI API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()

        # Verify the correct model was used
        args, kwargs = self.mock_client.chat.completions.create.call_args
        self.assertEqual(kwargs["model"], "gpt-4o")

        # Verify response format is JSON
        self.assertEqual(kwargs["response_format"], {"type": "json_object"})

        # Check if the correct result was returned
        self.assertEqual(result["summary"], "Test summary")
        self.assertEqual(result["key_points"], ["Point 1", "Point 2"])

    def test_process_with_gpt_empty_response(self):
        """Test handling of empty responses from GPT-4o."""
        # Mock an empty response
        self.mock_completions.choices[0].message.content = None

        result = process_with_gpt(
            self.mock_client, "Sample OCR text", "Summarize this text"
        )

        self.assertEqual(result, {"error": "Empty response from GPT-4o"})

    def test_process_with_gpt_invalid_json(self):
        """Test handling of invalid JSON responses from GPT-4o."""
        # Mock an invalid JSON response
        self.mock_completions.choices[0].message.content = "Not valid JSON"

        result = process_with_gpt(
            self.mock_client, "Sample OCR text", "Summarize this text"
        )

        self.assertIn("error", result)
        self.assertIn("Failed to parse response", result["error"])

    def test_read_input_json_list(self):
        """Test reading JSON list input."""
        mock_json = '[{"file": "doc1.pdf", "ocr_text": "Sample text 1"}, '
        mock_json += '{"file": "doc2.pdf", "ocr_text": "Sample text 2"}]'

        with patch("sys.stdin.read", return_value=mock_json):
            result = read_input()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["file"], "doc1.pdf")
        self.assertEqual(result[0]["ocr_text"], "Sample text 1")
        self.assertEqual(result[1]["file"], "doc2.pdf")
        self.assertEqual(result[1]["ocr_text"], "Sample text 2")

    def test_read_input_json_object(self):
        """Test reading JSON object input."""
        mock_json = '{"some_key": "some_value"}'

        with patch("sys.stdin.read", return_value=mock_json):
            result = read_input()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "unknown")
        self.assertEqual(result[0]["ocr_text"], mock_json)

    def test_read_input_raw_text(self):
        """Test reading raw text input."""
        mock_text = "This is some raw OCR text"

        with patch("sys.stdin.read", return_value=mock_text):
            result = read_input()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "unknown")
        self.assertEqual(result[0]["ocr_text"], mock_text)

    def test_main_function(self):
        """Test the main function."""
        # Mock input data
        mock_input = '[{"file": "test.pdf", "ocr_text": "Sample OCR text"}]'

        # Expected output
        expected_output = [
            {
                "file": "test.pdf",
                "analysis": {
                    "summary": "Test summary",
                    "key_points": ["Point 1", "Point 2"],
                },
            }
        ]

        # Mock command line arguments
        with patch("sys.argv", ["summarize_text.py"]):
            # Mock stdin read
            with patch("sys.stdin.read", return_value=mock_input):
                # Mock print function
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify print was called with correct JSON
                    mock_print.assert_called_once()
                    printed_output = json.loads(mock_print.call_args[0][0])
                    self.assertEqual(printed_output, expected_output)


if __name__ == "__main__":
    unittest.main()
