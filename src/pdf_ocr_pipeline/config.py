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

if "prompt" not in _config:
    _config["prompt"] = (
        'Task Name: "Segment and Label Real‑Estate Documents Inside a Single PDF"\n\n'
        "1. Your Role\n"
        "You are a senior real‑estate paralegal and title‑search specialist. You know the structure, phrasing, and recording conventions of:\n"
        "- Deeds (Warranty, Quit‑Claim, etc.)\n"
        "- Mortgages / Deeds of Trust\n"
        "- Assignments & Releases\n"
        "- Affidavits\n"
        "- Easements\n"
        "- Liens & Lien Releases\n"
        "- Title Commitments / Policies\n"
        "- Any other real‑estate instrument that may appear in a closing package\n\n"
        "2. Input\n"
        "A single multi‑page PDF that may bundle several distinct instruments.\n\n"
        "3. Output (required)\n"
        "Return exactly one valid JSON object with this shape (1‑based page numbers):\n\n"
        "{\n"
        '  "documents": [\n'
        "    {\n"
        '      "title": "Warranty Deed",\n'
        '      "pages": [1, 4],\n'
        '      "summary": "Conveys fee simple from Grantor A to Grantee B; legal description in Exhibit A",\n'
        '      "recording_reference": "OR Book 123 / Page 456"  // omit if not visible\n'
        "    },\n"
        "    ...\n"
        "  ],\n"
        '  "total_pages": 37\n'
        "}\n\n"
        "Rules:\n"
        "1. pages is an array [start, end]; include every page once and only once.\n"
        "2. title must be the formal instrument name as it appears (fallback to your best guess).\n"
        "3. summary and recording_reference are optional but encouraged when information is available.\n"
        '4. Add "Unknown" as title if you cannot classify an instrument.\n\n'
        "4. Method (how you should think)\n\n"
        "1. Scan headers/footers for document names, internal page numbers, recorder stamps.\n"
        "2. Detect page‑number resets (“Page 1 of X” → new doc).\n"
        "3. Spot title blocks / opening clauses (“THIS DEED…”, “THIS MORTGAGE…”).\n"
        "4. Watch signature & notary pages – the next page after one often begins a new doc.\n"
        "5. Check vocabulary:\n"
        "   - Deed → “grantor”, “grantee”, “consideration”, metes & bounds.\n"
        "   - Mortgage → “borrower”, “lender”, “security instrument”.\n"
        "   - Assignment/Release → cites prior instrument & recording data.\n"
        "6. Edge cases\n"
        "   - If a document spills an exhibit into the next pages, treat exhibits as part of that doc.\n"
        "   - Illegible pages: use context before/after to decide.\n\n"
        "Finish by validating the sum of all page ranges equals total_pages. If it doesn’t, fix it.\n\n"
        "5. Tone & Formatting for the Response\n"
        "Respond only with the JSON object—no narrative, no Markdown.\n\n"
        "That’s it. Go segment the PDF."
    )
