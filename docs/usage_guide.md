# PDF OCR Pipeline Usage Guide

This guide provides detailed instructions on how to use the PDF OCR Pipeline tool for extracting and analyzing text from PDF documents.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [OCR Options](#ocr-options)
- [AI Analysis](#ai-analysis)
- [Processing Multiple Files](#processing-multiple-files)
- [Batch Processing](#batch-processing)
- [Programmatic Usage](#programmatic-usage)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.6 or higher
- External dependencies:
  - pdftoppm (from poppler-utils)
  - tesseract (OCR engine)
- OpenAI API key (for AI analysis features)

### From PyPI (Recommended)

```bash
# Install uv package manager
pip install uv
# Install pdf-ocr-pipeline from PyPI into the environment
uv pip install pdf-ocr-pipeline
```

### From Source

```bash
git clone https://github.com/yourusername/pdf-ocr-pipeline.git
cd pdf-ocr-pipeline
# Install uv package manager and synchronize the project environment
pip install uv
uv sync --all-extras
```

### Environment Setup

For AI analysis features, set your OpenAI API key:

```bash
# Linux/MacOS
export OPENAI_API_KEY="your-api-key"

# Windows
set OPENAI_API_KEY=your-api-key
```

## Basic Usage

### Simple OCR

To extract text from a PDF and output as JSON:

```bash
# Using the installed entry point
pdf-ocr document.pdf > ocr_output.json

# Or via uv
uv run pdf-ocr document.pdf > ocr_output.json
```

### OCR with AI Analysis

To extract and analyze text in one command:

```bash
# Process a PDF file and analyze the text
pdf-ocr document.pdf | pdf-ocr-summarize > analysis.json

# Or via uv
uv run pdf-ocr document.pdf | uv run pdf-ocr-summarize > analysis.json
```

### Pretty-Printed Output

For human-readable output:

```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json
```

## OCR Options

### Resolution (DPI)

Higher DPI values generally produce more accurate results but are slower:

```bash
pdf-ocr --dpi 600 document.pdf > output.json
```

### Language

Specify the language of the document for better OCR results:

```bash
# French document
pdf-ocr -l fra document.pdf > output.json

# German document
pdf-ocr --lang deu document.pdf > output.json
```

See [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html) for available language codes.

## AI Analysis

### Default Analysis

By default, the AI will extract key information including names, dates, locations, and main topics:

```bash
pdf-ocr document.pdf | pdf-ocr-summarize
```

### Custom Prompts

You can customize the analysis by providing a specific prompt:

```bash
# Extract legal entities and provisions
pdf-ocr legal_doc.pdf | pdf-ocr-summarize --prompt "Extract all legal entities, contract provisions, and obligations mentioned in this document"

# Extract financial information
pdf-ocr financial_report.pdf | pdf-ocr-summarize --prompt "Extract all financial figures, percentages, dates, and company names. Organize them by categories."
```

### Verbose Mode

For more detailed logging during processing:

```bash
pdf-ocr document.pdf | pdf-ocr-summarize -v
```

## Processing Multiple Files

You can process multiple PDFs in a single command:

```bash
pdf-ocr file1.pdf file2.pdf file3.pdf > all_ocr.json
```

And analyze all of them together:

```bash
pdf-ocr file1.pdf file2.pdf | pdf-ocr-summarize > analysis.json
```

## Batch Processing

### Using Shell Scripts

The provided example script processes all PDFs in a directory:

```bash
./examples/process_dir.sh /path/to/pdf/directory 300 eng
```

### OCR and Analysis in a Single Step

The combined pipeline script provides OCR and AI analysis in one step:

```bash
./examples/ocr_and_analyze.sh document.pdf "Custom prompt here" output.json
```

## Programmatic Usage

### OCR Only

```python
from pathlib import Path
from pdf_ocr_pipeline import ocr_pdf

# Process a PDF
pdf_path = Path("document.pdf")
text = ocr_pdf(pdf_path, dpi=300, lang="eng")
print(text)
```

### Complete Pipeline

```python
from pathlib import Path
import os
import json
from pdf_ocr_pipeline import ocr_pdf, process_with_gpt
from openai import OpenAI

# Setup
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
pdf_path = Path("document.pdf")

# Extract text
ocr_text = ocr_pdf(pdf_path, dpi=300, lang="eng")

# Analyze with AI
analysis = process_with_gpt(
    client,
    ocr_text,
    "Extract and summarize the key information from this text"
)

# Save results
result = {
    "file": pdf_path.name,
    "ocr_text": ocr_text,
    "analysis": analysis
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

## Troubleshooting

### Missing Dependencies

If you receive a "Missing binary" error:

```
ERROR: Missing binary: pdftoppm
```

Install the required external tools:

```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils tesseract-ocr

# macOS
brew install poppler tesseract
```

### PDF Processing Issues

If your PDF fails to process:

1. Check if the PDF is encrypted or password-protected
2. Try with a higher DPI value for better quality: `pdf-ocr --dpi 600 document.pdf`
3. Ensure the PDF contains actual scanned pages (not just digital text)

### AI Analysis Issues

If AI analysis fails:

1. Check that your OpenAI API key is set correctly
2. Verify you have sufficient credits in your OpenAI account
3. Check your internet connection
4. Try with a simpler or more specific prompt

For further assistance, please open an issue on GitHub.