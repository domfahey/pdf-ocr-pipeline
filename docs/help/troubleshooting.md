# Troubleshooting

Common issues and their solutions.

## OCR Problems

### Blank or Empty Output

**Problem**: Running OCR produces empty or minimal text.

**Solutions**:
1. Increase the DPI resolution:
   ```bash
   pdf-ocr --dpi 600 document.pdf
   ```

2. Verify your PDF contains actual scanned text (not just images):
   ```bash
   pdfinfo document.pdf
   ```

3. Ensure the document language matches the OCR language:
   ```bash
   pdf-ocr --lang fra document.pdf  # For French documents
   ```

### Incorrect Character Recognition

**Problem**: Text is recognized but with many errors.

**Solutions**:
1. Specify the correct language:
   ```bash
   pdf-ocr --lang deu document.pdf  # For German documents
   ```

2. Increase DPI for better quality:
   ```bash
   pdf-ocr --dpi 600 document.pdf
   ```

## AI Analysis Issues

### OpenAI API Key Errors

**Problem**: `Error: OpenAI API key not found`

**Solution**: Set your API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key"
```

### API Rate Limiting

**Problem**: `Error: Rate limit exceeded`

**Solutions**:
1. Add delays between API calls:
   ```bash
   sleep 2  # Wait 2 seconds between calls
   ```

2. Use batching to reduce the number of API calls:
   ```bash
   pdf-ocr file1.pdf file2.pdf | pdf-ocr-summarize
   ```

### Token Limit Exceeded

**Problem**: `Error: This model's maximum context length is...`

**Solutions**:
1. Process smaller documents or page ranges
2. Reduce the extracted text by using a lower DPI:
   ```bash
   pdf-ocr --dpi 150 document.pdf | pdf-ocr-summarize
   ```

## External Dependency Issues

### "pdftoppm: write failed broken pipe"

**Problem**: Poppler version 25 changed behavior, causing this error.

**Solution**: Either:
1. Upgrade to Poppler >25
2. Downgrade to Poppler <25
3. Use the latest version of PDF OCR Pipeline which includes a workaround

### "Error opening data file ... eng.traineddata"

**Problem**: Tesseract cannot find the requested language pack.

**Solution**: Install the language package:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-eng

# macOS
brew install tesseract-lang
```

## JSON Formatting Issues

**Problem**: Error parsing JSON output.

**Solution**: Use the `--pretty` flag for readable JSON:
```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > output.json
```

## Getting Help

If your issue isn't covered here:

1. Check if pdftoppm and tesseract are properly installed and on your PATH:
   ```bash
   which pdftoppm tesseract  # Linux/macOS
   where pdftoppm tesseract  # Windows
   ```

2. Run commands with verbose logging:
   ```bash
   pdf-ocr -v document.pdf
   ```

3. [Open an issue](https://github.com/pdf-ocr/pdf-ocr-pipeline/issues) on GitHub with:
   - Commands you're running
   - Error messages
   - System information
   - Version of PDF OCR Pipeline (`pdf-ocr --version`)