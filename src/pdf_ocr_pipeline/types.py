"""Typed helper definitions used across *pdf_ocr_pipeline*.

These are **pure type‑hints** so they do not add runtime overhead.  They help
static analysers (mypy / Pyright) catch key‑name typos and improper data
shapes while keeping the public interface 100‑% JSON‑serialisable.
"""

from __future__ import annotations

from typing import TypedDict, List


class OcrResult(TypedDict):
    """Result object produced by the CLI after OCR only."""

    file: str
    ocr_text: str


class SegmentationDoc(TypedDict, total=False):
    """Single document segment inside a multi‑page PDF."""

    title: str
    pages: List[int]
    summary: str
    recording_reference: str


class SegmentationResult(TypedDict):
    """Top‑level JSON object returned by LLM prompt."""

    documents: List[SegmentationDoc]
    total_pages: int
