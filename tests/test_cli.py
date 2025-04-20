#!/usr/bin/env python3
"""
Unit tests for the PDF OCR Pipeline CLI.
"""

import unittest
import sys
import os
import io
import json
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from pdf_ocr_pipeline.cli import main  # noqa: E402


class TestCli(unittest.TestCase):
    """Test cases for the command-line interface."""

    def setUp(self):
        """Set up test fixtures."""
        # Patch OCR function and file existence
        self.ocr_patcher = patch("pdf_ocr_pipeline.cli.ocr_pdf")
        self.mock_ocr = self.ocr_patcher.start()
        self.mock_ocr.return_value = "OCR text result"
        self.isfile_patcher = patch("pathlib.Path.is_file", return_value=True)
        self.mock_isfile = self.isfile_patcher.start()
        # Patch logger to suppress output
        self.logger_patcher = patch("pdf_ocr_pipeline.cli.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.ocr_patcher.stop()
        self.isfile_patcher.stop()
        self.logger_patcher.stop()

    def test_main_single_file(self):
        """Test main function with a single PDF file."""
        # Simulate CLI invocation
        sys.argv = ["pdf-ocr", "file1.pdf"]
        out = io.StringIO()
        with redirect_stdout(out):
            main()
        # Parse JSON output
        result = json.loads(out.getvalue())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["file"], "file1.pdf")
        self.assertEqual(result[0]["ocr_text"], "OCR text result")
        # Verify OCR called with correct args
        # OCR function should be called with positional args (pdf_path, dpi, lang)
        self.mock_ocr.assert_called_once_with(Path("file1.pdf"), 300, "eng")

    def test_main_multiple_files(self):
        """Test main function with multiple PDF files."""
        # Simulate CLI invocation with two PDFs
        sys.argv = ["pdf-ocr", "file1.pdf", "file2.pdf"]
        # Return different texts for each file
        self.mock_ocr.side_effect = ["text1", "text2"]
        out = io.StringIO()
        with redirect_stdout(out):
            main()
        results = json.loads(out.getvalue())
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["ocr_text"], "text1")
        self.assertEqual(results[1]["ocr_text"], "text2")
        # OCR function should be called for each file with positional args
        from unittest.mock import call

        expected_calls = [
            call(Path("file1.pdf"), 300, "eng"),
            call(Path("file2.pdf"), 300, "eng"),
        ]
        self.assertEqual(self.mock_ocr.call_args_list, expected_calls)

    def test_main_verbose_mode(self):
        """Test main function with verbose flag enabled."""
        # Simulate verbose mode; CLI should pretty-print JSON
        sys.argv = ["pdf-ocr", "-v", "file1.pdf"]
        out = io.StringIO()
        with redirect_stdout(out):
            main()
        output = out.getvalue()
        # Pretty JSON starts with '[\n' and contains indented entries
        self.assertTrue(output.strip().startswith("["))
        self.assertIn("\n  {", output)
        # Validate parsed content
        results = json.loads(output)
        self.assertEqual(results[0]["file"], "file1.pdf")
        self.assertEqual(results[0]["ocr_text"], "OCR text result")


if __name__ == "__main__":
    unittest.main()
