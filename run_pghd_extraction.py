"""
Extract PGHD-related content from markdown files.

This script:
1. Defines PGHD-related search terms
2. Extracts paragraphs containing those terms from markdown files
3. Saves results to parquet and CSV files

Note: Run run_pdf_to_markdown.py first to convert PDFs to markdown.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_utils import (
    define_pghd_terms,
    extract_paragraphs_with_terms,
    create_and_save_dataframe,
)


def main():
    """Extract PGHD content from markdown files."""
    # Define paths
    project_root = Path(__file__).parent
    markdown_path = project_root / "data" / "processed" / "markdown"
    output_path = project_root / "data" / "processed" / "rule_based_extraction"
    
    # Check if markdown files exist
    if not markdown_path.exists() or not list(markdown_path.glob("*.md")):
        print("Error: No markdown files found!")
        print(f"Please run 'python run_pdf_to_markdown.py' first to convert PDFs.")
        return
    
    print("=" * 60)
    print("PGHD Extraction Pipeline")
    print("=" * 60)
    
    # Step 1: Define PGHD terms
    print("\n[Step 1/3] Defining PGHD search terms...")
    pghd_terms = define_pghd_terms()
    print(f"Defined {len(pghd_terms)} search terms")
    
    # Step 2: Extract paragraphs with terms
    print("\n[Step 2/3] Extracting paragraphs containing PGHD terms...")
    results = extract_paragraphs_with_terms(markdown_path, pghd_terms)
    
    # Step 3: Create and save dataframe
    print("\n[Step 3/3] Creating and saving dataframe...")
    df = create_and_save_dataframe(results, output_path)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
