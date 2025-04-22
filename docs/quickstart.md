<!-- Quickstart Guide for PDF OCR Pipeline -->
# Quickstart

Welcome to the Quickstart guide for PDF OCR Pipeline. This minimal page shows you how to install, run, and integrate the basic functionality in under five commands.

## Installation

Ensure you have Python 3.8+ and Poppler (`pdftoppm`) and Tesseract on your PATH.

```bash
# Install the package
pip install pdf-ocr-pipeline

# Set up your OpenAI API key for AI features
export OPENAI_API_KEY="your-api-key"  # Linux/macOS
# or
set OPENAI_API_KEY=your-api-key  # Windows
```

## Quick CLI Usage

### Pure OCR

Extract text from a PDF and output JSON:
```bash
pdf-ocr document.pdf > ocr_output.json
```

### OCR + AI Analysis

Run OCR and immediately analyze with GPT-4o:
```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json
```

## Quick Programmatic Integration

Use the high-level `process_pdf` in your own scripts:
```python
from pathlib import Path
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

# Configure pipeline: enable analysis
settings = ProcessSettings(analyze=True)

# Run pipeline
result = process_pdf(Path("document.pdf"), settings=settings)
print(result)
```

That's it—you're up and running!