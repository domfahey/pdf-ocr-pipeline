# API Reference

Core functions for using PDF OCR Pipeline in your Python code.

## Main Functions

### process_pdf()

```python
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

result = process_pdf(
    "document.pdf",
    settings=ProcessSettings(analyze=True)
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` or `Path` | Path to the PDF file |
| `settings` | `ProcessSettings` | Configuration options |

**Returns:**

- With `analyze=False`: `{"file": "filename.pdf", "ocr_text": "text..."}`
- With `analyze=True`: The AI analysis result

### ocr_pdf()

```python
from pdf_ocr_pipeline import ocr_pdf
from pathlib import Path

text = ocr_pdf(Path("document.pdf"), dpi=300, lang="eng")
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf_path` | `Path` | Path to the PDF file |
| `dpi` | `int` | Resolution for OCR (default: 300) |
| `lang` | `str` | Language code (default: "eng") |

**Returns:**

- `str`: The extracted text

### segment_pdf()

```python
from pdf_ocr_pipeline import ocr_pdf, segment_pdf

text = ocr_pdf("document.pdf")
segments = segment_pdf(text)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `text` | `str` | OCR text to segment |
| `prompt` | `str` | Optional custom prompt |
| `model` | `str` | AI model to use (default: "gpt-4o") |

**Returns:**

- Document segmentation result

## Settings

### ProcessSettings

```python
from pdf_ocr_pipeline.types import ProcessSettings

settings = ProcessSettings(
    analyze=False,  # Enable AI analysis
    dpi=300,        # OCR resolution
    lang="eng",     # OCR language
    prompt=None,    # AI prompt
    model="gpt-4o"  # AI model
)
```

## Example: Complete Workflow

```python
from pathlib import Path
import json
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

# Process PDF with AI analysis
result = process_pdf(
    Path("document.pdf"),
    settings=ProcessSettings(
        analyze=True,
        dpi=600,
        lang="eng",
        prompt="Extract key information"
    )
)

# Save the result
with open("analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

For more detailed API information, use the Python help function:

```python
import pdf_ocr_pipeline
help(pdf_ocr_pipeline.process_pdf)
```