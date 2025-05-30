import os
import json
from datetime import datetime

def get_filing_text(cik: str, form_type: str, date_filed: str, raw_data_base_path: str = "sec_data/raw") -> str | None:
    """
    Retrieves the text content of a specific filing from the raw data storage.

    Args:
        cik: The CIK of the company (should be unpadded, will be padded internally).
        form_type: The form type (e.g., "10-K", "8-K").
        date_filed: The date the form was filed (YYYY-MM-DD string).
        raw_data_base_path: The base directory where raw filings are stored.

    Returns:
        The text content of the filing if found, otherwise None.
    """
    try:
        date_obj = datetime.strptime(date_filed, '%Y-%m-%d')
        year = str(date_obj.year)
        month = f"{date_obj.month:02d}"
        day = f"{date_obj.day:02d}"
    except ValueError:
        print(f"Warning: Invalid date_filed format for get_filing_text: {date_filed}. Expected YYYY-MM-DD.")
        return None

    padded_cik = cik.zfill(10)
    form_type_cleaned = form_type.replace('/', '-') # e.g., S-1/A -> S-1-A

    # Path construction based on how save_raw_filing structures it.
    # It uses target_date for the directory structure (year/month/day part)
    # and date_filed for the filename.
    # For get_filing_text, if we don't have a "target_date" context for when it was processed,
    # using date_filed for directory parts is a reasonable assumption.
    # This means save_raw_filing's target_date and this date_filed should align for retrieval.
    # If a filing was processed on 2023-10-27 (target_date) but its actual date_filed is 2023-10-26,
    # save_raw_filing would put it in .../2023/10/27/CIK_.../FORM_2023-10-26.txt
    # To retrieve this, get_filing_text would need to know the processing date (2023-10-27)
    # for the year/month/day path part.
    # For simplicity now, we assume the year/month/day in the path *is* from date_filed.
    # This implies that when save_raw_filing saves, its target_date's Y/M/D matches the filing's date_filed Y/M/D.
    # This might need refinement if processing batches significantly post-date the filings.

    file_path_dir = os.path.join(raw_data_base_path, year, month, day, f"CIK_{padded_cik}")
    file_name = f"{form_type_cleaned}_{date_filed}.txt"
    full_file_path = os.path.join(file_path_dir, file_name)

    if os.path.exists(full_file_path):
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Warning: Could not read file {full_file_path}: {e}")
            return None
    else:
        print(f"Warning: Filing not found at {full_file_path}")
        return None

# --- Placeholder Analysis Functions ---

def extract_business_model_changes(filing_text: str, previous_filing_text: str | None = None) -> dict:
    """
    Placeholder: Extracts business model changes from filing text, potentially comparing to a previous filing.
    """
    print(f"Placeholder: Analyzing business model changes (current length: {len(filing_text)}, prev length: {len(previous_filing_text) if previous_filing_text else 'N/A'})")
    # In a real scenario, this would involve NLP, diffing, and pattern matching.
    return {"detected_changes": "none_implemented_yet"}

def extract_financial_statement_anomalies(filing_text: str) -> dict:
    """
    Placeholder: Extracts financial statement anomalies from filing text.
    (Future: Could involve parsing XBRL data if available)
    """
    print(f"Placeholder: Analyzing financial statement anomalies (text length: {len(filing_text)})")
    # In a real scenario, this would parse financial tables, look for outliers, inconsistencies.
    return {"detected_anomalies": "none_implemented_yet"}

def extract_insider_transaction_patterns(filing_text: str) -> dict:
    """
    Placeholder: Extracts insider transaction patterns from filing text (e.g., from Form 4, or sections in 10-K/Q).
    """
    print(f"Placeholder: Analyzing insider transaction patterns (text length: {len(filing_text)})")
    # This would parse ownership tables, transaction details.
    return {"detected_patterns": "none_implemented_yet"}

# --- New Placeholder Valuation Functions ---

