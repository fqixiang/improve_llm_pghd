# PGHD in Medical Research Literature

This project analyzes how patient-generated health data (PGHD) is defined and used in medical research literature across various disease areas.

## Project Overview

The project implements pipelines to:
1. Extract PGHD-related content from scientific papers (PDFs)
2. Analyze terminology and usage patterns
3. Compare across different disease domains

## Project Structure

```
improve_llm_pghd/
├── data/
│   ├── raw/
│   │   └── PDFs/                    # Original PDF files organized by disease
│   │       ├── Cardiovascular disease/
│   │       ├── Chronic inflammation/
│   │       ├── Neurology/
│   │       ├── Oncology/
│   │       └── Ophthalmology/
│   └── processed/
│       ├── markdown/                # Converted markdown files
│       └── rule_based_extraction/   # Extracted PGHD content
├── src/
│   ├── pipeline_utils.py           # Shared pipeline utilities
│   └── analysis_utils.py           # Analysis utilities
├── run_pdf_to_markdown.py          # PDF conversion script
├── run_pghd_extraction.py          # PGHD extraction script
├── run_analysis.py                 # Analysis script
└── pyproject.toml                  # Dependencies
```

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for package management:

```bash
# Install dependencies
uv sync
```

### Dependencies

- **marker-pdf**: PDF to markdown conversion
- **pandas**: Data manipulation
- **pyarrow**: Parquet file support

## Usage

### Step 1: Convert PDFs to Markdown

Convert all PDFs to markdown format:

```bash
uv run python run_pdf_to_markdown.py
```

This will:
- Find all PDFs in `data/raw/PDFs/[disease]/FT_Included/` folders
- Convert them to markdown using the marker package
- Save to `data/processed/markdown/` with metadata headers

### Step 2: Extract PGHD Content

Extract PGHD-related paragraphs from the markdown files:

```bash
python run_pghd_extraction.py
```

**What it does:**
1. Searches for PGHD-related terms (patient-reported outcomes, wearables, remote monitoring, etc.)
2. Extracts paragraphs containing these terms
3. Saves results with metadata (disease topic, matched terms)

**Output files:**
- `data/processed/rule_based_extraction/pghd_extraction_results.parquet`
- `data/processed/rule_based_extraction/pghd_extraction_results.csv`

### Step 3: Analyze Results

Analyze the extracted data:

```bash
python run_analysis.py
```

**What it does:**
1. Counts frequency of each matched term
2. Generates statistics (total papers, matches, unique terms)
3. Filters results by specific keywords
4. Saves frequency tables and filtered results

**Output files:**
- `data/processed/rule_based_extraction/pghd_extraction_results.parquet`
- `data/processed/rule_based_extraction/pghd_extraction_results.csv`
- `data/processed/rule_based_extraction/term_frequencies.csv` (from analysis)
- `data/processed/rule_based_extraction/wearable_filtered_results.csv` (from analysis)

**Output schema:**
| Column | Description |
|--------|-------------|
| `paper_pdf_id` | PDF filename (without extension) |
| `disease_main_topic` | Main disease category |
| `disease_sub_topic` | Sub-category (if applicable) |
| `matched_paragraph` | Paragraph containing PGHD terms |
| `matched_terms` | Comma-separated list of matched terms |

## PGHD Terms

The pipeline searches for 33+ terms related to patient-generated health data, including:

- **Core terms**: patient-generated health data, PGHD
- **Patient-reported outcomes**: PRO, PROMs, patient-reported data
- **Technology**: wearable data, fitness tracker, smartwatch, activity tracker
- **Digital health**: mobile health, mHealth, remote monitoring, RPM
- **Self-reporting**: patient diary, symptom diary, self-monitoring

See `src/pipeline_utils.py` for the complete list.

## Custom Analysis

You can use the analysis utilities programmatically:

```python
from pathlib import Path
from src.analysis_utils import count_term_frequencies, filter_by_keywords

# Count term frequencies
results_file = Path("data/processed/rule_based_extraction/pghd_extraction_results.parquet")
term_freq = count_term_frequencies(results_file)

# Count specific keywords only
my_keywords = ["wearable data", "remote monitoring", "mhealth"]
specific_freq = count_term_frequencies(results_file, keywords=my_keywords)

# Filter by keywords
filtered_df = filter_by_keywords(
    results_file, 
    keywords=["patient-reported outcome", "pro"],
    output_file=Path("data/processed/rule_based_extraction/pro_filtered.csv")
)
```

## Data Organization

PDFs should be organized in the following structure:

```
data/raw/PDFs/
└── [disease_main_topic]/
    └── [disease_sub_topic]/          # Optional
        └── FT_Included/              # Or "FT Included" / "FT Include"
            └── *.pdf
```

## Requirements

- Python 3.11+
- macOS, Linux, or Windows

## Future Pipelines

This project is designed to support multiple analysis pipelines. Additional pipelines will be added to analyze PGHD usage patterns using LLMs and other methods.
