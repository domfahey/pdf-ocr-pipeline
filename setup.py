#!/usr/bin/env python3
"""
Setup script for the PDF OCR Pipeline.
"""

from setuptools import setup, find_packages

# Read version from package __init__.py
with open("src/pdf_ocr_pipeline/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pdf-ocr-pipeline",
    version=version,
    author="PDF OCR Pipeline Contributors",
    author_email="your.email@example.com",
    description="A tool to extract text from PDF documents using OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-ocr-pipeline",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/pdf-ocr-pipeline/issues",
        "Documentation": "https://github.com/yourusername/pdf-ocr-pipeline#readme",
        "Source Code": "https://github.com/yourusername/pdf-ocr-pipeline",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "openai>=1.75.0",  # Required for GPT-4o integration
    ],
    entry_points={
        "console_scripts": [
            "pdf-ocr=pdf_ocr_pipeline.cli:main",
            "pdf-ocr-summarize=pdf_ocr_pipeline.summarize:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
    ],
)
