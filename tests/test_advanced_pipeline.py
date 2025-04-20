#!/usr/bin/env python3
"""
Advanced integration tests for the complete OCR and summarization pipeline.
"""

import unittest
import sys
import os
import json
import io
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


class TestAdvancedPipeline(unittest.TestCase):
    """Advanced integration tests for the complete pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock OCR process
        self.ocr_patcher = patch("pdf_ocr_pipeline.ocr.ocr_pdf")
        self.mock_ocr = self.ocr_patcher.start()

        # Mock OpenAI client and setup
        self.openai_patcher = patch("pdf_ocr_pipeline.summarize.setup_openai_client")
        self.mock_openai_setup = self.openai_patcher.start()
        self.mock_client = MagicMock()
        self.mock_openai_setup.return_value = self.mock_client

        # Mock GPT process
        self.gpt_patcher = patch("pdf_ocr_pipeline.summarize.process_with_gpt")
        self.mock_gpt = self.gpt_patcher.start()

        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
        self.env_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.ocr_patcher.stop()
        self.openai_patcher.stop()
        self.gpt_patcher.stop()
        self.env_patcher.stop()

    def test_multiple_document_pipeline(self):
        """Test processing multiple documents through the entire pipeline."""
        # Set up sample OCR results
        sample_ocr_results = [
            {
                "file": "doc1.pdf",
                "ocr_text": "This is the OCR text from document 1.",
            },
            {
                "file": "doc2.pdf",
                "ocr_text": "This is the OCR text from document 2.",
            },
            {
                "file": "doc3.pdf",
                "ocr_text": "This is the OCR text from document 3.",
            },
        ]

        # Set up GPT analysis responses
        gpt_responses = [
            {"summary": "Summary of document 1", "keywords": ["doc1", "sample"]},
            {"summary": "Summary of document 2", "keywords": ["doc2", "example"]},
            {"summary": "Summary of document 3", "keywords": ["doc3", "test"]},
        ]

        # Configure mocks for CLI
        with patch("pdf_ocr_pipeline.cli.ocr_pdf") as mock_cli_ocr:
            # Set up OCR mock to return different texts for each file
            mock_cli_ocr.side_effect = [doc["ocr_text"] for doc in sample_ocr_results]

            # Set up mock arguments for CLI
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value.pdfs = [
                    Path(doc["file"]) for doc in sample_ocr_results
                ]
                mock_args.return_value.dpi = 300
                mock_args.return_value.lang = "eng"
                mock_args.return_value.verbose = False

                # Set up Path.is_file to return True for all files
                with patch("pathlib.Path.is_file", return_value=True):
                    # Mock print function for CLI output capture
                    with patch("builtins.print") as mock_cli_print:
                        # Import and run CLI
                        from pdf_ocr_pipeline.cli import main as cli_main

                        cli_main()

                        # Verify OCR was called for each file
                        self.assertEqual(mock_cli_ocr.call_count, 3)

                        # Capture the JSON output from CLI
                        cli_output = mock_cli_print.call_args[0][0]

        # Configure GPT mock to return different analyses for each document
        self.mock_gpt.side_effect = gpt_responses

        # Now process the OCR results through summarization
        with patch("sys.argv", ["summarize_text.py"]):
            # Mock stdin with the captured CLI output
            with patch("sys.stdin", io.StringIO(cli_output)):
                with patch("builtins.print") as mock_summ_print:
                    # Import and run summarization
                    from pdf_ocr_pipeline.summarize import main as summarize_main

                    summarize_main()

                    # Verify GPT was called for each document
                    self.assertEqual(self.mock_gpt.call_count, 3)

                    # Verify the correct calls to process_with_gpt
                    expected_calls = [
                        call(self.mock_client, doc["ocr_text"], unittest.mock.ANY)
                        for doc in sample_ocr_results
                    ]
                    self.mock_gpt.assert_has_calls(expected_calls, any_order=False)

                    # Check final output format
                    json_output = json.loads(mock_summ_print.call_args[0][0])
                    self.assertEqual(len(json_output), 3)

                    # Verify each document has file and analysis fields
                    for i, doc in enumerate(json_output):
                        self.assertEqual(doc["file"], sample_ocr_results[i]["file"])
                        self.assertEqual(doc["analysis"], gpt_responses[i])

    def test_pipeline_with_multiple_languages(self):
        """Test processing documents in different languages."""
        # Set up sample documents in different languages
        multilingual_docs = [
            {
                "file": "english.pdf",
                "ocr_text": "This is English text",
                "lang": "eng",
                "analysis": {"summary": "English document summary"},
            },
            {
                "file": "french.pdf",
                "ocr_text": "Ceci est un texte français",
                "lang": "fra",
                "analysis": {"summary": "French document summary"},
            },
            {
                "file": "german.pdf",
                "ocr_text": "Dies ist deutscher Text",
                "lang": "deu",
                "analysis": {"summary": "German document summary"},
            },
        ]

        # Set up the GPT mock responses for each document
        self.mock_gpt.side_effect = [doc["analysis"] for doc in multilingual_docs]

        # Process each document separately with different language settings
        for doc in multilingual_docs:
            # Mock CLI arguments
            with patch("argparse.ArgumentParser.parse_args") as mock_args:
                mock_args.return_value.pdfs = [Path(doc["file"])]
                mock_args.return_value.dpi = 300
                mock_args.return_value.lang = doc["lang"]
                mock_args.return_value.verbose = False

                # Mock OCR function to return language-specific text
                with patch("pdf_ocr_pipeline.cli.ocr_pdf") as mock_cli_ocr:
                    mock_cli_ocr.return_value = doc["ocr_text"]

                    # Mock Path.is_file
                    with patch("pathlib.Path.is_file", return_value=True):
                        # Capture CLI output
                        with patch("builtins.print") as mock_cli_print:
                            # Run OCR CLI
                            from pdf_ocr_pipeline.cli import main as cli_main

                            cli_main()

                            # Verify OCR was called with correct language
                            mock_cli_ocr.assert_called_once_with(
                                Path(doc["file"]), 300, doc["lang"]
                            )

                            # Get CLI output
                            cli_output = mock_cli_print.call_args[0][0]

                        # Now process through summarization
                        with patch("sys.argv", ["summarize_text.py"]):
                            with patch("sys.stdin", io.StringIO(cli_output)):
                                with patch("builtins.print") as mock_summ_print:
                                    # Import and run summarization
                                    from pdf_ocr_pipeline.summarize import (
                                        main as summarize_main,
                                    )

                                    summarize_main()

                                    # Check the output includes correct analysis
                                    json_output = json.loads(
                                        mock_summ_print.call_args[0][0]
                                    )
                                    self.assertEqual(len(json_output), 1)
                                    self.assertEqual(
                                        json_output[0]["file"], doc["file"]
                                    )
                                    self.assertEqual(
                                        json_output[0]["analysis"], doc["analysis"]
                                    )

    def test_pipeline_with_custom_prompts(self):
        """Test pipeline with different custom prompts for different document types."""
        # Sample document
        doc = {
            "file": "financial_report.pdf",
            "ocr_text": "Revenue increased by 15% in Q2 2023 compared to Q1 2023.",
        }

        # Different prompt types and expected analyses
        prompts_and_analyses = [
            {
                "prompt": "Extract all percentages and financial metrics",
                "analysis": {"percentages": ["15%"], "metrics": ["Revenue"]},
            },
            {
                "prompt": "Extract all dates and time periods",
                "analysis": {"dates": [], "periods": ["Q1 2023", "Q2 2023"]},
            },
            {
                "prompt": "Summarize the financial performance",
                "analysis": {"summary": "Revenue growth of 15% in Q2 2023"},
            },
        ]

        # Run the pipeline for each prompt type
        for prompt_data in prompts_and_analyses:
            # Set up GPT mock to return the expected analysis
            self.mock_gpt.reset_mock()
            self.mock_gpt.return_value = prompt_data["analysis"]

            # Mock CLI for OCR
            with patch("pdf_ocr_pipeline.cli.ocr_pdf") as mock_cli_ocr:
                mock_cli_ocr.return_value = doc["ocr_text"]

                # Mock args for OCR
                with patch("argparse.ArgumentParser.parse_args") as mock_args:
                    mock_args.return_value.pdfs = [Path(doc["file"])]
                    mock_args.return_value.dpi = 300
                    mock_args.return_value.lang = "eng"
                    mock_args.return_value.verbose = False

                    # Mock Path.is_file
                    with patch("pathlib.Path.is_file", return_value=True):
                        # Capture CLI output
                        with patch("builtins.print") as mock_cli_print:
                            # Run OCR CLI
                            from pdf_ocr_pipeline.cli import main as cli_main

                            cli_main()
                            cli_output = mock_cli_print.call_args[0][0]

                # Now run summarization with custom prompt
                with patch(
                    "sys.argv", ["summarize_text.py", "--prompt", prompt_data["prompt"]]
                ):
                    # Mock args for summarization
                    with patch("argparse.ArgumentParser.parse_args") as mock_summ_args:
                        mock_summ_args.return_value.prompt = prompt_data["prompt"]
                        mock_summ_args.return_value.pretty = False
                        mock_summ_args.return_value.verbose = False

                        # Run with CLI output as input
                        with patch("sys.stdin", io.StringIO(cli_output)):
                            with patch("builtins.print") as mock_summ_print:
                                # Import and run summarization
                                from pdf_ocr_pipeline.summarize import (
                                    main as summarize_main,
                                )

                                summarize_main()

                                # Verify GPT was called with the custom prompt
                                self.mock_gpt.assert_called_once()
                                _, _, prompt_arg = self.mock_gpt.call_args[0]
                                self.assertEqual(prompt_arg, prompt_data["prompt"])

                                # Check output contains the expected analysis
                                json_output = json.loads(
                                    mock_summ_print.call_args[0][0]
                                )
                                self.assertEqual(
                                    json_output[0]["analysis"], prompt_data["analysis"]
                                )


if __name__ == "__main__":
    unittest.main()
