"""
Convert scientific paper PDFs to markdown files.

This script converts all PDFs in the disease folders to markdown format
using the marker package, preserving metadata about disease categories.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_utils import convert_pdfs_to_markdown


def main():
    """Convert PDFs to markdown."""
    # Define paths
    project_root = Path(__file__).parent
    raw_pdf_path = project_root / "data" / "raw" / "PDFs_update"
    markdown_path = project_root / "data" / "processed" / "markdown"
    
    print("=" * 60)
    print("PDF to Markdown Conversion")
    print("=" * 60)
    
    # Convert PDFs to markdown
    print("\nConverting PDFs to markdown...")
    convert_pdfs_to_markdown(raw_pdf_path, markdown_path)
    
    print("\n" + "=" * 60)
    print("Conversion completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
