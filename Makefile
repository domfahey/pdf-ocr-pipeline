.PHONY: clean lint test type coverage install dev dist publish

# Variables
PYTHON = python3
PIP = $(PYTHON) -m pip
PYTEST = pytest
BLACK = black
FLAKE8 = flake8
MYPY = mypy

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(BLACK) src tests examples
	$(FLAKE8) src tests examples

test:
	$(PYTEST) tests/

type:
	$(MYPY) src

coverage:
	$(PYTEST) --cov=pdf_ocr_pipeline --cov-report=html tests/
	@echo "HTML coverage report generated in htmlcov/"

install:
	# Sync the project environment and install dependencies with uv
	uv sync

dev:
	# Sync the project environment including development dependencies
	uv sync --all-extras

dist:
	# Build source distributions and wheels with uv
	uv build

publish:
   # Publish distributions via uv (uses Twine under the hood)
   uv publish