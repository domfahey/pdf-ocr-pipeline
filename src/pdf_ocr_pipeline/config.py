"""
Configuration loader for PDF OCR Pipeline.
Loads JSON configuration from standard locations for API key, model, prompt, DPI, language, etc.
"""
import json
import os
from pathlib import Path

def load_config() -> dict:
    """
    Load JSON configuration from the first existing file.

    Search order (first match wins):
      - $XDG_CONFIG_HOME/pdf_ocr_pipeline/config.json
      - ~/.config/pdf_ocr_pipeline/config.json
      - ~/.pdf_ocr_pipeline/config.json
      - ./pdf_ocr_pipeline_config.json

    Returns:
        dict: Parsed configuration, or empty dict if none found.
    """
    candidates = [
        Path(os.getenv("XDG_CONFIG_HOME", "")) / "pdf_ocr_pipeline" / "config.json",
        Path.home() / ".config" / "pdf_ocr_pipeline" / "config.json",
        Path.home() / ".pdf_ocr_pipeline" / "config.json",
        Path.cwd() / "pdf_ocr_pipeline_config.json",
    ]
    for cfg in candidates:
        if cfg.is_file():
            try:
                return json.loads(cfg.read_text(encoding="utf-8"))
            except Exception:
                continue
    return {}

# Global configuration dictionary
_config = load_config()
