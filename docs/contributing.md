# Contributing to PDF OCR Pipeline

We welcome contributions to PDF OCR Pipeline! This guide will help you get started.

## Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/pdf-ocr-pipeline.git
   cd pdf-ocr-pipeline
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Style

This project follows these code style guidelines:

- **Python version**: 3.8+
- **Line length**: 88 characters (Black)
- **Formatting**: Using Black and ruff
- **Type annotations**: Required for all functions
- **Docstrings**: Google style format

### Running Tests

```bash
# Run all tests
pytest

# Run a specific test
pytest tests/test_ocr.py

# Run with coverage
pytest --cov=pdf_ocr_pipeline tests/
```

### Quality Checks

```bash
# Code formatting
make format

# Linting
make lint

# Type checking
make typecheck

# Combined checks
make check
```

## Pull Request Process

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them with clear messages:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

3. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

4. **Push your branch** to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** against the main repository.

## Pull Request Guidelines

- Include tests for new functionality
- Update documentation when necessary
- Ensure all tests pass
- Follow the existing code style
- Keep PRs focused on a single change
- Rebase your branch if necessary

## Adding Documentation

Documentation is written in Markdown and built with MkDocs:

1. Add or update files in the `docs/` directory
2. Test locally with:
   ```bash
   mkdocs serve
   ```
3. View at http://localhost:8000

## Project Structure

Understanding the project organization will help you contribute effectively:

```
pdf-ocr-pipeline/
├── docs/                  # Documentation files
├── src/
│   └── pdf_ocr_pipeline/  # Source code
│       ├── __init__.py    # Package exports
│       ├── cli.py         # Command-line interface
│       ├── ocr.py         # OCR functionality
│       ├── segmentation.py# Text segmentation
│       └── summarize.py   # AI analysis
├── tests/                 # Test suite
└── examples/              # Example scripts
```

For a more detailed view, see the [Project Structure](project_organization.md) documentation.

## Getting Help

If you have questions or need help:

- **Open an issue** for bugs or features
- **Join our community discussions** for questions
- **Check existing issues and PRs** before creating new ones