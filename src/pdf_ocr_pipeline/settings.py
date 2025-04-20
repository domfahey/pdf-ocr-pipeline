"""Application‑wide configuration using *Pydantic* settings.

This replaces the loose ``_config`` dictionary previously loaded from an INI
file while remaining 100 % backward compatible: existing code can still import
``pdf_ocr_pipeline.config._config`` but new code should read from the typed
singleton :data:`settings` defined below.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Pydantic v2 split BaseSettings into separate package; support both.
try:
    # Pydantic v2 recommended package
    from pydantic_settings import BaseSettings  # type: ignore
except ImportError:  # pragma: no cover – fall back for environments w/o extra pkg
    # Pydantic <2.0 ships BaseSettings in core; in >=2.0 it was split out. We
    # attempt to import it and if unavailable create a minimal shim that at
    # least honours environment variables.
    try:
        from pydantic import BaseSettings  # type: ignore
    except (ImportError, AttributeError):  # pragma: no cover
        from pydantic import BaseModel

        class BaseSettings(BaseModel):  # type: ignore
            """Very small subset replacement for missing BaseSettings."""

            class Config:
                @classmethod
                def customise_sources(cls, settings_cls, init_settings, env_settings, file_secret_settings):  # noqa: E501
                    return env_settings, init_settings

from pydantic import Field

# ---------------------------------------------------------------------------
# Fallback: reuse the INI‑based loader so we respect legacy overrides.
# ---------------------------------------------------------------------------

try:
    from .config import _config  # noqa: WPS433  (allowed internal import)
except ImportError:  # pragma: no cover – tests always have config module
    _config: dict[str, Any] = {}


class AppSettings(BaseSettings):
    """Typed settings pulled from environment variables or legacy INI file."""

    # OCR defaults
    dpi: int = _config.get("dpi", 600)
    lang: str = _config.get("lang", "eng")

    # Prompt used by the summarizer / LLM step
    prompt: str = _config.get("prompt", "")

    # Verbosity default for CLI tools
    verbose: bool = _config.get("verbose", False)

    # pretty‑print default for summarize CLI
    pretty: bool = _config.get("pretty", False)

    # OpenAI credentials & endpoint overrides
    openai_api_key: str = Field("", env="OPENAI_API_KEY")
    api_base: str | None = _config.get("api_base")
    api_version: str | None = _config.get("api_version")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "PDF_OCR_"


# Singleton instance – import this from other modules
settings = AppSettings()
