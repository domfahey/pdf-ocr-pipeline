#!/usr/bin/env bash
# This script processes all PDF files in a directory and saves the OCR results to individual JSON files

if [ $# -lt 1 ]; then
    echo "Usage: $0 <directory> [dpi] [lang]"
    echo "  directory: Directory containing PDF files to process"
    echo "  dpi:       Resolution for OCR (default: 300)"
    echo "  lang:      Language code for OCR (default: eng)"
    exit 1
fi

# Default parameters
DIR="$1"
DPI="${2:-300}"
LANG="${3:-eng}"

# Check if directory exists
if [ ! -d "$DIR" ]; then
    echo "Error: Directory '$DIR' not found."
    exit 1
fi

# Create output directory
OUTPUT_DIR="${DIR}/ocr_output"
mkdir -p "$OUTPUT_DIR"

echo "Processing all PDFs in '$DIR' with DPI=$DPI and language=$LANG"
echo "Results will be saved to '$OUTPUT_DIR'"

# Find all PDF files and process them
find "$DIR" -maxdepth 1 -type f -name "*.pdf" | while read -r pdf_file; do
    filename=$(basename "$pdf_file")
    echo "Processing: $filename"
    
    # Run OCR and save to JSON file
    # Use the installed command if available, otherwise fall back to script
    if command -v pdf-ocr &> /dev/null; then
        pdf-ocr --dpi "$DPI" -l "$LANG" "$pdf_file" > "$OUTPUT_DIR/${filename%.pdf}.json"
    else
        python -m pdf_ocr_pipeline --dpi "$DPI" -l "$LANG" "$pdf_file" > "$OUTPUT_DIR/${filename%.pdf}.json"
    fi
    
    if [ $? -eq 0 ]; then
        echo "  Success: Output saved to $OUTPUT_DIR/${filename%.pdf}.json"
    else
        echo "  Error: Failed to process $filename"
    fi
done

echo "Processing complete!"