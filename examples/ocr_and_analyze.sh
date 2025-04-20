#!/usr/bin/env bash
# Example script demonstrating a complete pipeline:
# 1. OCR a PDF file
# 2. Process the OCR text with GPT-4o
# 3. Save the results

if [ $# -lt 1 ]; then
    echo "Usage: $0 <pdf_file> [prompt] [output_file]"
    echo "  pdf_file:    PDF file to process"
    echo "  prompt:      (Optional) Prompt for GPT-4o analysis"
    echo "  output_file: (Optional) File to save JSON results (default: output.json)"
    exit 1
fi

# Get arguments
PDF_FILE="$1"
PROMPT="${2:-Extract and summarize the key information from this OCR text. Include any dates, names, and important facts.}"
OUTPUT_FILE="${3:-output.json}"

# Check if PDF file exists
if [ ! -f "$PDF_FILE" ]; then
    echo "Error: File '$PDF_FILE' not found."
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable not set."
    echo "Please set it with: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$(dirname "$(realpath "$0")")"

echo "Processing file: $PDF_FILE"
echo "Using prompt: $PROMPT"
echo "Output will be saved to: $OUTPUT_FILE"

# Run the pipeline
if command -v pdf-ocr &> /dev/null && command -v pdf-ocr-summarize &> /dev/null; then
    pdf-ocr "$PDF_FILE" | pdf-ocr-summarize --prompt "$PROMPT" --pretty > "$OUTPUT_FILE"
else
    python3 -m pdf_ocr_pipeline "$PDF_FILE" | python3 -m pdf_ocr_pipeline.summarize --prompt "$PROMPT" --pretty > "$OUTPUT_FILE"
fi

# Check if the pipeline succeeded
if [ $? -eq 0 ]; then
    echo "Processing complete. Results saved to: $OUTPUT_FILE"
    # Show a preview of the results
    echo "Preview of analysis:"
    jq '.[] | .analysis | {summary: .summary}' "$OUTPUT_FILE" 2>/dev/null || \
    echo "Could not parse JSON output. Check $OUTPUT_FILE for full results."
else
    echo "Error: Processing failed."
    exit 1
fi