#!/usr/bin/env python3
"""
Unit tests for error handling in the PDF OCR Pipeline CLI.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from pdf_ocr_pipeline.cli import main  # noqa: E402


class TestCliErrorHandling(unittest.TestCase):
    """Test cases for CLI error handling."""

    def setUp(self):
        """Set up test fixtures."""
        # Set up mock for argparse
        self.parser_patcher = patch("argparse.ArgumentParser.parse_args")
        self.mock_args = self.parser_patcher.start()

        # Set up mock for ocr_pdf function
        self.ocr_patcher = patch("pdf_ocr_pipeline.cli.ocr_pdf")
        self.mock_ocr = self.ocr_patcher.start()

        # Set up mock for json dumps
        self.json_patcher = patch("json.dumps")
        self.mock_json = self.json_patcher.start()
        self.mock_json.return_value = '{"result":"json"}'

        # Set up mock for print
        self.print_patcher = patch("builtins.print")
        self.mock_print = self.print_patcher.start()

        # Set up mock for logger
        self.logger_patcher = patch("pdf_ocr_pipeline.cli.logger")
        self.mock_logger = self.logger_patcher.start()

        # Set up mock for sys.exit
        self.exit_patcher = patch("sys.exit")
        self.mock_exit = self.exit_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.parser_patcher.stop()
        self.ocr_patcher.stop()
        self.json_patcher.stop()
        self.print_patcher.stop()
        self.logger_patcher.stop()
        self.exit_patcher.stop()

    def test_file_not_found(self):
        """Test error handling when a file is not found."""
        # Set up mock arguments
        mock_args = MagicMock()
        mock_args.pdfs = [Path("nonexistent.pdf")]
        mock_args.dpi = 300
        mock_args.lang = "eng"
        mock_args.verbose = False
        self.mock_args.return_value = mock_args

        # Set up Path.is_file to return False
        with patch("pathlib.Path.is_file", return_value=False):
            # Call the function
            main()

            # Assertions
            self.mock_logger.error.assert_called_once()
            self.mock_exit.assert_called_once_with(1)

    def test_ocr_exception_handling(self):
        """Test handling of exceptions from OCR process."""
        # Set up mock arguments
        mock_args = MagicMock()
        mock_args.pdfs = [Path("file1.pdf"), Path("file2.pdf")]
        mock_args.dpi = 300
        mock_args.lang = "eng"
        mock_args.verbose = False
        self.mock_args.return_value = mock_args

        # Set up Path.is_file to return True
        with patch("pathlib.Path.is_file", return_value=True):
            # First file succeeds, second one raises exception
            self.mock_ocr.side_effect = [
                "OCR text for file1",
                Exception("Test OCR exception"),
            ]

            # Call the function
            main()

            # Assertions
            self.assertEqual(self.mock_ocr.call_count, 2)
            self.mock_logger.error.assert_called_once()

            # Check that JSON output includes both files, with error for the second
            expected_results = [
                {"file": "file1.pdf", "ocr_text": "OCR text for file1"},
                {"file": "file2.pdf", "error": "Test OCR exception"},
            ]
            self.mock_json.assert_called_once()
            args, _ = self.mock_json.call_args
            self.assertEqual(args[0], expected_results)

    def test_system_exit_propagation(self):
        """
        Tests that a SystemExit raised during the OCR process is not caught and propagates as expected.
        """
        # Set up mock arguments
        mock_args = MagicMock()
        mock_args.pdfs = [Path("file1.pdf")]
        mock_args.dpi = 300
        mock_args.lang = "eng"
        mock_args.verbose = False
        self.mock_args.return_value = mock_args

        # Set up Path.is_file to return True
        with patch("pathlib.Path.is_file", return_value=True):
            # Make OCR process raise SystemExit
            self.mock_ocr.side_effect = SystemExit(2)

            # Call the function, expect exception to propagate
            with self.assertRaises(SystemExit):
                main()

    def test_verbose_and_quiet_conflict(self):
        """
        Tests that providing both --verbose and --quiet flags causes the CLI to raise a parser error.
        """
        mock_args = MagicMock()
        mock_args.pdfs = [Path("file1.pdf")]
        mock_args.dpi = 300
        mock_args.lang = "eng"
        mock_args.verbose = True
        mock_args.quiet = True
        self.mock_args.return_value = mock_args

        with patch(
            "argparse.ArgumentParser.error", side_effect=SystemExit(2)
        ) as mock_error:
            with self.assertRaises(SystemExit):
                main()
            mock_error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
