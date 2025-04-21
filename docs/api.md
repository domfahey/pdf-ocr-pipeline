# PDF OCR Pipeline API Reference

## Core Functions

### `ocr_pdf(pdf_path, dpi=300, lang="eng")`

Perform OCR on a PDF file using pdftoppm and tesseract.

**Parameters:**
- `pdf_path` (Path): Path of the PDF file to process.
- `dpi` (int, optional): Resolution in DPI for conversion and OCR. Default is 300.
- `lang` (str, optional): Tesseract language code. Default is "eng" (English).

**Returns:**
- `str`: The recognized text as a Unicode string.

**Exits:**
- 1: If pdftoppm or tesseract fails.

**Example:**
```python
from pathlib import Path
from pdf_ocr_pipeline import ocr_pdf

pdf_path = Path("document.pdf")
text = ocr_pdf(pdf_path, dpi=300, lang="eng")
print(text)
```

### `process_pdf(path, settings)`

High-level convenience function that runs OCR and (optionally) AI analysis in one call.

**Signature:**
```python
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

settings = ProcessSettings(
    analyze=False,
    dpi=None,
    lang=None,
    prompt=None,
    model=None,
)
result = process_pdf("document.pdf", settings=settings)
```

**Parameters:**
- `path` (`str` or `Path`): Path to the PDF file.
- `settings` (`ProcessSettings`): Dataclass with options:
  - `analyze` (`bool`): If `True`, run AI analysis after OCR.
  - `dpi` (`Optional[int]`): Override OCR resolution (defaults from settings).
  - `lang` (`Optional[str]`): Override OCR language code.
  - `prompt` (`Optional[str]`): Custom prompt for AI analysis.
  - `model` (`Optional[str]`): Model name for AI analysis (e.g. "gpt-4o").

**Returns:**
- `OcrResult` (when `analyze=False`):
  ```json
  {"file": "document.pdf", "ocr_text": "..."}
  ```
- `SegmentationResult` (when `analyze=True`): AI analysis JSON.

**Raises:**
- `FileNotFoundError`: If the PDF path does not exist.

### `process_with_gpt(client, text, prompt, model=None)`

The command-line interface is provided through the `pdf-ocr` command after installation.

**Usage:**
```
pdf-ocr [options] file1.pdf [file2.pdf ...]
```

**Options:**
- `--dpi DPI`: Set the resolution for OCR processing (default: 300)
- `-l, --lang LANGUAGE`: Set the language for Tesseract (default: eng)
- `-v, --verbose`: Enable verbose output

**Example:**
```bash
pdf-ocr --dpi 600 -l fra document.pdf > result.json
```

## AI‑Powered Analysis Functions

### `setup_openai_client()`

Initialize and return an OpenAI client using the `OPENAI_API_KEY` environment variable.

**Returns:**
- `OpenAI`: Configured client instance

**Raises:**
- `ValueError`: If `OPENAI_API_KEY` is not found

### `process_with_gpt(client, text, prompt)`

Send OCR text to GPT‑4o for structured analysis.

**Parameters:**
- `client` (`OpenAI`): OpenAI client instance
- `text` (`str`): The OCR‐extracted text to analyze
- `prompt` (`str`): Instructions guiding the analysis

**Returns:**
- `dict`: Parsed JSON response (or error info)

**Example:**
```python
from pdf_ocr_pipeline import ocr_pdf, setup_openai_client, process_with_gpt
from pathlib import Path

client = setup_openai_client()
text = ocr_pdf(Path("document.pdf"))
result = process_with_gpt(client, text, "Summarize key points and entities.")
print(result)
```

## Command-line Interface

## Output Format

```json
[
  {
    "file": "document.pdf",
    "ocr_text": "The extracted text content..."
  }
]
```

When processing multiple files, the output will be an array of objects:

```json
[
  {
    "file": "file1.pdf",
    "ocr_text": "The extracted text from file1..."
  },
  {
    "file": "file2.pdf",
    "ocr_text": "The extracted text from file2..."
  }
]
```