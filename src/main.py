# Placeholder for the main script
from datetime import datetime
import requests # Import requests for error handling
import pandas as pd
import os
from src.utils import (
    download_master_index,
    parse_master_index,
    download_filing_text,
    save_raw_filing,
    update_company_db
)
from src.analysis import get_filing_text, perform_preliminary_analysis # Added analysis imports
from collections import defaultdict

def process_daily_filings(target_date: datetime):
    """
    Processes daily SEC filings for a given target date.

    Args:
        target_date: The date for which to process filings.
    """
    # Construct the DAILY_URL
    year = target_date.year
    quarter = (target_date.month - 1) // 3 + 1
    date_str = target_date.strftime('%Y%m%d')
    daily_url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{quarter}/master.{date_str}.idx"
    print(f"Constructed DAILY_URL: {daily_url}")

    # Download the master index file
    try:
        print(f"Downloading master index file from {daily_url}")
        master_index_content = download_master_index(daily_url)
        print(f"Successfully downloaded master index file for {target_date}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading master index file for {target_date}: {e}")
        return # Exit if download fails

    # Parse the master index file
    print(f"Parsing master index file (length: {len(master_index_content)} bytes)")
    parsed_filings = parse_master_index(master_index_content)
    print(f"Parsed {len(parsed_filings)} filings.")

    # Filter filings
    target_forms = ['10-K', '10-Q', '8-K', 'DEF 14A']
    print(f"Filtering for forms: {', '.join(target_forms)}")
    filtered_filings = [
        filing for filing in parsed_filings if filing['form_type'] in target_forms
    ]
    print(f"Found {len(filtered_filings)} relevant filings after filtering.")

    # Save filings and aggregate metadata
    raw_data_base_path = "sec_data/raw"
    processed_data_base_path = "sec_data/processed" # For analysis results
    all_processed_filing_metadata_for_db = [] # Initialize list to collect all successful metadata

    # Group filings by CIK
    filings_by_cik = defaultdict(list)
    for f in filtered_filings:
        filings_by_cik[f['cik']].append(f)

    print(f"Processing filings for {len(filings_by_cik)} CIKs.")
    total_filings_processed = 0
    total_filings_succeeded = 0

    for cik, cik_filings in filings_by_cik.items():
        print(f"Processing {len(cik_filings)} filings for CIK: {cik}")
        daily_cik_metadata_list_for_parquet = [] # For the CIK-specific daily parquet
        padded_cik = cik.zfill(10)

        for filing_info in cik_filings:
            total_filings_processed += 1
            try:
                # 1. Download filing text
                filing_content = download_filing_text(filing_info['file_name'])

                # 2. Save raw filing text
                raw_file_path = save_raw_filing(filing_content, filing_info, raw_data_base_path, target_date)

                # 3. Perform preliminary analysis
                # Retrieve the just-saved filing text for analysis
                # Note: get_filing_text needs unpadded CIK
                retrieved_filing_text_for_analysis = get_filing_text(
                    cik=filing_info['cik'], # Pass unpadded CIK
                    form_type=filing_info['form_type'],
                    date_filed=filing_info['date_filed'],
                    raw_data_base_path=raw_data_base_path
                )

                if retrieved_filing_text_for_analysis:
                    # perform_preliminary_analysis now returns a dict or None
                    analysis_output_data = perform_preliminary_analysis(
                        cik=filing_info['cik'],
                        company_name=filing_info['company_name'],
                        form_type=filing_info['form_type'],
                        date_filed=filing_info['date_filed'],
                        target_date=target_date,
                        filing_text=retrieved_filing_text_for_analysis,
                        processed_data_base_path=processed_data_base_path
                    )

                    analysis_json_path = None
                    munger_report_md_path = None

                    if analysis_output_data:
                        analysis_json_path = analysis_output_data.get('json_save_path')
                        munger_report_md_path = analysis_output_data.get('munger_report_path')
                        # Messages about JSON and MD saving are now handled within perform_preliminary_analysis and generate_munger_markdown_report
                    else:
                        print(f"Preliminary analysis failed for {filing_info['form_type']} CIK {filing_info['cik']}.")
                else:
                    print(f"Could not retrieve text for {filing_info['form_type']} CIK {filing_info['cik']} from {raw_file_path} for analysis.")
                    analysis_json_path = None # Ensure these are None if text retrieval fails
                    munger_report_md_path = None

                # 4. Prepare metadata for this specific filing (for daily .parquet and company_db)
                current_filing_metadata = {
                    "cik": padded_cik,
                    "company_name": filing_info['company_name'],
                    "form_type": filing_info['form_type'],
                    "date_filed": filing_info['date_filed'],
                    "processed_date": target_date.isoformat(),
                    "raw_file_path": raw_file_path,
                    "filing_url": filing_info['file_name'],
                    "analysis_json_path": analysis_json_path,
                    "munger_report_path": munger_report_md_path
                }
                daily_cik_metadata_list_for_parquet.append(current_filing_metadata)
                all_processed_filing_metadata_for_db.append(current_filing_metadata)
                total_filings_succeeded +=1
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {filing_info.get('file_name', 'N/A')} for CIK {cik}: {e}")
            except IOError as e:
                print(f"Error saving file for CIK {cik}, form {filing_info.get('form_type', 'N/A')}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred processing filing {filing_info.get('form_type', 'N/A')} for CIK {cik}: {e}")

        if not daily_cik_metadata_list_for_parquet: # Check the list for the daily parquet
            print(f"No metadata collected for CIK {cik} on {target_date.strftime('%Y-%m-%d')} for daily Parquet. Skipping Parquet generation for this CIK.")
            continue

        # 4. Create and save metadata.parquet for the CIK for the target_date
        try:
            metadata_df = pd.DataFrame(daily_cik_metadata_list_for_parquet)

            # Construct path for metadata.parquet using target_date for year/month/day
            year = str(target_date.year)
            month = f"{target_date.month:02d}"
            day = f"{target_date.day:02d}"

            metadata_dir = os.path.join(raw_data_base_path, year, month, day, f"CIK_{padded_cik}")
            os.makedirs(metadata_dir, exist_ok=True) # Ensure directory exists

            parquet_path = os.path.join(metadata_dir, "metadata.parquet")

            metadata_df.to_parquet(parquet_path, engine='pyarrow', compression='ZSTD')
            print(f"Successfully saved metadata.parquet for CIK {cik} at {parquet_path}")
        except Exception as e:
            print(f"Error generating or saving metadata.parquet for CIK {cik}: {e}")

    print(f"\nFinished processing all CIKs for {target_date.strftime('%Y-%m-%d')}.")
    print(f"Total filings encountered: {total_filings_processed}")
    print(f"Total filings successfully downloaded and saved: {total_filings_succeeded}")

    # Update company database with all successfully processed filings from this run
    if all_processed_filing_metadata_for_db:
        company_db_path = os.path.join("sec_data", "processed", "company_db.parquet")
        print(f"\nUpdating company database at {company_db_path}...")
        update_company_db(all_processed_filing_metadata_for_db, company_db_path)
    else:
        print("\nNo filings were successfully processed in this run. Company database remains unchanged.")


