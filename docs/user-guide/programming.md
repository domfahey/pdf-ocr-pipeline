# Programming with PDF OCR Pipeline

Integrate PDF OCR Pipeline into your Python applications to automate document processing workflows.

## Basic Usage

The high-level `process_pdf` function provides a convenient way to run OCR and optional AI analysis in one call:

```python
from pathlib import Path
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

# OCR only
result = process_pdf(
    Path("document.pdf"),
    settings=ProcessSettings(analyze=False)
)
print(result["ocr_text"])

# OCR + AI analysis
result = process_pdf(
    Path("document.pdf"),
    settings=ProcessSettings(analyze=True)
)
print(result["documents"])
```

## Individual Components

For more control, you can access the individual components directly:

### OCR Processing

```python
from pathlib import Path
from pdf_ocr_pipeline import ocr_pdf

# Extract text from a PDF
pdf_path = Path("document.pdf")
text = ocr_pdf(pdf_path, dpi=300, lang="eng")
print(text)
```

### AI Text Analysis

```python
from pdf_ocr_pipeline import ocr_pdf, setup_openai_client, process_with_gpt
from pathlib import Path

# Extract text
pdf_path = Path("document.pdf")
text = ocr_pdf(pdf_path)

# Set up OpenAI client
client = setup_openai_client()  # Uses OPENAI_API_KEY environment variable

# Analyze with GPT-4o
analysis = process_with_gpt(
    client,
    text,
    "Extract and summarize key information from this document"
)
print(analysis)
```

### Document Segmentation

```python
from pdf_ocr_pipeline import ocr_pdf, segment_pdf
from pathlib import Path

# Extract text
pdf_path = Path("document.pdf")
text = ocr_pdf(pdf_path)

# Segment the document
segmentation = segment_pdf(text)
print(segmentation)
```

## Custom Configuration

Use the `ProcessSettings` class to configure processing options:

```python
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings

# Configure custom settings
settings = ProcessSettings(
    analyze=True,
    dpi=600,
    lang="fra",
    prompt="Extract all dates, names, and addresses",
    model="gpt-4o-2024-05-13"
)

# Process with custom settings
result = process_pdf("document.pdf", settings=settings)
```

## Processing Multiple Files

```python
from pathlib import Path
from pdf_ocr_pipeline import process_pdf
from pdf_ocr_pipeline.types import ProcessSettings
import json

# Process multiple files
pdf_dir = Path("documents")
results = []

for pdf_path in pdf_dir.glob("*.pdf"):
    result = process_pdf(
        pdf_path,
        settings=ProcessSettings(analyze=True)
    )
    results.append({"file": pdf_path.name, "analysis": result})

# Save combined results
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

## Integration Patterns

### Web Application Integration

```python
# Example Flask endpoint
@app.route("/process", methods=["POST"])
def process_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Save uploaded file
    temp_path = Path("/tmp") / file.filename
    file.save(temp_path)
    
    # Process the file
    try:
        result = process_pdf(
            temp_path,
            settings=ProcessSettings(analyze=True)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up
        temp_path.unlink(missing_ok=True)
```

### Asynchronous Processing

```python
# Example Celery task
@celery.task
def process_document_task(file_path, analyze=False):
    settings = ProcessSettings(analyze=analyze)
    result = process_pdf(Path(file_path), settings=settings)
    
    # Store result or notify user
    with open(f"{file_path}.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return {"status": "completed", "file": file_path}
```