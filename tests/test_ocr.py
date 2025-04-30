#!/usr/bin/env python3
"""
Unit tests for the PDF OCR Pipeline core functionality.
"""

import unittest
import sys
import os
import subprocess

# Built‑ins
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

        from pdf_ocr_pipeline.errors import MissingBinaryError

        with self.assertRaises(MissingBinaryError):
            run_cmd(["test_command"])
        self.mock_logger.error.assert_called_once()


@patch("pdf_ocr_pipeline.ocr.run_cmd")
class TestOcrPdf(unittest.TestCase):
    """Test cases for the ocr_pdf function."""

    def setUp(self):
        """Set up test fixtures."""
        # Path to the sample scanned PDF fixture
        self.scanned_pdf = Path(__file__).parent / "fixtures" / "test_scanned.pdf"
        self.digital_pdf = Path(__file__).parent / "fixtures" / "test_digital.pdf"

        # Set up a mock logger
        self.logger_patcher = patch("pdf_ocr_pipeline.ocr.logger")
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.logger_patcher.stop()

    def test_ocr_pdf_success_scanned(self, mock_run_cmd):
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

        # Select pdf path
        result = ocr_pdf(self.scanned_pdf)
        # Expected tagged output for a single page
        expected = "<page number 1>\nSample OCR text\n</page number 1>"
        # Assertions
        self.assertEqual(result, expected)
        self.assertEqual(mock_run_cmd.call_count, 2)

    def test_ocr_pdf_success_digital(self, mock_run_cmd):
        """
        Tests that `ocr_pdf` correctly processes a digital PDF and returns OCR output
        wrapped with the appropriate page number tag.
        
        Simulates successful execution of the underlying commands and verifies that the
        output matches the expected format for a single-page digital PDF.
        """

        # Mock successful pdftoppm and tesseract runs
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = b"ppm_image_data"
        ppm_result.returncode = 0

        tess_result = MagicMock(spec=subprocess.CompletedProcess)
        tess_result.stdout = b"Sample OCR text"
        tess_result.returncode = 0

        mock_run_cmd.side_effect = [ppm_result, tess_result]

        from pdf_ocr_pipeline.ocr import ocr_pdf

        result = ocr_pdf(self.digital_pdf)
        # Expected tagged output for a single page
        expected = "<page number 1>\nSample OCR text\n</page number 1>"
        # Assertions
        self.assertEqual(result, expected)
        self.assertEqual(mock_run_cmd.call_count, 2)

    def test_ocr_pdf_pdftoppm_error_scanned(self, mock_run_cmd):
        """
        Tests that ocr_pdf raises OcrError when pdftoppm fails on a scanned PDF.
        """
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock pdftoppm error
        pdftoppm_error = subprocess.CalledProcessError(returncode=1, cmd=["pdftoppm"])
        mock_run_cmd.side_effect = pdftoppm_error

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.scanned_pdf)

    def test_ocr_pdf_pdftoppm_error_digital(self, mock_run_cmd):
        """Digital version."""

        from pdf_ocr_pipeline.ocr import ocr_pdf

        pdftoppm_error = subprocess.CalledProcessError(returncode=1, cmd=["pdftoppm"])
        mock_run_cmd.side_effect = pdftoppm_error

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.digital_pdf)
        self.mock_logger.error.assert_called_once()

    def test_ocr_pdf_tesseract_error_scanned(self, mock_run_cmd):
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

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.scanned_pdf)

    def test_ocr_pdf_tesseract_error_digital(self, mock_run_cmd):
        from pdf_ocr_pipeline.ocr import ocr_pdf

        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = b"ppm_image_data"
        ppm_result.returncode = 0

        tesseract_error = subprocess.CalledProcessError(returncode=2, cmd=["tesseract"])

        mock_run_cmd.side_effect = [ppm_result, tesseract_error]

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.digital_pdf)
        self.mock_logger.error.assert_called_once()

    def test_ocr_pdf_no_stdout_scanned(self, mock_run_cmd):
        """Test ocr_pdf function when pdftoppm stdout is None."""
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock pdftoppm with no stdout
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = None
        ppm_result.returncode = 0

        mock_run_cmd.return_value = ppm_result

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.scanned_pdf)

    def test_ocr_pdf_no_stdout_digital(self, mock_run_cmd):
        """
        Tests that ocr_pdf raises OcrError and logs an error when pdftoppm returns no stdout for a digital PDF.
        """
        from pdf_ocr_pipeline.ocr import ocr_pdf

        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = None
        ppm_result.returncode = 0

        mock_run_cmd.return_value = ppm_result

        from pdf_ocr_pipeline.errors import OcrError

        with self.assertRaises(OcrError):
            ocr_pdf(self.digital_pdf)
        self.mock_logger.error.assert_called_once()

    def test_ocr_pdf_multiple_pages(self, mock_run_cmd):
        """
        Tests that the ocr_pdf function processes multi-page PDFs and wraps each page's OCR text with the correct page number tags.
        
        Simulates a multi-page PDF by mocking subprocess calls and file discovery, then verifies that the combined OCR output includes each page's content wrapped in the appropriate tags and that the expected number of commands are executed.
        """
        # Import here to apply patches properly
        from pdf_ocr_pipeline.ocr import ocr_pdf

        # Mock pdftoppm to produce multiple image files
        ppm_result = MagicMock(spec=subprocess.CompletedProcess)
        ppm_result.stdout = b"ppm_image_data"
        ppm_result.returncode = 0

        # Set up multiple test page results
        page1_text = "Page one content"
        page2_text = "Page two content"
        page3_text = "Page three content"

        # Create a sequence of mock responses for each page
        tess_result1 = MagicMock(spec=subprocess.CompletedProcess)
        tess_result1.stdout = page1_text.encode("utf-8")
        tess_result1.returncode = 0

        tess_result2 = MagicMock(spec=subprocess.CompletedProcess)
        tess_result2.stdout = page2_text.encode("utf-8")
        tess_result2.returncode = 0

        tess_result3 = MagicMock(spec=subprocess.CompletedProcess)
        tess_result3.stdout = page3_text.encode("utf-8")
        tess_result3.returncode = 0

        # Set up the sequence of responses
        mock_run_cmd.side_effect = [
            ppm_result,
            tess_result1,
            tess_result2,
            tess_result3,
        ]

        # Mock Path.glob to return multiple image file paths
        with patch("pathlib.Path.glob") as mock_glob:
            mock_glob.return_value = [
                Path("/tmp/page-01.ppm"),
                Path("/tmp/page-02.ppm"),
                Path("/tmp/page-03.ppm"),
            ]

            # Call the function under test
            result = ocr_pdf(self.digital_pdf)

        # Expected output with correct page number tags
        expected = (
            f"<page number 1>\n{page1_text}\n</page number 1>\n"
            f"<page number 2>\n{page2_text}\n</page number 2>\n"
            f"<page number 3>\n{page3_text}\n</page number 3>"
        )

        # Assertions
        self.assertEqual(result, expected)
        self.assertEqual(mock_run_cmd.call_count, 4)  # 1 pdftoppm + 3 tesseract calls


if __name__ == "__main__":
    unittest.main()
