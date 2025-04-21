"""
Optional configuration fallback for PDF OCR Pipeline CLI.
This module provides a compatibility layer for legacy config import.
"""

import configparser
from pathlib import Path

# Global dictionary for configuration values.
_config: dict = {}


def _load_config():
    """
    Load configuration from INI files. Looks for 'pdf-ocr-pipeline.ini'
    in the current directory or '~/.pdf-ocr-pipeline.ini'.
    Supported keys in the [pdf-ocr-pipeline] section:
      dpi (int), lang (str), verbose (bool)
    """
    parser = configparser.ConfigParser()
    # Potential config file location (project directory only)
    path = Path.cwd() / "pdf-ocr-pipeline.ini"
    if path.is_file():
        try:
            parser.read(path)
        except Exception:
            return
    section = "pdf-ocr-pipeline"
    if not parser.has_section(section):
        return
    # Parse integer dpi
    if parser.has_option(section, "dpi"):
        try:
            _config["dpi"] = parser.getint(section, "dpi")
        except ValueError:
            pass
    # Parse language
    if parser.has_option(section, "lang"):
        _config["lang"] = parser.get(section, "lang")
    # Parse default prompt for summarization
    if parser.has_option(section, "prompt"):
        _config["prompt"] = parser.get(section, "prompt")
    # Parse model name for summarization
    if parser.has_option(section, "model"):
        _config["model"] = parser.get(section, "model")
    # Parse pretty default output formatting
    if parser.has_option(section, "pretty"):
        try:
            _config["pretty"] = parser.getboolean(section, "pretty")
        except ValueError:
            pass
    # Parse API base endpoint (e.g., for OpenAI)
    if parser.has_option(section, "api_base"):
        _config["api_base"] = parser.get(section, "api_base")
    # Parse API version
    if parser.has_option(section, "api_version"):
        _config["api_version"] = parser.get(section, "api_version")
    # Parse verbose flag
    if parser.has_option(section, "verbose"):
        try:
            _config["verbose"] = parser.getboolean(section, "verbose")
        except ValueError:
            pass


_load_config()

# ---------------------------------------------------------------------------
# Built‑in defaults that can be overridden by the on‑disk
# `pdf-ocr-pipeline.ini`.  Placing them here allows *all* entry points
# (cli, summarize, etc.) to share the same values without duplicating the
# strings in multiple modules.
# ---------------------------------------------------------------------------

# Default prompt now stored externally (see templates/segment_prompt.txt).
# Keep empty string here so legacy ``_config.get("prompt")`` calls succeed.
if "prompt" not in _config:
    _config["prompt"] = ""
