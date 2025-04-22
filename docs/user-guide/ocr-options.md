# OCR Options

Customize the OCR process to achieve the best results for different document types.

## Resolution (DPI)

The DPI (dots per inch) setting controls the resolution used when converting PDF pages to images for OCR processing.

```bash
pdf-ocr --dpi 600 document.pdf
```

| DPI | Use Case |
|-----|----------|
| 150 | Fast processing, lower quality |
| 300 | Default - good balance of speed and quality |
| 600 | High quality, slower processing |
| 900 | Very high quality, much slower processing |

!!! tip "Memory Usage"
    Higher DPI values consume more memory. For very large documents, you may need to reduce the DPI if you encounter memory errors.

## Language Selection

Tesseract OCR supports many languages. Specify the language using the ISO 639-2 three-letter code.

```bash
pdf-ocr -l fra document.pdf  # French
pdf-ocr --lang deu document.pdf  # German
```

### Common Language Codes

| Code | Language |
|------|----------|
| `eng` | English (default) |
| `fra` | French |
| `deu` | German |
| `spa` | Spanish |
| `ita` | Italian |
| `jpn` | Japanese |
| `kor` | Korean |
| `chi_sim` | Chinese (Simplified) |
| `chi_tra` | Chinese (Traditional) |
| `ara` | Arabic |
| `rus` | Russian |

See the [complete list of language codes](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html).

## Multiple Page Handling

All pages in the PDF are processed by default. The extracted text includes all pages concatenated in order.

```bash
# Process a multi-page PDF
pdf-ocr multipage.pdf > all_pages.json
```

## Optimizing OCR Quality

For the best OCR results:

1. **Select the appropriate DPI**:
   - 300 DPI for most documents
   - 600 DPI for documents with very small text
   
2. **Choose the correct language**:
   - Match the language of your document
   - Use `eng` only for English documents
   
3. **Consider document quality**:
   - Higher DPI may help with poor quality scans
   - Consider preprocessing very poor quality scans with other tools before OCR

4. **Test with sample documents**:
   - Try different settings on representative samples
   - Compare the OCR accuracy to find optimal parameters