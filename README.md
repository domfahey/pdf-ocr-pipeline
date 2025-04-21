# PDF OCR Pipeline
![PyPI](https://img.shields.io/pypi/v/pdf-ocr-pipeline)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python Version](https://img.shields.io/pypi/pyversions/pdf-ocr-pipeline)

PDF OCR Pipeline is a command-line and programmatic tool to extract text from PDF documents using OCR (Optical Character Recognition), with optional AI‑powered analysis and summarization.

## Features

- Process single or multiple PDF files in one command
- Configurable OCR resolution (DPI)
- Support for multiple languages via Tesseract
- JSON output for easy integration with other tools
- AI-powered text analysis and summarization using OpenAI's GPT-4o

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [AI‑Powered Analysis](#ai-powered-analysis)
- [Programmatic Usage](#programmatic-usage)
- [Output Format](#output-format)
- [Testing](#testing)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Requirements

- Python 3.6+
- External dependencies:
  - `pdftoppm` (typically from poppler-utils)
  - `tesseract` (Tesseract OCR engine)

## Installation

### From Source

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/pdf-ocr-pipeline.git
   cd pdf-ocr-pipeline
   ```

2. Install the project environment and dependencies using uv:
   ```bash
   # Install uv if not already available
   pip install uv
   # Sync the project (creates .venv and installs dependencies)
   uv sync
   ```
   This will set up a virtual environment, install the package in editable mode,
   and install all runtime dependencies.

### Using pip (when published)

```bash
# Add the published package as a dependency and sync the environment
uv add pdf-ocr-pipeline
uv sync
```

### External Dependencies

Ensure the required external tools are installed:

   **Ubuntu/Debian:**
   ```
   sudo apt-get install poppler-utils tesseract-ocr
   ```

   **macOS:**
   ```
   brew install poppler tesseract
   ```

   **Windows:**
   
   Install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) and [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki). Ensure both are added to your PATH.

## Usage

### Command Line

After installation, you can use either the module directly, the installed entry point, or via uv:

Basic usage:

```bash
# Using the module directly
python ocr_pipe.py path/to/document.pdf > result.json

# Using the installed entry point
pdf-ocr path/to/document.pdf > result.json

# Using uv to run the CLI
uv run pdf-ocr path/to/document.pdf > result.json
```

Process multiple files:

```bash
# Using the module directly
python ocr_pipe.py file1.pdf file2.pdf file3.pdf > results.json

# Using the installed entry point
pdf-ocr file1.pdf file2.pdf file3.pdf > results.json

# Using uv to run the CLI
uv run pdf-ocr file1.pdf file2.pdf file3.pdf > results.json
```

#### Options

- `--dpi DPI`: Set the resolution for OCR processing (default: 300)
- `-l, --lang LANGUAGE`: Set the language for Tesseract (default: eng)

Example with options:

```bash
python ocr_pipe.py --dpi 600 -l fra path/to/french_document.pdf > result.json
```

### AI-Powered Text Analysis

The package includes a powerful tool to analyze OCR text using OpenAI's GPT-4o model:

```bash
# Process a PDF file and analyze the text
pdf-ocr document.pdf | pdf-ocr-summarize --pretty > analysis.json

# Use a custom prompt for the analysis
pdf-ocr document.pdf | pdf-ocr-summarize --prompt "Extract all dates and names mentioned in the text" > analysis.json
```

#### Customizing AI Analysis

You can tailor the AI analysis by providing custom prompts for different types of documents:

- **Legal documents**: `--prompt "Extract all legal entities, contract provisions, and obligations"`
- **Academic papers**: `--prompt "Summarize the methodology, findings and conclusions"`
- **Financial reports**: `--prompt "Extract financial figures, percentages, and trends"`
- **Medical documents**: `--prompt "Extract diagnoses, treatments, and medications"`

#### AI Configuration

- **API Key**: Set the `OPENAI_API_KEY` environment variable with your OpenAI API key
- **Model**: Uses GPT-4o by default for optimal accuracy and structured output
- **Output Format**: Returns structured JSON with analysis organized into relevant sections
- **Verbose Mode**: Use `-v` for detailed processing information

See the [API reference](docs/api.md) for details on library functions and the [Project Organization](docs/project_organization.md) for an overview of the code structure.

### Programmatic Usage

You can also use the pipeline directly from Python:

```python
from pdf_ocr_pipeline import process_pdf

# Pure OCR
ocr = process_pdf("invoice.pdf")

# OCR + segmentation via GPT
segments = process_pdf("closing_package.pdf", analyze=True)
```

See the `examples/` directory for more in‑depth examples.

```python
from pathlib import Path
from pdf_ocr_pipeline import process_pdf

# Pure OCR
pdf_path = Path('document.pdf')
ocr_result = process_pdf(pdf_path, dpi=300, lang='eng')
print(ocr_result)
```

### Example Scripts

The repository includes example scripts to demonstrate common workflows:

1. **Batch Processing with AI Analysis**
   ```bash
   ./examples/ocr_and_analyze.sh document.pdf "Extract key points and entities from this document" output.json
   ```
   This script performs OCR on a PDF, sends the extracted text to OpenAI's GPT-4o for analysis, and saves the structured results to a JSON file. Perfect for automating document processing workflows.

2. **Directory Processing**
   ```bash
   ./examples/process_dir.sh /path/to/pdf/directory [dpi] [language]
   ```
   This script processes all PDF files in a directory and saves individual JSON output files to an `ocr_output` subdirectory. Ideal for batch processing large collections of documents.

3. **Programmatic Integration**
   ```python
   # From examples/programmatic_usage.py
   from pathlib import Path
   from pdf_ocr_pipeline import process_pdf

   pdf_path = Path('document.pdf')

   # Pure OCR
   ocr_result = process_pdf(pdf_path)
   print(ocr_result)

   # OCR + segmentation via GPT
   segmentation_result = process_pdf(pdf_path, analyze=True)
   print(segmentation_result)
   ```
   Demonstrates how to integrate the PDF OCR Pipeline into your own Python applications, using the high-level `process_pdf` function for both OCR and optional AI analysis.

## Output Format

The tool outputs JSON to stdout with the following structure:

For a single file:
```json
[
  {
    "file": "document.pdf",
    "ocr_text": "The extracted text content..."
  }
]
```

For multiple files:
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

### AI Analysis Output Format

When using the GPT-4o analysis feature, the output format is:

```json
[
  {
    "file": "document.pdf",
    "analysis": {
      "summary": "Brief summary of the document content",
      "entities": [
        {"name": "John Smith", "type": "person"},
        {"date": "2023-04-15", "type": "date"}
      ],
      "key_points": [
        "First important point from the document",
        "Second important point from the document"
      ],
      "tables": [
        {
          "header": ["Column1", "Column2"],
          "rows": [
            ["Value1", "Value2"],
            ["Value3", "Value4"]
          ]
        }
      ]
    }
  }
]
```

Note: The exact structure of the `analysis` field may vary depending on the prompt used and the content of the document.

## Testing

To run the test suite:

```bash
python -m unittest discover tests
```

The tests use mock objects to avoid dependencies on external tools, so you can run them even without installing pdftoppm or tesseract.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Format your code: `black ocr_pipe.py`
4. Run linters: `flake8 ocr_pipe.py` and `mypy ocr_pipe.py`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## Documentation

- [API Reference](docs/api.md) – Library and CLI reference
- [Project Organization](docs/project_organization.md) – Code structure and design
- [Changelog](CHANGELOG.md) – History of changes
- [Contributing](CONTRIBUTING.md) – Guidelines for contributing

## Project Structure

```
pdf-ocr-pipeline/
├── CHANGELOG.md           # History of changes to the project
├── CLAUDE.md              # Guidelines for Claude AI when working with this code
├── CONTRIBUTING.md        # Guidelines for contributing to the project
├── LICENSE                # MIT License
├── Makefile               # Development task automation
├── README.md              # This documentation
├── bin/                   # Executable scripts
│   ├── ocr_pipe.py        # OCR command-line script
│   └── summarize_text.py  # Text analysis command-line script
├── docs/                  # Documentation
│   ├── api.md              # API reference
   └── project_organization.md # Project structure and design
├── examples/              # Example scripts and usage patterns
│   ├── __init__.py        # Package indicator
│   ├── ocr_and_analyze.sh # Combined OCR and analysis script
│   ├── process_dir.sh     # Directory processing script
│   └── programmatic_usage.py # Example of programmatic usage
├── ocr_pipe.py            # Symlink for backward compatibility
├── pyproject.toml         # Modern Python project configuration
├── requirements-dev.txt   # Development dependencies
├── requirements.lock      # Locked dependencies
├── setup.cfg              # Configuration for development tools
├── setup.py               # Package installation configuration
├── src/                   # Source code
│   └── pdf_ocr_pipeline/  # Main package
│       ├── __init__.py    # Package initialization
│       ├── __main__.py    # Entry point for running as a module
│       ├── cli.py         # OCR command-line interface
│       ├── ocr.py         # Core OCR functionality
│       └── summarize.py   # AI text analysis functionality
├── tests/                 # Unit tests
│   ├── __init__.py        # Package indicator
│   ├── test_cli.py        # Tests for CLI functionality
│   ├── test_ocr.py        # Tests for OCR functionality
│   ├── test_pipeline.py   # Integration tests for the full pipeline
│   └── test_summarize.py  # Tests for AI summarization
└── tox.ini                # Test automation configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Poppler](https://poppler.freedesktop.org/) for PDF rendering
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition