# agentic-trading

Repository for agentic trading using SEC and agents, publishing to slack

## SEC Bulk Analysis System

A comprehensive system for downloading, parsing, and analyzing SEC filings using Charlie Munger's investment framework.

### Features

- **Daily Filing Retrieval**: Downloads daily master index files from SEC.gov
- **CIK-Based Organization**: Organizes filings by 10-digit CIK with structured directory layout
- **Munger Analysis Framework**: Applies Charlie Munger's four investment filters and valuation methods
- **Automated Processing**: Batch processing with error handling and incremental updates
- **Multiple Output Formats**: Generates both JSON data and human-readable Markdown reports
- **Combined Reports**: Combines all individual reports into one comprehensive markdown file

### Installation

```bash
pip install -r requirements.txt
```

### Usage

#### Process yesterday's filings:
```bash
python main.py
```

#### Process a specific date:
```bash
python main.py --date 2024-01-15
```

#### Process a date range:
```bash
python main.py --start-date 2024-01-01 --end-date 2024-01-31
```

#### Custom storage location:
```bash
python main.py --storage-path /path/to/sec_data
```

#### Skip analysis (download and organize only):
```bash
python main.py --no-analysis
```

#### Combine all reports into one big markdown file:
```bash
# Combine reports for a specific date
python combine_reports.py --date 2025-05-30

# Use custom reports directory
python combine_reports.py --date 2025-05-30 --reports-dir /path/to/reports

# Save with custom filename
python combine_reports.py --date 2025-05-30 --output combined_analysis.md
```

#### Combine reports using the main report generator:
```bash
# Generate new reports and combine them
python fixed_reports.py --date 2025-05-30

# Only combine existing reports (no regeneration)
python fixed_reports.py --date 2025-05-30 --combine-only
```

### Directory Structure

The system creates the following directory structure:

```
sec_data/
├── raw/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── 15/
│   │   │   │   ├── master.idx
│   │   │   │   ├── CIK_0000320193/
│   │   │   │   │   ├── 10-K_20250115.txt
│   │   │   │   │   └── metadata.parquet
├── processed/
│   ├── company_db.parquet
│   └── analysis_results/
│       ├── 0000320193/
│       │   ├── APPLE_INC_20250115_analysis.json
│       │   └── APPLE_INC_20250115_munger.md
```

### Analysis Framework

The system implements Charlie Munger's investment framework:

#### Four Investment Filters:
1. ROE >15% for 5 consecutive years
2. Debt/Equity ratio <8%
3. Management ownership >5%
4. Consistent earnings growth

#### Moat Durability Score (1-10):
- Market Share Stability (40% weight)
- Patent Portfolio Strength (30% weight)
- Customer Retention Rate (20% weight)
- Pricing Power Evidence (10% weight)

#### Valuation Scenarios:
- **Base Case**: 8% discount rate, 2% terminal growth
- **Bear Case**: 10% discount rate, 1% terminal growth
- **Bull Case**: 6% discount rate, 3% terminal growth

#### Financial Forensics:
- Benford's Law analysis for accounting anomalies
- CAPEX vs Depreciation reality check
- True Owner Earnings calculation
- Historical trend analysis

### Combined Reports

The system now supports combining all individual reports for a given date into one comprehensive markdown file. This feature creates a single document containing:

1. **Table of Contents** - Navigation links to all sections
2. **Executive Summary** - Market overview and top investment opportunities  
3. **Individual Company Analysis** - All company reports in sequence
4. **CSV Data Summary** - Tabular summary of all metrics

The combined report is saved as `all_reports_YYYYMMDD.md` in the reports directory and includes:
- Proper markdown formatting with headers and sections
- Conversion of CSV data to readable markdown tables
- Navigation-friendly table of contents
- Report generation metadata and statistics

This makes it easy to review all analysis results in a single document while maintaining the granular individual reports for detailed reference.

### Testing

Run the test suite to validate system functionality:

```bash
python test_system.py
```

### Architecture

The system is built with the following components:

- **Models** (`sec_analysis/models/`): Pydantic data models for filings and analysis
- **Fetchers** (`sec_analysis/fetchers/`): SEC data downloading with proper headers
- **Parsers** (`sec_analysis/parsers/`): Master index parsing and validation
- **Storage** (`sec_analysis/storage/`): File organization and data persistence
- **Analyzers** (`sec_analysis/analyzers/`): Munger-style investment analysis

### Error Handling

The system includes comprehensive error handling:
- Retry logic for network requests
- Dead-letter queue for failed filings
- Graceful degradation for partial data
- Detailed logging for debugging

### Schema Evolution

Analysis results use versioned schemas (currently v2.1) to support:
- Backward compatibility
- Schema migration
- Flexible metadata storage

### Compliance

- Follows SEC guidelines for automated access
- Includes proper User-Agent headers
- Implements respectful rate limiting
- Maintains audit trail for all requests
