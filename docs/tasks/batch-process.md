# Batch Processing Multiple PDFs

```bash
pdf-ocr file1.pdf file2.pdf file3.pdf > all-texts.json
```

This command processes multiple PDF files in a single operation.

## Process an Entire Directory

```bash
# Using a shell loop
for pdf in *.pdf; do
  pdf-ocr "$pdf" > "${pdf%.pdf}.json"
done
```

## Process and Analyze in Batch

```bash
# Create a directory for outputs
mkdir -p results

# Process all PDFs with analysis
for pdf in *.pdf; do
  pdf-ocr "$pdf" | pdf-ocr-summarize --pretty > "results/${pdf%.pdf}.json"
done
```

## Understanding Batch Output

When processing multiple files in a single command:

```json
[
  {
    "file": "file1.pdf",
    "ocr_text": "Text from the first document..."
  },
  {
    "file": "file2.pdf",
    "ocr_text": "Text from the second document..."
  }
]
```

## Processing in Python

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

## Example Shell Script

Save this as `process_directory.sh`:

```bash
#!/bin/bash
# Usage: ./process_directory.sh <directory> <output_directory>

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Process each PDF file
for pdf in "$INPUT_DIR"/*.pdf; do
  if [ -f "$pdf" ]; then
    filename=$(basename "$pdf" .pdf)
    echo "Processing $filename"
    pdf-ocr "$pdf" | pdf-ocr-summarize --pretty > "$OUTPUT_DIR/$filename.json"
  fi
done

echo "All files processed"
```

Make it executable and run:

```bash
chmod +x process_directory.sh
./process_directory.sh /path/to/pdfs /path/to/output
```

## What's Next?

- [Extract text from PDFs →](extract-text.md)
- [Analyze documents with AI →](analyze-documents.md)