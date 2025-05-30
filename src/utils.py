# Placeholder for utility functions
import requests
import os
from datetime import datetime, timezone
import pandas as pd

def example_util_function():
    print("Utility function placeholder")

def download_master_index(daily_url: str) -> str:
    """
    Downloads the master index file from the SEC EDGAR database.

    Args:
        daily_url: The URL of the master index file.

    Returns:
        The text content of the master index file.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(daily_url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    return response.text

def download_filing_text(filing_url: str) -> str:
    """
    Downloads the text content of a single filing from its URL.

    Args:
        filing_url: The URL of the filing document.

    Returns:
        The text content of the filing.

    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(f"Downloading filing text from: {filing_url}")
    response = requests.get(filing_url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_master_index(master_file_content: str) -> list[dict]:
    """
    Parses the text content of a master index file.

    The master file has a header section (lines starting with '#') that should be skipped.
    Data lines are pipe-delimited (|). Relevant columns are:
    CIK, Company Name, Form Type, Date Filed, File Name.

    Args:
        master_file_content: The text content of the master index file.

    Returns:
        A list of dictionaries, where each dictionary represents a filing
        and has the keys: 'cik', 'company_name', 'form_type', 'date_filed', 'file_name' (full URL).
    """
    filings = []
    lines = master_file_content.splitlines()
    header_skipped = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('#'):
            # This is part of the description or header, skip actual header line count for parsing start
            if "CIK|Company Name|Form Type|Date Filed|File Name" in line: # Standard header line
                 header_skipped = True
            continue

        if not header_skipped: # Still in header section before actual data lines
            continue

        parts = line.split('|')
        if len(parts) == 5:
            cik, company_name, form_type, date_filed, file_name_path = parts
            full_file_name_url = f"https://www.sec.gov/Archives/{file_name_path}"
            filings.append({
                "cik": cik,
                "company_name": company_name,
                "form_type": form_type,
                "date_filed": date_filed,
                "file_name": full_file_name_url,
            })
    return filings

def save_raw_filing(content: str, filing_info: dict, base_path: str, target_date: datetime) -> str:
    """
    Saves the already downloaded filing content to a structured directory.
    The directory structure is based on the target_date for consistency in batch processing.

    Args:
        content: The text content of the filing.
        filing_info: Dictionary containing filing details ('cik', 'form_type', 'date_filed').
        base_path: The root directory for saving (e.g., "sec_data/raw").
        target_date: The primary date for organizing the folder structure (year, month, day).

    Returns:
        The full path where the file was saved.

    Raises:
        IOError: If saving the file fails.
        Exception: For other unexpected errors.
    """
    try:
        # Use target_date for the main directory structure
        year = str(target_date.year)
        month = f"{target_date.month:02d}"
        day = f"{target_date.day:02d}"

        # Pad CIK to 10 digits

        padded_cik = filing_info['cik'].zfill(10)
        safe_form_type = filing_info['form_type'].replace('/', '-')

        # Use filing_info['date_filed'] for the actual filename, as it's specific to the document
        file_specific_date = filing_info['date_filed']

        save_dir = os.path.join(base_path, year, month, day, f"CIK_{padded_cik}")
        filename = f"{safe_form_type}_{file_specific_date}.txt"
        full_save_path = os.path.join(save_dir, filename)

        os.makedirs(save_dir, exist_ok=True)

        with open(full_save_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully saved raw filing: {full_save_path}")
        return full_save_path

    except IOError as e:
        print(f"Error saving raw file {full_save_path}: {e}")
        raise  # Re-raise to be caught by the main processing loop
    except Exception as e:
        print(f"An unexpected error occurred while saving raw filing for CIK {filing_info.get('cik', 'Unknown CIK')}, Form {filing_info.get('form_type', 'Unknown Form')}: {e}")
        raise # Re-raise

def update_company_db(processed_filings_metadata: list[dict], db_path: str):
    """
    Updates or creates a company database Parquet file with metadata from processed filings.

    Args:
        processed_filings_metadata: A list of dictionaries, each containing metadata
                                    for a successfully processed filing.
        db_path: Path to the company_db.parquet file.
    """
    db_cols = ['cik', 'company_name', 'forms', 'first_filed', 'last_updated', 'analysis_version']

    if os.path.exists(db_path):
        try:
            company_df = pd.read_parquet(db_path)
            if not company_df.empty and 'cik' in company_df.columns:
                 company_df = company_df.set_index('cik')
            else: # DB exists but is empty or malformed
                print(f"Company DB at {db_path} is empty or 'cik' column is missing. Initializing new DB.")
                company_df = pd.DataFrame(columns=db_cols[1:]).set_index(pd.Index([], name='cik'))

        except Exception as e:
            print(f"Error loading company DB from {db_path}: {e}. Initializing new DB.")
            # Initialize an empty DataFrame with 'cik' as index if loading fails
            company_df = pd.DataFrame(columns=db_cols[1:]).set_index(pd.Index([], name='cik'))
    else:
        print(f"Company DB not found at {db_path}. Initializing new DB.")
        company_df = pd.DataFrame(columns=db_cols[1:]).set_index(pd.Index([], name='cik'))

    # Ensure 'forms' column exists and is of object type to hold lists
    if 'forms' not in company_df.columns:
        company_df['forms'] = pd.Series(dtype='object')

    # Fill NaN in 'forms' with empty lists if any CIKs don't have it yet
    # This is crucial if adding a new CIK or if a CIK somehow has a NaN 'forms' field
    for cik_idx in company_df.index:
        if pd.isna(company_df.loc[cik_idx, 'forms']):
            company_df.loc[cik_idx, 'forms'] = []


    for filing_meta in processed_filings_metadata:
        cik = filing_meta['cik'] # Assuming CIK is already padded
        company_name = filing_meta['company_name']
        form_type = filing_meta['form_type']

        # Ensure date_filed is a string. If it's datetime, format it.
        date_filed_val = filing_meta['date_filed']
        if isinstance(date_filed_val, datetime):
            date_filed_str = date_filed_val.strftime('%Y-%m-%d')
        else:
            date_filed_str = str(date_filed_val) # Assume it's already YYYY-MM-DD string

        current_time_utc_iso = datetime.now(timezone.utc).isoformat()
        analysis_version = "2.1" # Hardcoded as per requirement

        if cik in company_df.index:
            # Update existing entry
            company_df.loc[cik, 'last_updated'] = current_time_utc_iso

            # Ensure 'forms' for the CIK is a list
            if not isinstance(company_df.loc[cik, 'forms'], list):
                company_df.loc[cik, 'forms'] = [] # Initialize as list if not already

            if form_type not in company_df.loc[cik, 'forms']:
                company_df.loc[cik, 'forms'].append(form_type)

            # Update first_filed if the current filing's date is earlier
            # It's important that first_filed is also a string for comparison or convert both
            if pd.isna(company_df.loc[cik, 'first_filed']) or date_filed_str < company_df.loc[cik, 'first_filed']:
                company_df.loc[cik, 'first_filed'] = date_filed_str

            # Update company name if it has changed (e.g. due to corrections in newer filings)
            company_df.loc[cik, 'company_name'] = company_name
            company_df.loc[cik, 'analysis_version'] = analysis_version # Update version too
        else:
            # Add new entry
            new_entry = {
                'company_name': company_name,
                'forms': [form_type],
                'first_filed': date_filed_str,
                'last_updated': current_time_utc_iso,
                'analysis_version': analysis_version
            }
            company_df.loc[cik] = new_entry
            # Ensure 'forms' for new entries are actual lists
            if not isinstance(company_df.loc[cik, 'forms'], list):
                 company_df.loc[cik, 'forms'] = [company_df.loc[cik, 'forms']]


    # Save the database
    try:
        db_dir = os.path.dirname(db_path)
        if db_dir: # Ensure directory is not empty (root path case)
            os.makedirs(db_dir, exist_ok=True)

        # Reset index to make 'cik' a column before saving
        company_df.reset_index().rename(columns={'index': 'cik'}).to_parquet(db_path, engine='pyarrow', compression='ZSTD', index=False)
        print(f"Company database successfully updated and saved to {db_path}")
    except Exception as e:
        print(f"Error saving company database to {db_path}: {e}")
