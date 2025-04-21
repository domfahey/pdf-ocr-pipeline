(completed items are checked)  

Step‑by‑step implementation roadmap  
(Each task is self‑contained and can be merged independently.)

- [x] **0. Baseline**
  - [x] Create “dev‑improvement” branch.
  - [x] Enable pre‑commit hooks locally (`pre-commit install`).
  - [x] Confirm all tests pass.

- [x] **1. Exception hierarchy**
  - [x] 1.1 Add `pdf_ocr_pipeline/errors.py`
  - [x] 1.1.1 `class PipelineError(Exception)`
  - [x] 1.1.2 `class MissingBinaryError(PipelineError)`
  - [x] 1.1.3 `class OcrError(PipelineError)`
  - [x] 1.1.4 `class LlmError(PipelineError)`
  - [x] 1.2 Refactor `ocr.py` and `summarize.py` to raise these instead of `sys.exit`.
  - [x] 1.3 Update `cli.py` & `summarize.py` main functions to `except PipelineError` and call `sys.exit(1)`.
  - [x] 1.4 Adjust unit‑tests to use `pytest.raises`.

- [x] **2. Typed data models**
  - [x] 2.1 Create `pdf_ocr_pipeline/types.py`
  - [x] 2.1.1 `TypedDict` / `dataclass` for `OcrResult`, `SegmentationDoc`, `SegmentationResult`.
  - [x] 2.2 Annotate return types in `ocr.py`, `summarize.py`.
  - [x] 2.3 Enable mypy `disallow_untyped_defs = True` only on `src/pdf_ocr_pipeline`.

 - [x] **3. Settings via Pydantic**
  - [x] 3.1 Add `settings.py`

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

  - [x] 3.2 Replace `_config` dict with a singleton `settings = AppSettings()`; adapt code.

- [x] **4. External prompt template**
  - [x] 4.1 Create `pdf_ocr_pipeline/templates/segment_prompt.txt` (current prompt).
  - [x] 4.2 Load it with `importlib.resources.files("pdf_ocr_pipeline.templates").joinpath(...).read_text()` in `settings.py`.
  - [x] 4.3 Remove long string from code → readability gain.

- [x] **5. Logging overhaul**
  - [x] 5.1 Add helper `get_logger(name: str) -> logging.Logger` that sets formatter once and returns child loggers.
  - [x] 5.2 Replace direct `logging.basicConfig` calls with this helper.
  - [x] 5.3 Add `--quiet` / `--verbose` CLI flags that adjust root level only.

- [x] **6. Poppler behaviour detection**
  - [x] 6.1 On first `ocr_pdf` call: run `pdftoppm -stdout-for-testing` tiny probe; cache result in module variable.
  - [x] 6.2 Choose streaming or temp‑file path accordingly—no try/except every time.

- [x] **7. Cleaner subprocess helper**
  - [x] 7.1 Enhance `run_cmd()` to accept `ok_exit_codes=(0,)`, capture stderr by default, raise `CalledProcessError` with decoded message.
  - [x] 7.2 Centralise `shutil.which()` check at import time; raise MissingBinaryError early.

- [x] **8. LLM client abstraction**
  - [x] 8.1 Create `pdf_ocr_pipeline/llm_client.py`
  - [x] 8.1.1 Wrap OpenAI / Azure logic; expose `send(messages, model, **kw) -> dict`.
  - [x] 8.2 `process_with_gpt()` becomes a thin wrapper around this client.

- [x] **9. Testing improvements**
  - [x] 9.1 Use `pytest‑httpx` (or `respx`) to stub OpenAI endpoint; mark as “network” optional.
  - [x] 9.2 Parametrize OCR tests with two fixtures: scanned PDF & digital‑text PDF.
  - [x] 9.3 Add pact‑style golden JSON test for segmentation function with mocked LLM.

  - [x] 10.1 Switch Flake8 → Ruff in `.pre-commit-config.yaml` (`ruff check --fix`).
  - [x] 10.2 Add `Makefile`:

  ```make
  format:  ruff format . && black .
  lint:    ruff check . && black --check .
  test:    pytest -q
  check:   lint test
  ```

  - [x] 10.3 Document dev workflow in `CONTRIBUTING.md`.

