# Extracting Text from PDFs

```bash
pdf-ocr document.pdf > output.json
```

This command extracts all text from `document.pdf` and saves it as JSON.

## How It Works

1. PDF pages are converted to images
2. Tesseract OCR processes the images
3. The extracted text is returned as JSON

## Options for Better Results

### Adjust Image Quality

```bash
pdf-ocr --dpi 600 document.pdf > output.json
```

Higher DPI values produce more accurate results but process more slowly.

| DPI | Quality | Speed | Use for |
|-----|---------|-------|---------|
| 150 | Low | Fast | Basic documents |
| 300 | Medium | Medium | Default setting |
| 600 | High | Slow | Small text/details |

### Change Language

```bash
pdf-ocr --lang fra document.pdf > output.json
```

Common language codes:
- `eng` - English (default)
- `fra` - French
- `deu` - German
- `spa` - Spanish

## Understanding the Output

The output is a JSON array containing document information:

```json
[
  {
    "file": "document.pdf",
    "ocr_text": "The extracted text from your document..."
  }
]
```

## Common Issues

**Problem:** Text is poorly recognized

**Solution:** Try increasing the DPI:
```bash
pdf-ocr --dpi 600 document.pdf
```

**Problem:** Text has incorrect characters

**Solution:** Make sure you've set the correct language:
```bash
pdf-ocr --lang deu document.pdf  # For German text
```

## What's Next?

- [Analyze your documents with AI →](analyze-documents.md)
- [Process multiple documents →](batch-process.md)