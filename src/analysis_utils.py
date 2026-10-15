"""Analysis utilities for rule-based PGHD extraction results."""

from pathlib import Path
from typing import List, Optional
import pandas as pd


def count_term_frequencies(
    results_file: Path,
    keywords: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Count the frequency of each matched term in the extraction results.
    
    Args:
        results_file: Path to the extraction results (parquet or csv)
        keywords: Optional list of specific keywords to count. If None, counts all terms.
    
    Returns:
        DataFrame with columns: term, unique_papers, paragraph_count, sorted by unique_papers descending
    """
    # Read results file
    if results_file.suffix == '.parquet':
        df = pd.read_parquet(results_file)
    else:
        df = pd.read_csv(results_file)
    
    # Filter out rows with no matches
    df_matched = df[df['matched_terms'].notna()].copy()
    
    # Create a list to store term data
    term_data = []
    
    # Process each row to extract terms and associated paper IDs
    for _, row in df_matched.iterrows():
        paper_id = row['paper_pdf_id']
        terms_str = row['matched_terms']
        
        # Split by comma and strip whitespace
        terms = [term.strip() for term in terms_str.split(',')]
        
        for term in terms:
            term_data.append({'term': term, 'paper_id': paper_id})
    
    # Create DataFrame from term data
    term_df = pd.DataFrame(term_data)
    
    # Group by term and calculate counts
    term_counts = term_df.groupby('term').agg(
        unique_papers=('paper_id', 'nunique'),
        paragraph_count=('paper_id', 'count')
    ).reset_index()
    
    # Sort by unique_papers descending
    term_counts = term_counts.sort_values('unique_papers', ascending=False)
    
    # Filter to specific keywords if provided
    if keywords:
        # Convert keywords to lowercase for case-insensitive matching
        keywords_lower = [k.lower() for k in keywords]
        term_counts = term_counts[term_counts['term'].str.lower().isin(keywords_lower)]
    
    return term_counts


def filter_by_keywords(
    results_file: Path,
    keywords: List[str],
    output_file: Optional[Path] = None
) -> pd.DataFrame:
    """
    Filter extraction results to rows containing any of the specified keywords.
    
    Args:
        results_file: Path to the extraction results (parquet or csv)
        keywords: List of keywords to filter by
        output_file: Optional path to save filtered results (parquet or csv)
    
    Returns:
        Filtered DataFrame containing only rows with matching keywords
    """
    # Read results file
    if results_file.suffix == '.parquet':
        df = pd.read_parquet(results_file)
    else:
        df = pd.read_csv(results_file)
    
    # Filter out rows with no matches
    df_matched = df[df['matched_terms'].notna()].copy()
    
    # Convert keywords to lowercase for case-insensitive matching
    keywords_lower = [k.lower() for k in keywords]
    
    # Filter rows where matched_terms contains any of the keywords
    def contains_keyword(terms_str):
        if pd.isna(terms_str):
            return False
        terms = [term.strip().lower() for term in terms_str.split(',')]
        return any(term in keywords_lower for term in terms)
    
    filtered_df = df_matched[df_matched['matched_terms'].apply(contains_keyword)]
    
    # Save to file if output path provided
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        if output_file.suffix == '.parquet':
            filtered_df.to_parquet(output_file, index=False)
        else:
            filtered_df.to_csv(output_file, index=False)
        print(f"✓ Saved filtered results to {output_file}")
    
    return filtered_df


def get_term_statistics(
    results_file: Path,
    keywords: Optional[List[str]] = None
) -> dict:
    """
    Get comprehensive statistics about matched terms.
    
    Args:
        results_file: Path to the extraction results (parquet or csv)
        keywords: Optional list of specific keywords to analyze
    
    Returns:
        Dictionary with statistics including:
        - total_papers: total number of papers
        - papers_with_matches: papers with any matches
        - total_paragraphs: total matched paragraphs
        - unique_terms: number of unique terms matched
        - term_frequencies: DataFrame of term counts
    """
    # Read results file
    if results_file.suffix == '.parquet':
        df = pd.read_parquet(results_file)
    else:
        df = pd.read_csv(results_file)
    
    # Get term frequencies
    term_freq = count_term_frequencies(results_file, keywords)
    
    # Calculate statistics
    stats = {
        'total_papers': df['paper_pdf_id'].nunique(),
        'papers_with_matches': df[df['matched_terms'].notna()]['paper_pdf_id'].nunique(),
        'total_paragraphs': df['matched_paragraph'].notna().sum(),
        'unique_terms': len(term_freq),
        'term_frequencies': term_freq
    }
    
    return stats