- [x] **11. Documentation**
  - [x] 11.1 Add `docs/api/` with MkDocs‑Material; auto‑generate reference from docstrings.
  - [x] 11.2 Write “Troubleshooting” page (Poppler 25, Tesseract langs, API key).

- [x] **12. CI pipeline**
  - [x] 12.1 Enable GitHub Actions (or similar): matrix on py 3.8‑3.12; jobs: lint (ruff), type‑check (mypy), tests, optional end‑to‑end (needs secret).
  - [x] 12.2 Add pre‑commit.ci for automatic PR linting.

- [x] **13. Higher‑level API**
  - [x] 13.1 Implement `process_pdf(path, *, analyze=False, **settings) -> SegmentationResult | OcrResult`.
  - [x] 13.2 Expose from package `__init__.py`; update README example code.

- **14. Gradual adoption schedule**  
• Weeks 1‑2 → steps 1‑4 (core reliability & clarity).  
• Week 3      → steps 5‑7 (performance, logging).  
• Week 4      → step 8 (client abstraction).  
• Week 5      → steps 9‑10 (tests & tooling).  
• Week 6      → steps 11‑13 (docs, CI, public API).

Each step is mergeable on its own; run `make check` before opening a PR.

-------------------------------------------------------------------

## ✨ Backlog / Follow‑up Improvements (post‑v0.2) – *open*

These items were identified during a second‑pass review.  They are **not**
required for the current milestone but would further improve quality and
maintainability.

1. **API / Public surface**
   • Replace the growing `process_pdf()` parameter list with a `ProcessSettings` dataclass.  
   • Switch `__all__` to a lazy `__getattr__` pattern to avoid manual sync.  
   • Refine `SegmentationResult` typing – represent page range as `Tuple[int, int]`.

2. **Logging**  
   • In `logging_utils.get_logger` configure only the handler; leave the root
     level unchanged unless a dedicated `set_root_level(level)` helper is
     called (used by CLI).

3. **LLM client**  
   • Add thread‑safe lock around the singleton factory.  
   • Re‑raise `KeyboardInterrupt` / `BaseException` in `send()`.  
   • Guard against missing `choices[0].message.content` with a clearer error.

4. **OCR path**  
   • Consider defaulting `run_cmd(capture_output=False)` and setting pipes at call‑sites.  
   • Replace on‑disk *probe.pdf* with `NamedTemporaryFile` in `_detect_streaming_support()` and pass `-singlefile -f 1 -l 1`.

5. **CLI flags**  
   • Short‑circuit summarizer when OCR text empty so no API key needed.  
   • Replace `--quiet` with `--log-level {DEBUG,INFO,WARNING,ERROR}`.

6. **Tests & CI**  
   • Add `pytest‑httpx` to dev‑extras so stub tests aren’t skipped in CI.  
   • Run *mypy* inside `make check` and pre‑commit (`--strict`).

7. **Packaging / Distribution**  
   • Remove obsolete `[tool.flake8]` section from *pyproject.toml*.  
   • Delete redundant *bin/ocr_pipe.py* wrapper; rely on console‑scripts.  
   • Provide an `[llm]` extras‑require for OpenAI/litellm.

8. **Documentation**  
   • Remove hard‑coded `site_url` from *mkdocs.yml*; add Quickstart page mirroring `process_pdf` usage.

Nice‑to‑haves / future research  
   • Asyncio‑based OCR pipeline.  
   • Stream‑friendly PNG + NamedTemporaryFile approach.  
   • Dataclass/attrs result objects for IDE auto‑completion.

