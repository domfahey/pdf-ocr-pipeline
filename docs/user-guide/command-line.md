# Command Line Interface

PDF OCR Pipeline offers three main command-line tools for different tasks.

## pdf-ocr

Extract text from PDF files using OCR.

```bash
pdf-ocr [options] file1.pdf [file2.pdf ...]
```

### Options

| Option | Description |
|--------|-------------|
| `--dpi DPI` | Set OCR resolution (default: 300) |
| `-l, --lang LANGUAGE` | Set OCR language (default: eng) |
| `-v, --verbose` | Enable verbose logging |

### Example

```bash
# Basic usage
pdf-ocr document.pdf > result.json

# Higher quality OCR with French language
pdf-ocr --dpi 600 -l fra document.pdf > result.json

# Process multiple files
pdf-ocr file1.pdf file2.pdf > results.json
```

## pdf-ocr-summarize

Process OCR text with GPT-4o for structured analysis.

```bash
pdf-ocr-summarize [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--prompt PROMPT` | Custom analysis instructions |
| `--pretty` | Format JSON output with indentation |
| `-v, --verbose` | Enable verbose logging |
| `-q, --quiet` | Show only warnings and errors |

### Example

```bash
# Pipe OCR text to the analyzer
pdf-ocr document.pdf | pdf-ocr-summarize > analysis.json

# Pretty-print the output
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json

# Custom analysis prompt
pdf-ocr document.pdf | pdf-ocr-summarize --prompt "Extract all dates and names" > analysis.json
```

## pdf-ocr-segment

Segment OCR text into logical document sections (for real-estate documents).

```bash
pdf-ocr-segment [options]
```

### Options

| Option | Description |
|--------|-------------|
| `--prompt PROMPT` | Custom segmentation prompt (rarely needed) |
| `--pretty` | Format JSON output with indentation |
| `-v, --verbose` | Enable verbose logging |
| `-q, --quiet` | Show only warnings and errors |

### Example

```bash
# Segment a document
pdf-ocr document.pdf | pdf-ocr-segment > segments.json

# Pretty-print the output
pdf-ocr document.pdf | pdf-ocr-segment --pretty > segments.json
```

## Common Patterns

### Process and Analyze in One Command

```bash
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json
```

### Batch Processing

```bash
# Create a directory for outputs
mkdir -p results

# Process all PDFs in a directory
for pdf in *.pdf; do
  pdf-ocr "$pdf" | pdf-ocr-summarize --pretty > "results/$(basename "$pdf" .pdf).json"
done
```

### Integration with Other Tools

```bash
# Convert to CSV
pdf-ocr document.pdf | pdf-ocr-summarize | jq -r '.[] | .analysis.entities[] | [.name, .type] | @csv' > entities.csv

# Filter results with grep
pdf-ocr document.pdf | grep -i "important term"
```