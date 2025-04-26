# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Run all tests: `make test` or `pytest`
- Run single test: `pytest tests/test_file.py::TestClass::test_name`
- Test with coverage: `pytest --cov=pdf_ocr_pipeline tests/`
- Format code: `make format`
- Lint code: `make lint`
- Combined check: `make check`

## Code Style Guidelines
- Python 3.8+ with strict type annotations (mypy)
- Line length: 88 characters (Black)
- Formatting: ruff format followed by Black
- Imports: stdlib first, then third-party, grouped alphabetically
- Types: Full annotation required, use `TypedDict`, `dataclasses`, from `__future__` import annotations
- Naming: snake_case (variables/functions), PascalCase (classes), ALL_CAPS (constants)
- Error handling: Use custom exceptions from `errors.py`, never use `sys.exit()` in library code
- Docstrings: Google style format with clear parameter and return type documentation