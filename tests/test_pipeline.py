#!/usr/bin/env python3
"""
Integration test for the OCR and summarization pipeline.
"""

import unittest
import json
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestPipeline(unittest.TestCase):
    """Integration tests for OCR and summarization pipeline."""

    @patch("pdf_ocr_pipeline.ocr.ocr_pdf")
    def test_ocr_to_summarize(self, mock_ocr):
        """Test the pipeline from OCR to summarization using mocks."""
        # Mock the OCR function to return specific text
        mock_ocr.return_value = "Sample OCR text from PDF"

        # Mock the GPT response
        gpt_response = {"summary": "This is a summary of the text"}

        # Mock stdin to simulate OCR output
        ocr_output = [{"file": "test.pdf", "ocr_text": "Sample OCR text from PDF"}]

        # Now mock the summarize script with the mocked ocr output as input
        with patch("sys.argv", ["summarize_text.py"]), patch(
            "sys.stdin", io.StringIO(json.dumps(ocr_output))
        ), patch("builtins.print") as mock_print, patch(
            "pdf_ocr_pipeline.summarize.setup_openai_client"
        ) as mock_setup, patch(
            "pdf_ocr_pipeline.summarize.process_with_gpt"
        ) as mock_gpt:
            # Set up the mock returns
            mock_client = MagicMock()
            mock_setup.return_value = mock_client
            mock_gpt.return_value = gpt_response

            # Import summarize main function
            from pdf_ocr_pipeline.summarize import main as summ_main

            # Run summarize main
            summ_main()

            # Check if the right data was sent to GPT
            mock_gpt.assert_called_once()
            self.assertEqual(mock_gpt.call_args[0][1], "Sample OCR text from PDF")

            # Check if correct output was printed
            expected_output = [{"file": "test.pdf", "analysis": gpt_response}]
            mock_print.assert_called_once()
            self.assertEqual(json.loads(mock_print.call_args[0][0]), expected_output)


if __name__ == "__main__":
    unittest.main()