def calculate_moat_durability_score(filing_text: str, cik: str) -> dict:
    """Placeholder: Calculates a score for economic moat durability."""
    print(f"Placeholder: Calculating moat durability score for CIK {cik} (text length: {len(filing_text)})")
    return {
        "score": "pending",
        "components": {
            "brand_strength": "pending",
            "network_effects": "pending",
            "switching_costs": "pending",
            "intangible_assets_patents": "pending",
            "cost_advantages_scale": "pending",
            "regulatory_protection": "pending"
        },
        "details": "Requires qualitative and quantitative data extraction and scoring logic."
    }

def perform_financial_forensics(filing_text: str, cik: str) -> dict:
    """Placeholder: Performs financial forensic checks."""
    print(f"Placeholder: Performing financial forensics for CIK {cik} (text length: {len(filing_text)})")
    return {
        "revenue_recognition_quality": "pending",
        "expense_recognition_quality": "pending",
        "cash_flow_quality_vs_earnings": "pending",
        "benfords_law_check_financials": "pending",
        "capex_vs_depreciation_analysis": "pending",
        "true_owner_earnings_estimate": "pending",
        "details": "Requires detailed financial statement data extraction and analysis."
    }

def calculate_intrinsic_value_and_mos(filing_text: str, cik: str, market_price: float | None = None) -> dict:
    """Placeholder: Calculates intrinsic value and margin of safety."""
    print(f"Placeholder: Calculating intrinsic value and MoS for CIK {cik} (text length: {len(filing_text)}), Market Price: {market_price if market_price else 'N/A'}")
    return {
        "intrinsic_value_avg": "pending",
        "mos_pct_at_market_price": "pending" if market_price else "N/A (market price not provided)",
        "valuation_models_summary": {
            "dcf_discounted_cash_flow": {"value": "pending", "assumptions": "pending"},
            "epv_earnings_power_value": {"value": "pending", "assumptions": "pending"},
            "graham_formula_value": {"value": "pending", "inputs": "pending"},
            "asset_reproduction_value": {"value": "pending", "details": "pending"}
        },
        "scenarios": {
            "base_case_iv": "pending",
            "bear_case_iv": "pending",
            "bull_case_iv": "pending"
        },
        "details": "Requires comprehensive financial modeling, future projections, and potentially current market data."
    }

def apply_mungers_filters(filing_text: str, cik: str) -> dict:
    """
    Placeholder: Applies Munger's key financial filters.
    Currently, this is a placeholder and does not perform actual calculations.
    It will require parsed financial data in future implementations.

    Args:
        filing_text: The raw text of the filing (placeholder for now).
        cik: CIK of the company (placeholder for now).

    Returns:
        A dictionary representing the checklist status for Munger's filters.
    """
    print(f"Placeholder: Applying Munger's filters for CIK {cik} (text length: {len(filing_text)})")
    return {
        "roe_gt_15_5yrs": {"status": "pending", "details": "Requires historical data extraction and calculation"},
        "debt_equity_lt_0_5": {"status": "pending", "details": "Requires financial data extraction and calculation"},
        "fcf_sales_gt_8": {"status": "pending", "details": "Requires financial data extraction and calculation"},
        "mgmt_ownership_gt_5": {"status": "pending", "details": "Requires proxy statement (DEF 14A) analysis or specific section extraction from 10-K"}
    }

