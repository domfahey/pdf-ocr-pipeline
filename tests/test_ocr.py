#!/usr/bin/env python3
"""
Unit tests for the PDF OCR Pipeline core functionality.
"""

import unittest
import sys
import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

# Import the module with the functions we want to test
from pdf_ocr_pipeline.ocr import run_cmd  # noqa: E402


class TestRunCmd(unittest.TestCase):
    """Test cases for the run_cmd function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock for the subprocess.run function
        self.run_patcher = patch("subprocess.run")
        self.mock_run = self.run_patcher.start()

        # Set up default mock behavior
        completed_process = MagicMock(spec=subprocess.CompletedProcess)
        completed_process.stdout = b"Sample OCR text"
        completed_process.returncode = 0
        self.mock_run.return_value = completed_process

        # Set up a mock logger
        self.logger_patcher = patch("pdf_ocr_pipeline.ocr.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.run_patcher.stop()
        self.logger_patcher.stop()

    def test_run_cmd(self):
        """Test the run_cmd function."""
        cmd = ["test", "command"]
        run_cmd(cmd)
        self.mock_run.assert_called_once()

    def test_run_cmd_error(self):
        """Test run_cmd function with a FileNotFoundError."""
        # Simulate missing executable
        missing_exc = FileNotFoundError()
        missing_exc.filename = "test_command"
        self.mock_run.side_effect = missing_exc

        with patch("sys.exit") as mock_exit:
            run_cmd(["test_command"])
            self.mock_logger.error.assert_called_once()
            mock_exit.assert_called_once_with(1)


@patch("pdf_ocr_pipeline.ocr.run_cmd")
class TestOcrPdf(unittest.TestCase):
    """Test cases for the ocr_pdf function."""

    def setUp(self):
        """Set up test fixtures."""
        # Path to the sample scanned PDF fixture
        self.sample_pdf = Path(__file__).parent / "fixtures" / "test_scanned.pdf"

        # Set up a mock logger
        self.logger_patcher = patch("pdf_ocr_pipeline.ocr.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.logger_patcher.stop()

    def test_ocr_pdf_success(self, mock_run_cmd):
        """Test ocr_pdf function with successful execution."""
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock successful pdftoppm and tesseract runs
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = b"ppm_image_data"
        ppm_result.returncode = 0

        tess_result = MagicMock(spec=subprocess.CompletedProcess)
        tess_result.stdout = b"Sample OCR text"
        tess_result.returncode = 0

        # Set up side effect sequence
        mock_run_cmd.side_effect = [ppm_result, tess_result]

        # Call the function
        result = ocr_pdf(self.sample_pdf)

        # Assertions
        self.assertEqual(result, "Sample OCR text")
        self.assertEqual(mock_run_cmd.call_count, 2)

    def test_ocr_pdf_pdftoppm_error(self, mock_run_cmd):
        """Test ocr_pdf function when pdftoppm fails."""
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock pdftoppm error
        pdftoppm_error = subprocess.CalledProcessError(returncode=1, cmd=["pdftoppm"])
        mock_run_cmd.side_effect = pdftoppm_error

        # Patch sys.exit to prevent actual exit
        with patch("sys.exit") as mock_exit:
            try:
                ocr_pdf(self.sample_pdf)
            except UnboundLocalError:
                # We expect an UnboundLocalError since we're mocking an exception
                # that would normally cause an exit
                pass

            # Assertions on what happened before the exit
            self.mock_logger.error.assert_called_once()
            mock_exit.assert_called_once_with(1)

    def test_ocr_pdf_tesseract_error(self, mock_run_cmd):
        """Test ocr_pdf function when tesseract fails."""
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock successful pdftoppm
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = b"ppm_image_data"
        ppm_result.returncode = 0

        # Mock tesseract error after pdftoppm success
        tesseract_error = subprocess.CalledProcessError(returncode=2, cmd=["tesseract"])

        # Set up side effect sequence: pdftoppm succeeds, tesseract fails
        mock_run_cmd.side_effect = [ppm_result, tesseract_error]

        # Test function with exit mocked
        with patch("sys.exit") as mock_exit:
            try:
                ocr_pdf(self.sample_pdf)
            except UnboundLocalError:
                # We expect an UnboundLocalError since we're mocking an exception
                # that would normally cause an exit
                pass

            # Assertions on what happened before the exit
            self.mock_logger.error.assert_called_once()
            mock_exit.assert_called_once_with(2)

    def test_ocr_pdf_no_stdout(self, mock_run_cmd):
        """Test ocr_pdf function when pdftoppm stdout is None."""
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock pdftoppm with no stdout
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = None
        ppm_result.returncode = 0

        mock_run_cmd.return_value = ppm_result

        # Test function with exit mocked
        with patch("sys.exit") as mock_exit:
            try:
                ocr_pdf(self.sample_pdf)
            except UnboundLocalError:
                # We expect an UnboundLocalError since we're mocking a condition
                # that would normally cause an exit
                pass

            self.mock_logger.error.assert_called_once()
            mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
