# Project Organization

This document explains the organization and structure of the PDF OCR Pipeline project, following Python best practices.

## Workflow Diagram

![PDF OCR Pipeline Workflow](assets/images/workflow-diagram.md)

The diagram above illustrates the core workflow of the PDF OCR Pipeline, from PDF input through OCR processing to optional AI analysis.

## Directory Structure

```
pdf-ocr-pipeline/
├── docs/                  # Documentation site source
│   ├── index.md           # Home page
│   ├── quickstart.md      # Minimal Quickstart guide
│   ├── usage_guide.md     # Full usage guide
│   ├── api.md             # API overview
│   ├── project_organization.md # This document
│   └── troubleshooting.md # Troubleshooting tips
├── examples/              # Example workflows and scripts
│   ├── process_dir.sh     # Batch directory processing
│   ├── ocr_and_analyze.sh  # Combined OCR + AI analysis script
│   └── programmatic_usage.py # Python integration example
├── src/                   # Source code
│   └── pdf_ocr_pipeline/  # Main package
│       ├── __init__.py    # Exports and process_pdf API
│       ├── __main__.py    # Entry point for `python -m pdf_ocr_pipeline`
│       ├── cli.py         # Command-line interface
│       ├── ocr.py         # Core OCR logic
│       ├── segmentation.py# Text segmentation routines
│       ├── summarize.py   # AI-powered text analysis
│       ├── llm_client.py  # LLM client abstraction
│       ├── logging_utils.py # Logging helper
│       ├── settings.py    # Pydantic configuration
│       ├── templates/     # External prompt templates
│       │   ├── segment_prompt.txt
│       │   └── gpt_system_prompt.txt
│       └── types.py       # TypedDicts and ProcessSettings
├── tests/                 # Test suite
│   ├── fixtures/          # Sample files for tests
│   │   ├── segmentation_golden.json
│   │   └── test_digital.pdf
│   ├── test_basic.py      # Package import tests
│   ├── test_cli.py        # CLI tests
│   ├── test_ocr.py        # OCR unit tests
│   ├── test_process_pdf.py # High-level API tests
│   ├── test_segmentation_golden.py # Segmentation golden tests
│   ├── test_summarize.py  # Summarizer unit tests
│   ├── test_end_to_end_llm.py # End-to-end AI tests
│   └── test_llm_stub.py   # HTTP stub tests
├── .github/              # GitHub Actions workflows
│   └── workflows/ci.yml  # CI pipeline configuration
├── Makefile              # Developer commands
├── pyproject.toml        # Build system & project metadata
├── setup.py              # setuptools installation entry point
├── setup.cfg             # Linter and formatter config
├── requirements-dev.txt  # Dev dependencies
├── requirements.lock     # Pinned dependencies
├── uv.lock               # uv environment lock
├── todos.md              # Implementation roadmap
└── README.md             # Project overview and quick examples
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
4. **Automation** with tox and Makefile
