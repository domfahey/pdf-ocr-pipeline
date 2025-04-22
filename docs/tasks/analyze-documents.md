# Analyzing Documents with AI

```bash
pdf-ocr document.pdf | pdf-ocr-summarize > analysis.json
```

This command extracts text from your PDF and analyzes it with AI to identify key information.

## What You Get

The AI analysis provides:
- A summary of the document
- Key entities (names, dates, locations)
- Important points from the content
- Structured data extraction

## Customizing Analysis

### Use a Custom Prompt

```bash
pdf-ocr document.pdf | pdf-ocr-summarize --prompt "Extract all legal entities, dates, and contract terms" > legal-analysis.json
```

### Make Output Pretty-Printed

```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > readable-analysis.json
```

## Example Prompts by Document Type

| Document Type | Useful Prompt |
|---------------|---------------|
| Legal | "Extract all legal entities, contract terms, obligations, and effective dates" |
| Financial | "Extract financial figures, percentages, trends, and key metrics" |
| Medical | "Extract diagnoses, medications, dosages, and treatment plans" |
| Resume | "Extract the person's name, skills, work experience, and education" |

## Understanding the Output

The analysis output is a JSON object with structured information:

```json
[
  {
    "file": "document.pdf",
    "analysis": {
      "summary": "This is a contract between...",
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

## Requirements

You need an OpenAI API key to use this feature:

```bash
# Set your API key as an environment variable
export OPENAI_API_KEY="your-api-key"
```

## What's Next?

- [Extract text without analysis →](extract-text.md)
- [Segment multi-document PDFs →](segment-documents.md)