def perform_preliminary_analysis(
    cik: str,
    company_name: str,
    form_type: str,
    date_filed: str,
    target_date: datetime, # Date of the processing run
    filing_text: str,
    processed_data_base_path: str = "sec_data/processed"
) -> dict | None: # Returns the analysis_results dict or None
    """
    Performs preliminary analysis on a single filing and saves the results as JSON.

    Args:
        cik: CIK of the company (unpadded).
        company_name: Name of the company.
        form_type: Form type of the filing.
        date_filed: Date the filing was made (YYYY-MM-DD).
        target_date: The date of this processing run (used for folder structure and metadata).
        filing_text: The raw text content of the filing.
        processed_data_base_path: Base path for saving processed analysis data.

    Returns:
        Path to the saved analysis JSON file, or None if saving fails.
    """
    padded_cik = cik.zfill(10)
    analysis_version = "2.1" # As per issue requirement

    # Call placeholder extraction functions
    # For business_model_changes, previous_filing_text is None for now
    bmc_results = extract_business_model_changes(filing_text)
    fsa_results = extract_financial_statement_anomalies(filing_text)
    itp_results = extract_insider_transaction_patterns(filing_text)
    munger_filters_results = apply_mungers_filters(filing_text, cik)

    # Call new placeholder valuation functions
    moat_score_results = calculate_moat_durability_score(filing_text, cik)
    financial_forensics_results = perform_financial_forensics(filing_text, cik)
    # For iv_mos, market_price is not available in this context yet, so pass None
    iv_mos_results = calculate_intrinsic_value_and_mos(filing_text, cik, market_price=None)

    analysis_results = {
        "cik": padded_cik,
        "company_name": company_name,
        "form_type": form_type,
        "date_filed": date_filed,
        "processing_date": target_date.isoformat(),
        "analysis_version": analysis_version,
        "data_extraction": {
            "business_model_changes": bmc_results,
            "financial_statement_anomalies": fsa_results,
            "insider_transaction_patterns": itp_results,
        },
        "mungers_filters_checklist": munger_filters_results,
        "valuation_metrics": {
            "moat_durability_score": moat_score_results,
            "financial_forensics": financial_forensics_results,
            "intrinsic_value_and_mos": iv_mos_results
            # Previous simple placeholders like "graham_number_conservative" are now part of iv_mos_results
        }
    }

    # Construct save path using target_date for year/month/day
    year = str(target_date.year)
    month = f"{target_date.month:02d}"
    day = f"{target_date.day:02d}"

    form_type_cleaned = form_type.replace('/', '-')
    # Filename includes form_type, date_filed, and analysis_version for clarity
    analysis_filename = f"{form_type_cleaned}_{date_filed}_analysis_v{analysis_version}.json"
    json_save_dir = os.path.join(processed_data_base_path, year, month, day, f"CIK_{padded_cik}")
    json_full_save_path = os.path.join(json_save_dir, analysis_filename)

    analysis_results['json_save_path'] = json_full_save_path # Store JSON path in results

    try:
        os.makedirs(json_save_dir, exist_ok=True)
        with open(json_full_save_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=4)
        print(f"Successfully saved preliminary analysis JSON to: {json_full_save_path}")

        # Now generate and save the Markdown report
        markdown_report_path = generate_munger_markdown_report(analysis_results, target_date, processed_data_base_path)
        if markdown_report_path:
            analysis_results['munger_report_path'] = markdown_report_path
            # Re-save the JSON to include the markdown_report_path
            with open(json_full_save_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=4)
            print(f"Re-saved JSON with Munger report path: {json_full_save_path}")
        else:
            analysis_results['munger_report_path'] = None
            print(f"Failed to generate or save Munger Markdown report for CIK {padded_cik}, Form {form_type}.")

        return analysis_results # Return the comprehensive results

    except IOError as e:
        print(f"Error saving analysis JSON to {json_full_save_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while saving analysis JSON for CIK {padded_cik}, Form {form_type}: {e}")
        return None