if __name__ == "__main__":
    print("To run process_daily_filings, uncomment the example usage in __main__ and set a valid date.")
    # Make sure sec_data/raw exists or is created by the script if it's the very first run.
    # Example: process_daily_filings(datetime(2023, 4, 10)) # A date with some filings
    # For testing, it's good to pick a date with a small number of filings for target forms.
    # E.g., process_daily_filings(datetime(2024, 1, 2))
    # Check SEC EDGAR for recent dates with filings if you want to test live data.
    # process_daily_filings(datetime(2024, 3, 15))

    # --- Example usage of get_filing_text (for testing analysis module) ---
    # This assumes you have run process_daily_filings for a date that generated specific files.
    # For instance, if you processed for 2023-04-10 and know CIK 1000097 filed a 10-Q on that date (or it was filed earlier but processed with target_date 2023-04-10)
    # And assuming get_filing_text's path logic (using date_filed for Y/M/D path parts) aligns with a file saved.

    # To make this test runnable, you'd need to:
    # 1. Ensure a file exists at the expected path.
    #    e.g. sec_data/raw/2023/04/10/CIK_0001000097/10-Q_2023-04-10.txt
    # 2. Uncomment the call to process_daily_filings for a suitable date first, or manually place a file.

    # from src.analysis import get_filing_text, extract_business_model_changes
    # test_cik = "1000097" # Example CIK (AEHR TEST SYSTEMS)
    # test_form_type = "10-Q"
    # test_date_filed = "2023-04-10" # Example, ensure this file would exist if processing for this date
                                  # and that save_raw_filing's target_date's Y/M/D matches this.

    # print(f"\n--- Testing get_filing_text for CIK {test_cik}, Form {test_form_type}, Date {test_date_filed} ---")
    # filing_content = get_filing_text(test_cik, test_form_type, test_date_filed)
    # if filing_content:
    #     print(f"Successfully retrieved filing text. Length: {len(filing_content)} characters.")
    #     # You could then test a placeholder analysis function:
    #     # changes = extract_business_model_changes(filing_content)
    #     # print(f"Business model changes analysis (placeholder): {changes}")
    # else:
    #     print(f"Could not retrieve filing text for CIK {test_cik}, Form {test_form_type}, Date {test_date_filed}.")
    # print("--- End of get_filing_text test ---")
