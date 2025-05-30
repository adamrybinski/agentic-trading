#!/usr/bin/env python3
"""
Standalone script to combine SEC analysis reports into one big markdown file.
This is a simple wrapper around the combine_all_reports functionality.
"""

import sys
from pathlib import Path
from datetime import date, datetime
import argparse

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fixed_reports import FixedReportGenerator


def main():
    """Main function to combine reports."""
    parser = argparse.ArgumentParser(
        description='Combine all SEC analysis reports for a date into one big markdown file',
        epilog='''
Examples:
  python combine_reports.py --date 2025-05-30
  python combine_reports.py --date 2025-05-30 --reports-dir /custom/reports
  python combine_reports.py --date 2025-05-30 --output combined_analysis.md
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--date', type=str, required=True,
                       help='Date to combine reports for (YYYY-MM-DD)')
    parser.add_argument('--reports-dir', type=str, default='reports',
                       help='Base directory where reports are stored (default: reports)')
    parser.add_argument('--output', type=str, 
                       help='Output filename (default: all_reports_YYYYMMDD.md)')
    
    args = parser.parse_args()
    
    # Parse and validate date
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD format.")
        sys.exit(1)
    
    # Create report generator
    generator = FixedReportGenerator()
    
    # Check if reports directory exists
    reports_dir = Path(args.reports_dir) / target_date.strftime('%Y-%m-%d')
    if not reports_dir.exists():
        print(f"Error: Reports directory does not exist: {reports_dir}")
        print(f"Please ensure reports have been generated for {target_date}")
        sys.exit(1)
    
    print(f"Combining reports for {target_date.strftime('%B %d, %Y')}...")
    print(f"Source directory: {reports_dir}")
    
    # Combine reports
    try:
        generator.combine_all_reports(target_date, args.reports_dir)
        
        # Determine output filename
        if args.output:
            output_path = Path(args.output)
            default_output = Path(args.reports_dir) / f"all_reports_{target_date.strftime('%Y%m%d')}.md"
            if output_path != default_output:
                # Move/rename the file if custom output name specified
                default_output.rename(output_path)
                print(f"✅ Combined report saved as: {output_path}")
            else:
                print(f"✅ Combined report saved as: {default_output}")
        else:
            output_path = Path(args.reports_dir) / f"all_reports_{target_date.strftime('%Y%m%d')}.md"
            print(f"✅ Combined report saved as: {output_path}")
        
        # Show summary statistics
        if output_path.exists():
            file_size = output_path.stat().st_size
            content = output_path.read_text()
            company_count = content.count("### Company")
            line_count = len(content.split('\n'))
            
            print(f"📊 Report Statistics:")
            print(f"   - File size: {file_size:,} bytes")
            print(f"   - Lines: {line_count:,}")
            print(f"   - Companies: {company_count}")
            print(f"   - Sections: Executive Summary, Individual Analysis, CSV Summary")
            
    except Exception as e:
        print(f"Error: Failed to combine reports: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()