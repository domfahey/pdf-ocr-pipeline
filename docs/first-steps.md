# First Steps with PDF OCR Pipeline

This guide will help you quickly get started with basic tasks using PDF OCR Pipeline.

## Basic OCR Processing

Let's start by extracting text from a PDF:

```bash
# Process a single PDF file and save the output
pdf-ocr document.pdf > document.json
```

This creates a JSON file containing the extracted text.

## Understanding the Output

The output JSON has a simple structure:

```json
[
  {
    "file": "document.pdf",
    "ocr_text": "The extracted text from the document..."
  }
]
```

## Processing Multiple Files

You can process multiple PDFs at once:

```bash
# Process multiple files
pdf-ocr file1.pdf file2.pdf file3.pdf > output.json
```

The output will contain entries for each file:

```json
[
  {
    "file": "file1.pdf",
    "ocr_text": "..."
  },
  {
    "file": "file2.pdf",
    "ocr_text": "..."
  },
  ...
]
```

## Adding AI Analysis

To analyze the extracted text with AI:

```bash
# Extract and analyze a document
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json
```

This produces a more structured output with AI-generated insights:

```json
[
  {
    "file": "document.pdf",
    "analysis": {
      "summary": "This document is a contract between...",
      "entities": [
        {"name": "John Smith", "type": "person"},
        {"date": "2023-04-15", "type": "date"}
      ],
      "key_points": [
        "Agreement valid for 12 months",
        "Payment terms net 30 days"
      ]
    }
  }
]
```

## Examining Document Structure

For multi-document PDFs, especially real estate documents:

```bash
# Segment a document into logical parts
pdf-ocr closing_package.pdf | pdf-ocr-segment --pretty > segments.json
```

This identifies different document sections:

```json
[
  {
    "file": "closing_package.pdf",
    "segmentation": {
      "documents": [
        {
          "title": "Purchase Agreement",
          "pages": [1, 5],
          "summary": "Agreement for property purchase..."
        },
        {
          "title": "Disclosure Statement",
          "pages": [6, 8],
          "summary": "Seller's disclosure of property condition..."
        }
      ],
      "total_pages": 8
    }
  }
]
```

## Next Steps

Now that you've seen the basics, you can:

1. Explore [OCR Options](user-guide/ocr-options.md) to improve text extraction quality
2. Learn about [AI Analysis](user-guide/ai-analysis.md) with custom prompts
3. Try [Programming](user-guide/programming.md) with PDF OCR Pipeline in Python

For more detailed information on all commands and options, see the [Command Line Guide](user-guide/command-line.md).