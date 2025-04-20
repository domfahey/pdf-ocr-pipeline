# Project Organization

This document explains the organization and structure of the PDF OCR Pipeline project, following Python best practices.

## Directory Structure

```
pdf-ocr-pipeline/
├── bin/                   # Executable scripts
│   └── ocr_pipe.py        # Command-line script (for backward compatibility)
├── docs/                  # Documentation
│   ├── api.md             # API reference
│   └── project_organization.md # This document
├── examples/              # Example scripts and usage patterns
│   ├── __init__.py        # Package indicator
│   ├── process_dir.sh     # Shell script to process directories of PDFs
│   └── programmatic_usage.py # Example of using the tool in Python code
├── src/                   # Source code
│   └── pdf_ocr_pipeline/  # Main package
│       ├── __init__.py    # Package initialization
│       ├── __main__.py    # Entry point for running as a module
│       ├── cli.py         # Command-line interface (concurrent processing, verbose mode)
│       ├── ocr.py         # Core OCR functionality
│       └── summarize.py   # AI-powered text analysis (optional OpenAI dependency)
└── tests/                 # Unit tests
    ├── __init__.py        # Package indicator
    ├── test_basic.py      # Basic tests for package imports
    ├── test_cli.py        # Tests for CLI functionality
    └── test_ocr.py        # Tests for core functionality
```

## Package Design

The project follows a modern Python package structure with:

1. **Separation of concerns**:
   - `ocr.py`: Core functionality for PDF-to-Text OCR
   - `cli.py`: Command-line interface with multi-PDF support and concurrency
   - `summarize.py`: AI-powered analysis of OCR text (optional, requires OpenAI)
   - `__main__.py`: Entry point for module execution
   - `__init__.py`: Package exports and version metadata

2. **Support for different usage patterns**:
   - As a library: `from pdf_ocr_pipeline import ocr_pdf`
   - As a command-line tool: `pdf-ocr file.pdf`
   - As a Python module: `python -m pdf_ocr_pipeline file.pdf`
   - Backward compatibility via `bin/ocr_pipe.py`

3. **Development infrastructure**:
   - `setup.py`: Package installation
   - `pyproject.toml`: Modern Python packaging
   - `tox.ini`: Test automation
   - `Makefile`: Development task automation
   - `requirements-dev.txt`: Development dependencies

## Testing Strategy

The project uses a robust testing strategy:

1. **Unit tests** for core functionality
2. **Integration tests** for CLI components
3. **Basic tests** to ensure package structure works correctly

## Documentation Strategy

Documentation is organized into:

1. **User documentation**:
   - `README.md`: Overview, installation, and usage instructions
   - `docs/api.md`: API reference

2. **Developer documentation**:
   - `CONTRIBUTING.md`: Contribution guidelines and code style
   - `docs/project_organization.md`: Architecture and code structure overview
   - `CLAUDE.md`: Guidelines for AI assistants and code review

## Quality Control

The project maintains quality through:

1. **Linting** with flake8 and Black
2. **Type checking** with mypy
3. **Testing** with pytest
4. **Automation** with tox and Make