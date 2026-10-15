"""Functions for extracting PGHD-related content from medical literature."""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from tqdm import tqdm


def convert_pdfs_to_markdown(
    raw_pdf_base_path: Path,
    output_markdown_path: Path
) -> None:
    """
    Convert all PDFs in the disease folders to markdown files.
    
    Args:
        raw_pdf_base_path: Base path containing disease folders
        output_markdown_path: Path to save converted markdown files
    """
    # Create output directory
    output_markdown_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize marker model
    model_dict = create_model_dict()
    converter = PdfConverter(artifact_dict=model_dict)
    
    # Find all PDF files recursively in any subfolder
    pdf_files = list(raw_pdf_base_path.rglob('*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files to convert")
    
    # Convert each PDF to markdown
    for pdf_path in tqdm(pdf_files, desc="Converting PDFs", unit="file"):
        try:
            # Get disease topics from path
            path_parts = pdf_path.parts
            # Find the base path index (either 'PDFs' or 'PDFs_update')
            base_idx = None
            for i, part in enumerate(path_parts):
                if part in ['PDFs', 'PDFs_update']:
                    base_idx = i
                    break
            
            disease_main_topic = path_parts[base_idx + 1] if base_idx is not None and base_idx + 1 < len(path_parts) else "Unknown"
            
            # Determine if there's a sub-topic (excluding FT-related folders)
            disease_sub_topic = None
            if base_idx is not None and base_idx + 2 < len(path_parts):
                potential_sub = path_parts[base_idx + 2]
                # Exclude FT-related folders and the PDF filename itself
                if (potential_sub != pdf_path.name and 
                    'FT' not in potential_sub.upper()):
                    disease_sub_topic = potential_sub
            
            # Create output filename
            pdf_id = pdf_path.stem
            output_file = output_markdown_path / f"{pdf_id}.md"
            
            # Skip if already converted
            if output_file.exists():
                tqdm.write(f"Skipping {pdf_id} (already converted)")
                continue
            
            tqdm.write(f"Converting {pdf_id}...")
            
            # Convert PDF to markdown
            rendered = converter(str(pdf_path))
            markdown_text, _, _ = text_from_rendered(rendered)
            
            # Save markdown file with metadata header
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"<!-- PDF_ID: {pdf_id} -->\n")
                f.write(f"<!-- DISEASE_MAIN_TOPIC: {disease_main_topic} -->\n")
                f.write(f"<!-- DISEASE_SUB_TOPIC: {disease_sub_topic if disease_sub_topic else 'NA'} -->\n\n")
                f.write(markdown_text)
            
            tqdm.write(f"✓ Converted {pdf_id}")
            
        except Exception as e:
            tqdm.write(f"✗ Error converting {pdf_path.name}: {e}")
            continue


def define_pghd_terms() -> List[str]:
    """
    Define a comprehensive list of terms associated with PGHD 
    (patient-generated health data).
    
    Returns:
        List of search terms (lowercase for case-insensitive matching)
    """
    return [
        "patient-generated health data",
        "patient generated health data",
        "pghd",
        "patient-reported outcome",
        "patient reported outcome",
        "patient-reported outcome measure",
        "patient reported outcome measure",
        "pro",
        "proms",
        "prom",
        "patient-reported data",
        "patient reported data",
        "patient preference information",
        "ppi",
        "patient-reported experience measure",
        "patient reported experience measure",
        "prems",
        "prem",
        "self-reported data",
        "self reported data",
        "patient-collected data",
        "patient collected data",
        "wearable data",
        "wearable device",
        "fitness tracker",
        "activity tracker",
        "smartwatch",
        "patient diary",
        "health diary",
        "symptom diary",
        "mobile health",
        "mhealth",
        "m-health",
        "digital health",
        "remote monitoring",
        "remote patient monitoring",
        "rpm",
        "patient portal",
        "health app",
        "patient app",
        "self-monitoring",
        "self monitoring",
        "home monitoring",
    ]


def extract_paragraphs_with_terms(
    markdown_path: Path,
    pghd_terms: List[str]
) -> List[Tuple[str, str, Optional[str], str, List[str]]]:
    """
    Extract paragraphs containing PGHD terms from markdown files.
    
    Args:
        markdown_path: Path to markdown files
        pghd_terms: List of search terms
    
    Returns:
        List of tuples: (pdf_id, disease_main_topic, disease_sub_topic, 
                        matched_paragraph, matched_terms)
    """
    results = []
    
    # Get all markdown files
    markdown_files = list(markdown_path.glob("*.md"))
    print(f"\nProcessing {len(markdown_files)} markdown files...")
    
    for md_file in tqdm(markdown_files, desc="Processing markdown files", unit="file"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from comments
            pdf_id_match = re.search(r'<!-- PDF_ID: (.+?) -->', content)
            main_topic_match = re.search(r'<!-- DISEASE_MAIN_TOPIC: (.+?) -->', content)
            sub_topic_match = re.search(r'<!-- DISEASE_SUB_TOPIC: (.+?) -->', content)
            
            pdf_id = pdf_id_match.group(1) if pdf_id_match else md_file.stem
            disease_main_topic = main_topic_match.group(1) if main_topic_match else "Unknown"
            disease_sub_topic = sub_topic_match.group(1) if sub_topic_match else None
            if disease_sub_topic == "NA":
                disease_sub_topic = None
            
            # Remove metadata comments
            content = re.sub(r'<!-- .+? -->\n*', '', content)
            
            # Split into paragraphs (split by double newlines or more)
            paragraphs = re.split(r'\n\s*\n', content)
            paragraphs = [p.strip() for p in paragraphs if p.strip()]
            
            # Filter out tables and references
            filtered_paragraphs = []
            for paragraph in paragraphs:
                # Skip tables (markdown tables contain pipes |)
                if '|' in paragraph and paragraph.count('|') > 2:
                    continue
                
                # Skip reference sections (common patterns)
                lower_para = paragraph.lower()
                if any(ref_marker in lower_para[:50] for ref_marker in [
                    'references',
                    'bibliography',
                    'works cited',
                    '## references',
                    '# references',
                ]):
                    continue
                
                # Skip individual bibliography entries (NOT in-text citations)
                # These are full reference entries that appear in reference lists
                
                # Pattern 1: Numbered references with "- 1." or "- [1]" format (common in markdown)
                if re.match(r'^\s*[-•]\s*(\[\d+\]|\d+\.)\s+', paragraph):
                    continue
                
                # Pattern 2: References with HTML span tags (from PDF conversion)
                if '<span id=' in paragraph and re.search(r'\d{4}[;,\.]', paragraph):
                    continue
                
                # Pattern 3: Bullet point references starting with "- [Author" or "- Author"
                if re.match(r'^\s*[-•]\s+\[?\w+', paragraph) and re.search(r'\d{4}\)', paragraph):
                    continue
                
                # Pattern 4: References with URLs/DOIs and multiple commas (typical of full citations)
                if re.search(r'(http://|https://|doi:|DOI:)', paragraph) and paragraph.count(',') > 3:
                    continue
                
                # Pattern 5: Author-year with journal info (volume:page or pp.)
                # e.g., "Smith, J. (2020). Title. Journal 26:593-607"
                if (re.match(r'^\s*\w+,\s+\w+\..*\(\d{4}\)', paragraph) and 
                    re.search(r'(\d+:\d+[-–]\d+|pp?\.\s*\d+[-–]\d+)', paragraph)):
                    continue
                
                # Pattern 6: Multiple consecutive numbered references (reference lists have multiple)
                # Count how many numbered citations appear in the paragraph
                numbered_refs = len(re.findall(r'[-•]\s*\d+\.', paragraph))
                if numbered_refs >= 3:  # If 3 or more numbered items, likely a reference list
                    continue
                
                filtered_paragraphs.append(paragraph)
            
            # Check each paragraph for PGHD terms
            found_matches = False
            for paragraph in filtered_paragraphs:
                paragraph_lower = paragraph.lower()
                matched_terms = []
                
                for term in pghd_terms:
                    # Use word boundaries for better matching
                    pattern = r'\b' + re.escape(term.lower()) + r'\b'
                    if re.search(pattern, paragraph_lower):
                        matched_terms.append(term)
                
                if matched_terms:
                    # Remove duplicates and sort
                    matched_terms = sorted(list(set(matched_terms)))
                    results.append((
                        pdf_id,
                        disease_main_topic,
                        disease_sub_topic,
                        paragraph,
                        matched_terms
                    ))
                    found_matches = True
            
            # If no matches found, add one row with NAs
            if not found_matches:
                results.append((
                    pdf_id,
                    disease_main_topic,
                    disease_sub_topic,
                    None,
                    None
                ))
            
            tqdm.write(f"✓ Processed {pdf_id}")
            
        except Exception as e:
            tqdm.write(f"✗ Error processing {md_file.name}: {e}")
            continue
    
    return results


def create_and_save_dataframe(
    results: List[Tuple[str, str, Optional[str], str, List[str]]],
    output_path: Path
) -> pd.DataFrame:
    """
    Create a dataframe from extraction results and save to files.
    
    Args:
        results: List of extraction results
        output_path: Path to save output files
    
    Returns:
        DataFrame with results
    """
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create dataframe
    df = pd.DataFrame(results, columns=[
        'paper_pdf_id',
        'disease_main_topic',
        'disease_sub_topic',
        'matched_paragraph',
        'matched_terms'
    ])
    
    # Convert matched_terms list to string for easier reading
    df['matched_terms'] = df['matched_terms'].apply(
        lambda x: ', '.join(x) if x is not None else None
    )
    
    # Save to parquet
    parquet_file = output_path / 'pghd_extraction_results.parquet'
    df.to_parquet(parquet_file, index=False)
    print(f"\n✓ Saved results to {parquet_file}")
    
    # Save to CSV
    csv_file = output_path / 'pghd_extraction_results.csv'
    df.to_csv(csv_file, index=False)
    print(f"✓ Saved results to {csv_file}")
    
    # Print summary statistics
    print(f"\nSummary:")
    print(f"Total rows: {len(df)}")
    print(f"Unique papers: {df['paper_pdf_id'].nunique()}")
    print(f"Papers with matches: {df[df['matched_paragraph'].notna()]['paper_pdf_id'].nunique()}")
    print(f"Papers without matches: {df[df['matched_paragraph'].isna()]['paper_pdf_id'].nunique()}")
    print(f"Total matched paragraphs: {df['matched_paragraph'].notna().sum()}")
    
    return df
