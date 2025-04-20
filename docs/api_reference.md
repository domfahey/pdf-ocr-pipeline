# PDF OCR Pipeline API Reference

## Core OCR Module (`pdf_ocr_pipeline.ocr`)

### `ocr_pdf(pdf_path, dpi=300, lang="eng")`

Performs OCR on a PDF file using pdftoppm and tesseract.

**Parameters:**
- `pdf_path` (Path): Path to the PDF file to process
- `dpi` (int, optional): Resolution for OCR in DPI. Higher values give more accurate results but are slower. Default: 300
- `lang` (str, optional): Tesseract language code. Default: "eng" (English)

**Returns:**
- `str`: The extracted text as a Unicode string

**Raises:**
- `SystemExit`: If pdftoppm or tesseract fails, the function will log the error and exit with the appropriate error code

**Example:**
```python
from pathlib import Path
from pdf_ocr_pipeline import ocr_pdf

# Process a single PDF file
pdf_path = Path("document.pdf")
extracted_text = ocr_pdf(pdf_path, dpi=300, lang="eng")
print(extracted_text)
```

### `run_cmd(cmd, **kwargs)`

Low-level function to run a subprocess command with error handling.

**Parameters:**
- `cmd` (List[str]): Command to execute as a list of strings
- `**kwargs`: Additional arguments to pass to subprocess.run

**Returns:**
- `subprocess.CompletedProcess`: Result of the subprocess execution

**Raises:**
- `SystemExit`: If the command fails to execute, the function will log the error and exit with error code 1

## AI Summarization Module (`pdf_ocr_pipeline.summarize`)

### `process_with_gpt(client, text, prompt)`

Process text with OpenAI's GPT-4o model to generate structured analysis.

**Parameters:**
- `client` (OpenAI): Initialized OpenAI client
- `text` (str): The OCR text to analyze
- `prompt` (str): The prompt to guide GPT-4o's analysis

**Returns:**
- `Dict[str, Any]`: JSON response from the model containing analysis results

**Example:**
```python
from pdf_ocr_pipeline import ocr_pdf, process_with_gpt
from openai import OpenAI
import os

# Process a PDF file
text = ocr_pdf(Path("document.pdf"))

# Set up OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Analyze the text
analysis = process_with_gpt(
    client,
    text,
    "Extract key information including dates, names, and main topics"
)

# Use the analysis results
print(analysis["summary"])
```

### `setup_openai_client()`

Creates an OpenAI client instance using the API key from environment variables.

**Returns:**
- `OpenAI`: Initialized OpenAI client

**Raises:**
- `ValueError`: If the OPENAI_API_KEY environment variable is not set

### `read_input()`

Reads JSON or plain text input from stdin.

**Returns:**
- `List[Dict[str, Any]]`: List of dictionaries containing file names and OCR text

## Command Line Interface

### OCR Tool

```
pdf-ocr [options] PDF_FILE [PDF_FILE ...]
```

**Options:**
- `--dpi DPI`: Set the resolution for OCR processing (default: 300)
- `-l, --lang LANGUAGE`: Set the language for Tesseract (default: eng)

**Output:**
- JSON data on stdout with file names and OCR text

### Summarization Tool

```
pdf-ocr-summarize [options]
```

**Options:**
- `--prompt PROMPT`: Custom prompt to guide the AI analysis (default: extract key information)
- `--pretty`: Format the JSON output with indentation for better readability
- `-v, --verbose`: Enable verbose output with additional logging information

**Input:**
- JSON data from stdin (typically piped from pdf-ocr)

**Output:**
- JSON data on stdout with file names and AI analysis results

## Complete Pipeline Example

```bash
# Process a PDF and analyze it with AI, saving pretty-printed JSON output
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json

# Process multiple PDFs with custom prompt and higher resolution
pdf-ocr --dpi 600 file1.pdf file2.pdf | \
  pdf-ocr-summarize --prompt "Extract dates, people, and organizations" > results.json
```