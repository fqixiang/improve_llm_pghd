"""
Analyze rule-based PGHD extraction results.

This script provides two main analysis functions:
1. Count term frequencies (optionally filtering to specific keywords)
2. Filter results by keywords
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analysis_utils import (
    count_term_frequencies,
    filter_by_keywords,
    get_term_statistics,
)


def main():
    """Run analysis on extraction results."""
    # Define paths
    project_root = Path(__file__).parent
    results_file = project_root / "data" / "processed" / "rule_based_extraction" / "pghd_extraction_results.parquet"
    
    # Check if results file exists
    if not results_file.exists():
        print(f"Error: Results file not found at {results_file}")
        print("Please run 'python run_pghd_extraction.py' first.")
        return
    
    print("=" * 60)
    print("PGHD Extraction Results Analysis")
    print("=" * 60)
    
    # Example 1: Get overall statistics
    print("\n[Analysis 1] Overall Statistics")
    print("-" * 60)
    stats = get_term_statistics(results_file)
    print(f"Total papers: {stats['total_papers']}")
    print(f"Papers with matches: {stats['papers_with_matches']}")
    print(f"Total matched paragraphs: {stats['total_paragraphs']}")
    print(f"Unique terms matched: {stats['unique_terms']}")
    
    # Example 2: Count all term frequencies
    print("\n[Analysis 2] All Term Frequencies (Top 20)")
    print("-" * 60)
    term_freq = count_term_frequencies(results_file)
    print(term_freq.head(20).to_string(index=False))
    
    # Example 3: Count specific keywords
    print("\n[Analysis 3] Specific Keywords Frequency")
    print("-" * 60)
    filter_keywords = [
        "patient-generated health data",
        "patient generated health data",
        "pghd",
    ]
    specific_freq = count_term_frequencies(results_file, keywords=filter_keywords)
    print(specific_freq.to_string(index=False))
    
    # Example 4: Filter by keywords and save
    print("\n[Analysis 4] Filter by Keywords")
    print("-" * 60)
    output_file = project_root / "data" / "processed" / "rule_based_extraction" / "pghd_filtered_results.csv"
    
    filtered_df = filter_by_keywords(results_file, filter_keywords, output_file)
    print(f"Filtered to {len(filtered_df)} paragraphs containing pghd-specific terms")
    print(f"From {filtered_df['paper_pdf_id'].nunique()} unique papers")
    
    # Save all term frequencies to CSV
    freq_output = project_root / "data" / "processed" / "rule_based_extraction" / "term_frequencies.csv"
    term_freq.to_csv(freq_output, index=False)
    print(f"\n✓ Saved all term frequencies to {freq_output}")
    
    print("\n" + "=" * 60)
    print("Analysis completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
