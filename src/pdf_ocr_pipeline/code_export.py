#!/usr/bin/env python3
"""
Export all Python code to Markdown for AI analysis.
"""
import argparse
import sys
from pathlib import Path


def export_markdown(root: Path) -> str:
    """
    Walk the project directory from 'root', collecting .py files,
    and return a Markdown-formatted string with code fences.
    """
    parts = []
    for path in sorted(root.rglob("*.py")):
        # Skip __pycache__ directories
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root)
        parts.append(f"## File: {rel}\n```python")
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            content = f"# Error reading file: {e}"
        parts.append(content)
        parts.append("```\n")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export project Python code to Markdown"
    )
    parser.add_argument(
        "-r", "--root", type=Path, default=Path("."), help="Project root"
    )
    parser.add_argument("-o", "--output", type=Path, help="Output .md file")
    args = parser.parse_args()

    md = export_markdown(args.root)
    if args.output:
        args.output.write_text(md, encoding="utf-8")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
