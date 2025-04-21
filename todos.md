(completed items are checked)  

Step‑by‑step implementation roadmap  
(Each task is self‑contained and can be merged independently.)

- [x] **0. Baseline**  
  • Create “dev‑improvement” branch.  
  • Enable pre‑commit hooks locally (`pre-commit install`).  
  • Confirm all tests pass.

- [x] **1. Exception hierarchy**  
1.1 Add `pdf_ocr_pipeline/errors.py`  
 • `class PipelineError(Exception)`  
 • `class MissingBinaryError(PipelineError)`  
 • `class OcrError(PipelineError)`  
 • `class LlmError(PipelineError)`  
1.2 Refactor `ocr.py` and `summarize.py` to raise these instead of `sys.exit`.  
1.3 Update `cli.py` & `summarize.py` main functions to `except PipelineError` and call `sys.exit(1)`.  
1.4 Adjust unit‑tests to use `pytest.raises`.

- [x] **2. Typed data models**  
2.1 Create `pdf_ocr_pipeline/types.py`  
 • `TypedDict` / `dataclass` for `OcrResult`, `SegmentationDoc`, `SegmentationResult`.  
2.2 Annotate return types in `ocr.py`, `summarize.py`.  
2.3 Enable mypy `disallow_untyped_defs = True` only on `src/pdf_ocr_pipeline`.

- [x] **3. Settings via Pydantic**  
3.1 Add `settings.py`:

```python
from pydantic import BaseSettings, Field

class AppSettings(BaseSettings):
    dpi: int = 600
    lang: str = "eng"
    prompt: str = DEFAULT_PROMPT  # import from template (see step 4)
    openai_api_key: str = Field(env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"
```

3.2 Replace `_config` dict with a singleton `settings = AppSettings()`; adapt code.

- [x] **4. External prompt template**
4.1 Create `pdf_ocr_pipeline/templates/segment_prompt.txt` (current prompt).  
4.2 Load it with `importlib.resources.files("pdf_ocr_pipeline.templates").joinpath(...).read_text()` in `settings.py`.  
4.3 Remove long string from code → readability gain.

- [x] **5. Logging overhaul**  
5.1 Add helper `get_logger(name: str) -> logging.Logger` that sets formatter once and returns child loggers.  
5.2 Replace direct `logging.basicConfig` calls with this helper.  
5.3 Add `--quiet` / `--verbose` CLI flags that adjust root level only.

- [x] **6. Poppler behaviour detection**  
6.1 On first `ocr_pdf` call: run `pdftoppm -stdout-for-testing` tiny probe; cache result in module variable.  
6.2 Choose streaming or temp‑file path accordingly—no try/except every time.

- [x] **7. Cleaner subprocess helper**  
7.1 Enhance `run_cmd()` to accept `ok_exit_codes=(0,)`, capture stderr by default, raise `CalledProcessError` with decoded message.  
7.2 Centralise `shutil.which()` check at import time; raise MissingBinaryError early.

- [x] **8. LLM client abstraction**  
8.1 Create `pdf_ocr_pipeline/llm_client.py`  
 • Wrap OpenAI / Azure logic; expose `send(messages, model, **kw) -> dict`.  
8.2 `process_with_gpt()` becomes a thin wrapper around this client.

- [x] **9. Testing improvements**  
9.1 Use `pytest‑httpx` (or `respx`) to stub OpenAI endpoint; mark as “network” optional.  
9.2 Parametrize OCR tests with two fixtures: scanned PDF & digital‑text PDF.  
9.3 Add pact‑style golden JSON test for segmentation function with mocked LLM.

- [x] **10. Tooling polish**  
10.1 Switch Flake8 → Ruff in `.pre-commit-config.yaml` (`ruff check --fix`).  
10.2 Add `Makefile`:

```make
format:  ruff format . && black .
lint:    ruff check . && black --check .
test:    pytest -q
check:   lint test
```

10.3 Document dev workflow in `CONTRIBUTING.md`.

- [x] **11. Documentation**  
11.1 Add `docs/api/` with MkDocs‑Material; auto‑generate reference from docstrings.  
11.2 Write “Troubleshooting” page (Poppler 25, Tesseract langs, API key).

- [x] **12. CI pipeline**  
12.1 Enable GitHub Actions (or similar):  
 • matrix on py 3.8‑3.12  
 • jobs: lint (ruff), type‑check (mypy), tests, optional end‑to‑end (needs secret).  
12.2 Add pre‑commit.ci for automatic PR linting.

- [ ] **13. Higher‑level API**  
13.1 Implement `process_pdf(path, *, analyze=False, **settings) -> SegmentationResult | OcrResult`.  
13.2 Expose from package `__init__.py`; update README example code.

- **14. Gradual adoption schedule**  
• Weeks 1‑2 → steps 1‑4 (core reliability & clarity).  
• Week 3      → steps 5‑7 (performance, logging).  
• Week 4      → step 8 (client abstraction).  
• Week 5      → steps 9‑10 (tests & tooling).  
• Week 6      → steps 11‑13 (docs, CI, public API).

Each step is mergeable on its own; run `make check` before opening a PR.
