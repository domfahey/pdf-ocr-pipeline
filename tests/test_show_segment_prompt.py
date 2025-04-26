"""
Test to display the current segmentation prompt loaded by default.
Run with `pytest -s` to see the prompt printed to stdout.
"""

import sys
import os

# Ensure local src directory is first in import path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from pdf_ocr_pipeline.settings import settings


def test_show_segment_prompt():
    """
    Ensure the default segmentation prompt is loaded into settings and print it.
    """
    prompt = settings.prompt
    # Print the prompt so it can be inspected when running pytest with -s
    print("\n=== Current segmentation prompt ===\n")
    print(prompt)
    print("\n=== End of prompt ===\n")
    # Basic sanity check: prompt should not be empty
    assert prompt, "Expected non-empty segmentation prompt"
