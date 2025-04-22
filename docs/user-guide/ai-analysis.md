# AI Analysis

PDF OCR Pipeline leverages OpenAI's GPT-4o model to analyze and structure the text extracted from PDFs.

## Overview

After extracting text with OCR, you can analyze it with two AI tools:

1. **pdf-ocr-summarize**: General-purpose text analysis
2. **pdf-ocr-segment**: Specialized for segmenting real-estate documents

## Authentication

Both AI tools require an OpenAI API key. Set it as an environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"

# Windows
set OPENAI_API_KEY=your-api-key
```

!!! warning
    Never hardcode your API key in scripts or commit it to version control.

## General Analysis with pdf-ocr-summarize

The `pdf-ocr-summarize` tool sends OCR text to GPT-4o and returns structured information.

```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json
```

### Customizing Analysis with Prompts

You can customize what information to extract by providing a prompt:

```bash
# Extract legal entities
pdf-ocr contract.pdf | pdf-ocr-summarize --prompt "Extract all legal entities, contract terms, and obligations" > legal_analysis.json

# Extract financial information
pdf-ocr report.pdf | pdf-ocr-summarize --prompt "Extract financial figures, percentages, and trends" > financial_analysis.json
```

### Example Prompts for Different Document Types

| Document Type | Example Prompt |
|---------------|----------------|
| Legal | "Extract key legal entities, contract provisions, effective dates, and obligations" |
| Financial | "Extract financial metrics, growth percentages, and key performance indicators" |
| Medical | "Extract diagnoses, medications, dosages, and treatment plans" |
| Academic | "Summarize the methodology, findings, and conclusions" |
| Resume | "Extract the person's name, skills, work experience, and education history" |

## Document Segmentation with pdf-ocr-segment

The `pdf-ocr-segment` tool specializes in identifying and separating multiple logical documents within a single PDF.

```bash
pdf-ocr document.pdf | pdf-ocr-segment --pretty > segments.json
```

### Output Structure

The segmentation tool returns a JSON structure like this:

```json
[
  {
    "file": "document.pdf",
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

## Rate Limits and Performance

OpenAI API calls are subject to rate limits and token limits:

- Large documents may exceed the token limit of GPT-4o
- Frequent API calls may trigger rate limiting

To handle these limitations:

1. Process documents in batches with appropriate delays
2. For very large documents, consider splitting them before analysis
3. Set up exponential backoff for API calls