def generate_munger_markdown_report(
    analysis_data: dict,
    target_date: datetime, # Needed for path construction
    processed_data_base_path: str = "sec_data/processed"
) -> str | None:
    """
    Generates a Markdown report based on Munger's framework from analysis data.

    Args:
        analysis_data: The dictionary containing analysis results (from perform_preliminary_analysis).
        target_date: The date of the processing run, used for path construction.
        processed_data_base_path: Base path for saving the report.

    Returns:
        Path to the saved Markdown report, or None if saving fails.
    """
    try:
        cik = analysis_data['cik'] # Already padded
        company_name = analysis_data['company_name']
        form_type = analysis_data['form_type']
        date_filed = analysis_data['date_filed']
        processing_date = analysis_data['processing_date']
        analysis_version = analysis_data['analysis_version']

        # Data Extraction Summary
        de_summary = analysis_data.get('data_extraction', {})
        bmc_summary = de_summary.get('business_model_changes', {}).get('detected_changes', 'pending')
        fsa_summary = de_summary.get('financial_statement_anomalies', {}).get('detected_anomalies', 'pending')
        itp_summary = de_summary.get('insider_transaction_patterns', {}).get('detected_patterns', 'pending')

        # Munger's Filters
        mungers_filters = analysis_data.get('mungers_filters_checklist', {})

        # Valuation Metrics
        valuation_metrics = analysis_data.get('valuation_metrics', {})
        moat_score_data = valuation_metrics.get('moat_durability_score', {})
        forensics_data = valuation_metrics.get('financial_forensics', {})
        iv_mos_data = valuation_metrics.get('intrinsic_value_and_mos', {})
        iv_scenarios = iv_mos_data.get('scenarios', {})


        report_content = f"# Munger Framework Analysis: {company_name} ({cik}) - {form_type} ({date_filed})\n\n"
        report_content += "## Filing Details\n"
        report_content += f"- **CIK**: {cik}\n"
        report_content += f"- **Company Name**: {company_name}\n"
        report_content += f"- **Form Type**: {form_type}\n"
        report_content += f"- **Date Filed**: {date_filed}\n"
        report_content += f"- **Processing Date**: {processing_date}\n"
        report_content += f"- **Analysis Version**: {analysis_version}\n\n"

        report_content += "## Data Extraction Summary (Placeholder Status)\n"
        report_content += f"- **Business Model Changes**: {bmc_summary}\n"
        report_content += f"- **Financial Statement Anomalies**: {fsa_summary}\n"
        report_content += f"- **Insider Transaction Patterns**: {itp_summary}\n\n"

        report_content += "## Munger's 4 Filters Checklist\n"
        for filter_name, data in mungers_filters.items():
            report_content += f"- **{filter_name.replace('_', ' ').title()}**: {data.get('status', 'pending')} ({data.get('details', 'N/A')})\n"
        report_content += "\n"

        report_content += "## Valuation Summary\n"
        report_content += f"- **Moat Durability Score**: {moat_score_data.get('score', 'pending')} ({moat_score_data.get('details', 'N/A')})\n"
        report_content += "  - **Financial Forensics Checks**:\n"
        for ff_key, ff_val in forensics_data.items():
            if ff_key != 'details': # Don't print the main 'details' here again
                 report_content += f"    - {ff_key.replace('_', ' ').title()}: {ff_val if isinstance(ff_val, str) else ff_val.get('status', 'pending')}\n"
        report_content += f"  - _Overall Forensics Details_: {forensics_data.get('details', 'N/A')}\n"
        report_content += f"- **Intrinsic Value (Average)**: {iv_mos_data.get('intrinsic_value_avg', 'pending')} ({iv_mos_data.get('details', 'N/A')})\n\n"

        report_content += "## Margin of Safety (MoS)\n"
        report_content += f"- **Margin of Safety**: {iv_mos_data.get('mos_pct_at_market_price', 'pending')}\n\n"

        report_content += "## Valuation Scenarios (Base/Bear/Bull)\n"
        report_content += f"- **Base Case IV**: {iv_scenarios.get('base_case_iv', 'pending')}\n"
        report_content += f"- **Bear Case IV**: {iv_scenarios.get('bear_case_iv', 'pending')}\n"
        report_content += f"- **Bull Case IV**: {iv_scenarios.get('bull_case_iv', 'pending')}\n\n"

        report_content += "## Intrinsic Value Comparison\n"
        report_content += "- Comparison to previous quarter's intrinsic value is pending (requires historical analysis data).\n\n"

        report_content += "## Mental Model Conflicts\n"
        report_content += "- Mental model conflict analysis is pending.\n\n"

        # Save Markdown File
        year = str(target_date.year)
        month = f"{target_date.month:02d}"
        day = f"{target_date.day:02d}"
        form_type_cleaned = form_type.replace('/', '-')

        report_filename = f"{form_type_cleaned}_{date_filed}_munger_v{analysis_version}.md"
        save_dir = os.path.join(processed_data_base_path, year, month, day, f"CIK_{cik}") # CIK is already padded
        full_save_path = os.path.join(save_dir, report_filename)

        os.makedirs(save_dir, exist_ok=True)
        with open(full_save_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"Successfully generated Munger Markdown report: {full_save_path}")
        return full_save_path

    except KeyError as e:
        print(f"Error generating Markdown report: Missing key {e} in analysis_data.")
        return None
    except IOError as e:
        print(f"Error saving Markdown report to {full_save_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Markdown report generation for CIK {analysis_data.get('cik', 'Unknown')}: {e}")
        return None
