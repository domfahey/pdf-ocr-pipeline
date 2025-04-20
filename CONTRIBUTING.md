# Contributing to PDF OCR Pipeline

Thank you for considering contributing to the PDF OCR Pipeline project! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

## Code of Conduct

This project and everyone participating in it are governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork to your local machine
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes and commit them with clear messages
6. Push your changes to your fork
7. Submit a pull request

## Development Environment

### Prerequisites
- Python 3.6 or higher
- pdftoppm (from poppler-utils)
- tesseract OCR engine
- OpenAI API key (for AI-related features)

### Setting Up the Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-ocr-pipeline.git
   cd pdf-ocr-pipeline
   ```

2. Install the uv package manager (if not already installed) and synchronize the environment:
   ```bash
   pip install uv
   uv sync --all-extras
   ```

3. (Optional) Set up pre-commit hooks for code quality:
   ```bash
   uv run pre-commit install
   ```

## Pull Request Process

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes.

3. Run the linting tools:
   ```bash
   black src tests examples
   flake8 src tests examples
   mypy src
   ```

4. Run the tests:
   ```bash
   python -m unittest discover tests
   ```

5. Update the documentation if needed.

6. Commit your changes with a clear and descriptive commit message:
   ```bash
   git commit -m "Add feature: description of the feature"
   ```

7. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Submit a pull request to the main repository.

## Code Style Guidelines

This project follows these coding standards:

- **Formatting**: We use Black with a line length of 88 characters
- **Style**: PEP 8 guidelines with some exceptions defined in setup.cfg
- **Type Annotations**: All functions should have proper type annotations
- **Docstrings**: Google-style docstrings for all modules, classes, and functions
- **Imports**: Standard library first, then third-party packages, grouped and alphabetized

## Testing Guidelines

- All new features must include tests
- Maintain or improve test coverage with any changes
- Tests should be independent and not rely on external services
- Mock external dependencies like OpenAI API and subprocess calls
- Organize tests by module/functionality

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test modules
python -m unittest tests/test_summarize.py tests/test_pipeline.py

# Run with coverage
python -m pytest --cov=pdf_ocr_pipeline tests/
```

## Documentation Guidelines

- Update the README.md for any user-facing changes
- Add or update API documentation in docs/api_reference.md
- Update the usage guide in docs/usage_guide.md for new features
- Add examples where appropriate
- Document any new dependencies or requirements

Thank you for contributing to PDF OCR Pipeline!