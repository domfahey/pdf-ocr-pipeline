# AGENTS.md

This repository hosts the PDF OCR Pipeline project. The following guidelines summarize how automated agents should interact with the codebase.

## References
- **CLAUDE.md** – build/test commands and code style expectations.
- **CONTRIBUTING.md** and `docs/contributing.md` – workflow and pull request process.
- **README.md** – installation steps and external dependencies.
- **Makefile** – common developer commands.
- **todos.md** – roadmap notes; run `make check` before opening a PR.

## Key Practices
1. **Environment Setup**
   - Use Python 3.8+.
   - Install dependencies with `uv sync --all-extras`.
   - Optional: enable pre-commit hooks via `uv run pre-commit install`.
2. **Formatting and Linting**
   - Format code with `ruff format .` then `black .`.
   - Lint with `ruff check .`.
   - Both steps can be run together using `make format` and `make lint`.
3. **Testing**
   - Run `pytest` or `make test` to execute the suite.
   - Use `pytest --cov=pdf_ocr_pipeline tests/` for coverage.
   - The `make check` target runs linting and tests; ensure it passes before committing.
4. **Code Style**
   - Follow strict type annotations; see `CLAUDE.md` and `pyproject.toml` for mypy settings.
   - Use Google‑style docstrings and group imports by standard library, third‑party, then local.
   - Avoid `sys.exit()` in library code; prefer custom exceptions from `errors.py`.
5. **Pull Requests**
   - Branch from `main` and commit with clear messages (see `CONTRIBUTING.md`).
   - Include tests for new features and update documentation in `docs/` or `README.md` when needed.

Automated agents should read these documents before modifying the repository and always run the checks described above.
