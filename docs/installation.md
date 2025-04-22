# Installation

This guide covers installing PDF OCR Pipeline and its dependencies.

## Prerequisites

Before installing PDF OCR Pipeline, ensure you have:

1. **Python 3.8+** installed
2. **External dependencies**:
   - **pdftoppm**: Part of Poppler-utils, used to convert PDF to images
   - **Tesseract OCR**: Used for text recognition

## Installing External Dependencies

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
```

### macOS (Homebrew)

```bash
brew install poppler tesseract
```

### Windows

1. **Poppler**: 
   - Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Add the `bin` directory to your PATH

2. **Tesseract**:
   - Download the installer from [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install and add to your PATH

## Installing PDF OCR Pipeline

### Using pip (Recommended)

The simplest way to install PDF OCR Pipeline is from PyPI:

```bash
pip install pdf-ocr-pipeline
```

### Development Installation

For development or the latest features:

```bash
# Clone the repository
git clone https://github.com/pdf-ocr/pdf-ocr-pipeline.git
cd pdf-ocr-pipeline

# Install with development dependencies
pip install -e ".[dev]"
```

## Setting Up for AI Features

To use the AI analysis features, you need an OpenAI API key:

1. Sign up at [OpenAI Platform](https://platform.openai.com/) and create an API key
2. Set it as an environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key"
```

## Verifying Installation

Test that everything is working correctly:

```bash
# Test the OCR component
pdf-ocr --version

# Optional: Create a test document
echo "Sample OCR Test" > test.txt
convert text:test.txt test.pdf

# Run OCR on the test document
pdf-ocr test.pdf
```

If you see a JSON output with the extracted text, your installation is working correctly.

## Troubleshooting

If you encounter issues:

- **Missing binaries**: Ensure `pdftoppm` and `tesseract` are in your PATH
- **Tesseract languages**: Install additional language packs if needed
- **Permission issues**: Use `sudo` on Linux or run as administrator on Windows if necessary

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).