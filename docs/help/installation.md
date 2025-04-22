# Installation Guide

## Quick Install

```bash
# 1. Install PDF OCR Pipeline
pip install pdf-ocr-pipeline

# 2. Install external tools
# Ubuntu/Debian:
sudo apt-get install poppler-utils tesseract-ocr

# macOS:
brew install poppler tesseract

# 3. For AI features, set your API key
export OPENAI_API_KEY="your-api-key"
```

## External Dependencies

PDF OCR Pipeline requires two external tools:

1. **pdftoppm** (from Poppler)
2. **Tesseract OCR**

### Installing on Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr
```

### Installing on macOS

```bash
brew install poppler tesseract
```

### Installing on Windows

1. **Install Poppler**:
   - Download from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Add the `bin` directory to your PATH

2. **Install Tesseract**:
   - Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and add to your PATH

## Python Package Installation

### Standard Installation

```bash
pip install pdf-ocr-pipeline
```

### Install with Development Dependencies

```bash
pip install pdf-ocr-pipeline[dev]
```

### Install from Source

```bash
git clone https://github.com/pdf-ocr/pdf-ocr-pipeline.git
cd pdf-ocr-pipeline
pip install -e .
```

## Setting Up for AI Features

To use AI analysis features, you need an OpenAI API key:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key"
```

## Verifying Your Installation

Test that everything is working:

```bash
# Check the installed version
pdf-ocr --version

# Simple test (if you have a PDF)
pdf-ocr path/to/document.pdf
```

## Common Installation Issues

**Error**: `pdftoppm: command not found`

**Solution**: Install Poppler and make sure it's in your PATH:
```bash
# Check if pdftoppm is installed
which pdftoppm  # on Linux/macOS
where pdftoppm  # on Windows
```

**Error**: `tesseract: command not found`

**Solution**: Install Tesseract OCR and verify it's in your PATH:
```bash
# Check if tesseract is installed
which tesseract  # on Linux/macOS
where tesseract  # on Windows
```

**Error**: Language data not found

**Solution**: Install the language pack:
```bash
# On Ubuntu/Debian
sudo apt-get install tesseract-ocr-fra  # For French
```