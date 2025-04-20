#!/usr/bin/env python3
"""
Unit tests for edge cases in the PDF OCR Pipeline summarization functionality.
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
    read_input,
    main,
)


class TestSummarizeEdgeCases(unittest.TestCase):
    """Test cases for edge cases in the summarization functionality."""

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

    def test_very_long_input_text(self):
        """Test processing very long input text."""
        # Create a mock response
        mock_message = MagicMock()
        mock_message.content = '{"summary": "Summary of long text"}'
        self.mock_completions.choices = [MagicMock(message=mock_message)]

        # Very long text (10,000 characters)
        long_text = "Lorem ipsum dolor sit amet. " * 500

        # Process with GPT
        result = process_with_gpt(self.mock_client, long_text, "Summarize this text")

        # Verify the API was called correctly
        self.mock_client.chat.completions.create.assert_called_once()

        # Check combined prompt contains the long text
        args, kwargs = self.mock_client.chat.completions.create.call_args
        self.assertIn(long_text, kwargs["messages"][1]["content"])

        # Check result
        self.assertEqual(result["summary"], "Summary of long text")

    def test_empty_input_file(self):
        """Test handling of empty input."""
        with patch("sys.stdin.read", return_value=""):
            # Read input
            result = read_input()

            # Should return a list with one item
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["file"], "unknown")
            self.assertEqual(result[0]["ocr_text"], "")

    def test_empty_ocr_text_in_document(self):
        """Test handling of empty OCR text in a document."""
        # Mock input data with empty OCR text
        mock_input = '[{"file": "test.pdf", "ocr_text": ""}]'

        # Set up a default mock response
        mock_message = MagicMock()
        mock_message.content = '{"warning": "Empty text provided"}'
        self.mock_completions.choices = [MagicMock(message=mock_message)]

        # Mock command line arguments
        with patch("sys.argv", ["summarize_text.py"]):
            # Mock stdin read
            with patch("sys.stdin.read", return_value=mock_input):
                # Mock print function
                with patch("builtins.print") as mock_print:
                    # Should log a warning but continue
                    main()

                    # Verify logger was called with warning
                    self.mock_logger.warning.assert_called_once()

                    # Verify no API call was made
                    self.mock_client.chat.completions.create.assert_not_called()

                    # Check output - should be empty results list
                    self.assertTrue(mock_print.called)
                    printed_json = json.loads(mock_print.call_args[0][0])
                    self.assertEqual(len(printed_json), 0)

    def test_malformed_json_input(self):
        """Test handling of malformed JSON input."""
        # Malformed JSON input
        malformed_json = "This is not JSON at all"

        # Mock stdin read to return malformed JSON
        with patch("sys.stdin.read", return_value=malformed_json):
            # The function should handle this as raw text
            result = read_input()

            # Should interpret as raw text
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["file"], "unknown")
            self.assertEqual(result[0]["ocr_text"], malformed_json)

    def test_api_timeout_handling(self):
        """Test handling of API timeout."""
        # Create a mock exception and set it as side effect
        mock_exception = Exception("Request timed out")
        self.mock_client.chat.completions.create.side_effect = mock_exception

        # Process with GPT
        result = process_with_gpt(
            self.mock_client, "Sample text", "Summarize this text"
        )

        # Should return error in result
        self.assertTrue("error" in result)
        self.assertIn("API error", result["error"])
        self.assertIn("timed out", result["error"])

        # Should log error
        self.mock_logger.error.assert_called_once()

    def test_rate_limit_handling(self):
        """Test handling of rate limit errors."""
        # Set up mock to raise a generic exception for rate limiting
        mock_exception = Exception("Rate limit exceeded")
        self.mock_client.chat.completions.create.side_effect = mock_exception

        # Process with GPT
        result = process_with_gpt(
            self.mock_client, "Sample text", "Summarize this text"
        )

        # Should return error in result
        self.assertTrue("error" in result)
        self.assertIn("API error", result["error"])
        self.assertIn("Rate limit", result["error"])

        # Should log error
        self.mock_logger.error.assert_called_once()

    def test_custom_prompt(self):
        """Test using a custom prompt."""
        # Create a mock response
        mock_message = MagicMock()
        mock_message.content = '{"extracted_dates": ["2023-01-01", "2023-02-15"]}'
        self.mock_completions.choices = [MagicMock(message=mock_message)]

        # Custom prompt
        custom_prompt = "Extract all dates from this document"

        # Mock input data
        mock_input = (
            '[{"file": "test.pdf", '
            '"ocr_text": "Meeting on January 1, 2023 and February 15, 2023"}]'
        )

        # Mock command line arguments with custom prompt
        with patch("sys.argv", ["summarize_text.py", "--prompt", custom_prompt]):
            # Override ArgumentParser
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value.prompt = custom_prompt
                mock_args.return_value.pretty = False
                mock_args.return_value.verbose = False

                # Mock stdin read
                with patch("sys.stdin.read", return_value=mock_input):
                    # Mock print function
                    with patch("builtins.print") as mock_print:
                        main()

                        # Verify API was called with the custom prompt
                        self.mock_client.chat.completions.create.assert_called_once()
                        (
                            args,
                            kwargs,
                        ) = self.mock_client.chat.completions.create.call_args
                        self.assertIn(custom_prompt, kwargs["messages"][1]["content"])

                        # Check output includes the extracted dates
                        mock_print.assert_called_once()
                        printed_json = json.loads(mock_print.call_args[0][0])
                        self.assertEqual(
                            printed_json[0]["analysis"]["extracted_dates"],
                            ["2023-01-01", "2023-02-15"],
                        )


if __name__ == "__main__":
    unittest.main()
