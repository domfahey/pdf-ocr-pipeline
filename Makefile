# Developer shortcuts -------------------------------------------------

.PHONY: format lint test check

# Use the same Python that is running this script (assumes virtualenv/uv)
ifneq ($(wildcard .venv/bin/python),)
PY := .venv/bin/python
else
PY := python3
endif

format:
	@echo "Running ruff format and black …"
	@$(PY) -m ruff format .
	@$(PY) -m black .

lint:
	@echo "Running ruff check and black --check …"
	@$(PY) -m ruff check .
	@$(PY) -m black --check .

test:
	@echo "Running pytest …"
	@$(PY) -m pytest -q

check: lint test
	@echo "All checks passed ✔"
