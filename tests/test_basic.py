#!/usr/bin/env python3
"""
Basic test to verify the directory structure works.
"""

import unittest
import sys
import os

# Add src to the path so we can import the package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


class TestPackageImport(unittest.TestCase):
    """Test that the package can be imported."""

    def test_import(self):
        """Test importing the package."""
        try:
            import pdf_ocr_pipeline

            # Use the imported module to avoid unused import warning
            # Verify version exists
            self.assertIsNotNone(pdf_ocr_pipeline.__version__)
        except ImportError as e:
            self.fail(f"Failed to import package: {e}")


if __name__ == "__main__":
    unittest.main()
