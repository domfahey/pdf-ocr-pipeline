(completed items are checked)  

Step‑by‑step implementation roadmap  
(Each task is self‑contained and can be merged independently.)

- [x] **0. Baseline**  
  • Create “dev‑improvement” branch.  
  • Enable pre‑commit hooks locally (`pre-commit install`).  
  • Confirm all tests pass.

- [x] **1. Exception hierarchy**  
  … *(content unchanged)* …

- [x] **13. Higher‑level API**  
  - [x] 13.1 Implement `process_pdf(path, *, analyze=False, **settings)` returning typed result.  
  - [x] 13.2 Export from package; update README.

- **14. Gradual adoption schedule** *(historical)*

Each step above is mergeable on its own; run `make check` before opening a PR.

-------------------------------------------------------------------

## ✨ Backlog / Follow‑up Improvements (post‑v0.2) – *open*

Below items were identified in a second‑pass review.  None block release but
they will tighten quality and UX.  Every bullet lists **Why → Where → How →
Done‑when** to guide implementers.

### 15 API / Public surface

- [x] **15.1 `ProcessSettings` dataclass**  
  • *Why* prevent parameter creep in `process_pdf`.  
  • *Where* `src/pdf_ocr_pipeline/__init__.py`.  
  • *How* introduce frozen `@dataclass(slots=True)` with defaults; allow passing
    `cfg` param; raise on mixed usage.  
  • *Done‑when* new tests cover cfg path; old signature still works.

- [x] **15.2 Lazy exports** (`__getattr__`)  
  • *Why* remove manual `__all__` sync.  
  • *How* see code snippet in backlog description.  
  • *Done‑when* mypy passes with new import style.

- [x] **15.3 Segmentation typing** – use `Tuple[int, int]` for `pages`.

### 16 Logging

- [x] Configure only handler in `get_logger`; add `set_root_level`.  
  *Done‑when* CLI honours `--log-level`, `--verbose`/`--quiet` flags via `set_root_level`.

### 17 LLM client

- [ ] Thread‑safe singleton lock.  
- [ ] Re‑raise `KeyboardInterrupt` / `BaseException`.  
- [ ] Validate response schema.

### 18 OCR path

- [ ] Default `run_cmd(capture_output=False)`; update callers.  
- [ ] Replace on‑disk probe with `NamedTemporaryFile`; pass `-singlefile -f1 -l1`.

### 19 CLI polish

- [ ] Summarizer early‑exit when OCR text empty.  
- [ ] Replace `--quiet/‑v` with `--log-level {DEBUG,INFO,WARNING,ERROR}`.

### 20 Tests & CI

- [ ] Add `pytest‑httpx` to dev extra; ensure CI installs.  
- [ ] Run `mypy --strict` in Makefile `check` and pre‑commit.

### 21 Packaging / Distribution

- [ ] Remove `[tool.flake8]` from *pyproject.toml*.  
- [ ] Drop redundant `bin/ocr_pipe.py`; rely on console‑scripts.  
- [ ] Provide `[llm]` and `[doc]` extras.

### 22 Documentation

- [ ] Remove hard‑coded `site_url` from mkdocs.yml.  
- [ ] Add **Quickstart** page showing new settings dataclass.

### 23 Future R&D ideas (parking lot)

- Asyncio‑based OCR.  
- PNG raster + NamedTemporaryFile flow.  
- Convert results to attrs/pydantic models for IDE autocompletion.  
- End-to-end integration tests  
- Caching & incremental runs  
- Docker / container support  
- REST API / server mode  
- Metrics & monitoring  
- PDF-specific pre-processing  
- Encrypted PDF handling  
- UI-driven segmentation feedback  
- Strict type coverage & linting  
