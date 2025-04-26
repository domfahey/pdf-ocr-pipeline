#!/usr/bin/env bash
# Simple wrapper to segment a PDF using the default real-estate template.
# Usage: segment_pdf.sh <pdf_file> [output_file]

if [ $# -lt 1 ]; then
    echo "Usage: $(basename "$0") <pdf_file> [output_file]"
    exit 1
fi

PDF_FILE="$1"
OUTPUT_FILE="${2:-segment.json}"

# Ensure input PDF exists
if [ ! -f "$PDF_FILE" ]; then
    echo "Error: File '$PDF_FILE' not found." >&2
    exit 1
fi

echo "Segmenting PDF: $PDF_FILE"
echo "Output will be saved to: $OUTPUT_FILE"

# Ensure local 'src' is first on PYTHONPATH so we run the patched code
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

# Run OCR then segmentation (uses default prompt template)
## Always use local module to ensure using current workspace code
python3 -m pdf_ocr_pipeline "$PDF_FILE" \
  | python3 -m pdf_ocr_pipeline.summarize --pretty > "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "Segmentation complete. Results saved to: $OUTPUT_FILE"
else
    echo "Error: Segmentation failed." >&2
    exit 1
fi