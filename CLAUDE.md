# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
PDF OCR Pipeline: A Python tool that processes one or more PDF files through OCR using pdftoppm and tesseract, then analyzes the extracted text using OpenAI's GPT-4o model, outputting structured results as JSON.

## Build/Lint/Test Commands
- Install for development: `pip install -e .`
- Run the script: `pdf-ocr path/to/file1.pdf [path/to/file2.pdf ...] > output.json`
- Run the AI analysis: `pdf-ocr file.pdf | pdf-ocr-summarize --pretty > analysis.json`
- Testing: 
  - All tests: `python -m unittest discover tests`
  - Specific tests: `python -m unittest tests/test_summarize.py tests/test_pipeline.py`
- Linting commands:
  - `black src tests examples` - format code according to Black's style
  - `flake8 src tests examples` - check code quality
  - `mypy src` - verify type annotations
  - Run all linting: `make lint` (black + flake8)
  - Run all tests: `make test`
  - Run type checking: `make type`

## Testing Conventions
- Mock external dependencies (subprocess calls, stdin/stdout, OpenAI API)
- Use `unittest.mock.patch` for patching functions and context managers
- Exit conditions should be handled with try/except blocks when mocking sys.exit calls
- Tests should be isolated and not depend on external resources

## Dependencies
- Requires external tools: pdftoppm, tesseract
- Python dependencies in requirements.lock
- OpenAI Python client for GPT-4o integration
- Environment variable `OPENAI_API_KEY` must be set for summarization functionality

## Code Style Guidelines
- **Imports**: Standard library first, then third-party packages (grouped and alphabetized)
- **Formatting**: 4-space indentation, 88 character line limit (Black)
- **Types**: Type annotations for function parameters and return values
- **Naming**: snake_case for functions/variables, descriptive names
- **Error Handling**: Use try/except blocks with specific exceptions, logging for errors
- **Function Structure**: Small, focused functions with comprehensive docstrings
- **Documentation**: Google-style docstrings including Args, Returns, and Exits sections

## Additional Notes
- Command-line tools that output JSON to stdout
- Modular design supporting pipelines for advanced workflows
- Two main components: OCR extraction and AI analysis
- Error messages are logged and written to stderr
- Exit codes used to signal errors
- Supports multiple input files, processing them sequentially
- Requires an OpenAI API key for AI analysis features