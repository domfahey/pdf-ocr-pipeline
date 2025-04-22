# Segmenting Multi-Document PDFs

```bash
pdf-ocr document.pdf | pdf-ocr-segment > segments.json
```

This command identifies separate documents within a single PDF file (like a closing package or document bundle).

## What It Does

The segmentation tool:
1. Extracts text from your PDF
2. Identifies logical document boundaries
3. Provides title and page ranges for each document
4. Creates a structured JSON output

## Example Output

```json
[
  {
    "file": "closing_package.pdf",
    "segmentation": {
      "documents": [
        {
          "title": "Purchase Agreement",
          "pages": [1, 5],
          "summary": "Agreement for the purchase of property at 123 Main St"
        },
        {
          "title": "Disclosure Statement",
          "pages": [6, 8],
          "summary": "Seller's disclosure of property condition"
        }
      ],
      "total_pages": 8
    }
  }
]
```

## Options

### Pretty-Print the Output

```bash
pdf-ocr document.pdf | pdf-ocr-segment --pretty > segments.json
```

### Verbose Logging

```bash
pdf-ocr document.pdf | pdf-ocr-segment -v > segments.json
```

## Understanding the Output

- `documents` - Array of identified documents
  - `title` - Document title
  - `pages` - Array with start and end page numbers
  - `summary` - Brief description of document content
- `total_pages` - Total number of pages in the PDF

## Requirements

You need an OpenAI API key to use this feature:

```bash
# Set your API key as an environment variable
export OPENAI_API_KEY="your-api-key"
```

## What's Next?

- [Extract text without analysis →](extract-text.md)
- [Process multiple documents →](batch-process.md)