"""Parser for SEC master index files."""

import re
from datetime import date
from typing import List, Iterator
from ..models.filing import MasterIndexEntry, Filing
import logging

logger = logging.getLogger(__name__)


class MasterIndexParser:
    """Parses SEC master index files and extracts filing information."""
    
    # Target form types for analysis
    TARGET_FORMS = {'10-K', '10-Q', '8-K', 'DEF 14A', 'NT 10-K', 'NT 10-Q', '10-K/A', '10-Q/A', 'SCHEDULE 13G', 'SCHEDULE 13G/A'}
    
    def __init__(self):
        """Initialize the parser."""
        self.cik_pattern = re.compile(r'^\d{1,10}$')
    
    def parse_master_index(self, content: str) -> List[MasterIndexEntry]:
        """
        Parse the master index file content and extract filing entries.
        
        Args:
            content: Raw content of the master index file
            
        Returns:
            List of MasterIndexEntry objects
        """
        entries = []
        lines = content.split('\n')
        
        # Skip header lines (usually first 10-11 lines contain metadata)
        data_start = self._find_data_start(lines)
        
        for line_num, line in enumerate(lines[data_start:], start=data_start):
            if not line.strip():
                continue
                
            try:
                entry = self._parse_line(line)
                if entry and self._should_include_entry(entry):
                    entries.append(entry)
            except Exception as e:
                logger.warning(f"Failed to parse line {line_num}: {line[:50]}... Error: {e}")
                continue
        
        logger.info(f"Parsed {len(entries)} relevant entries from master index")
        return entries
    
    def _find_data_start(self, lines: List[str]) -> int:
        """Find the line where actual data starts (after headers)."""
        for i, line in enumerate(lines):
            # Look for the separator line with dashes
            if '----' in line or (i > 5 and '|' in line and len(line.split('|')) >= 4):
                return i + 1
        
        # Fallback: assume data starts after line 10
        return min(10, len(lines))
    
    def _parse_line(self, line: str) -> MasterIndexEntry:
        """
        Parse a single line from the master index.
        
        The format is typically:
        CIK|Company Name|Form Type|Date Filed|File Name
        """
        # Clean the line
        line = line.strip()
        
        # Try pipe-delimited format first
        if '|' in line:
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 5:
                cik, company_name, form_type, date_filed, filename = parts[:5]
                return self._create_entry(cik, company_name, form_type, date_filed, filename)
        
        # Try space-delimited format (older format)
        parts = line.split()
        if len(parts) >= 5:
            # CIK is typically the first numeric field
            cik = parts[0]
            # Filename is typically the last field with a file extension
            filename = parts[-1]
            # Form type and date are usually in the middle
            # This is a simplified parser - real implementation might need more sophistication
            form_type = parts[1] if len(parts) > 1 else ""
            date_filed = parts[2] if len(parts) > 2 else ""
            # Company name is everything in between
            company_name = " ".join(parts[3:-1]) if len(parts) > 4 else ""
            
            return self._create_entry(cik, company_name, form_type, date_filed, filename)
        
        return None
    
    def _create_entry(self, cik: str, company_name: str, form_type: str, 
                     date_filed: str, filename: str) -> MasterIndexEntry:
        """Create a MasterIndexEntry with validation."""
        # Clean and validate CIK
        cik_clean = re.sub(r'\D', '', cik)  # Remove non-digits
        if not cik_clean or not self.cik_pattern.match(cik_clean):
            raise ValueError(f"Invalid CIK: {cik}")
        
        # Pad CIK to 10 digits
        cik_padded = cik_clean.zfill(10)
        
        # Clean company name
        company_name = company_name.strip().upper()
        
        # Validate form type
        form_type = form_type.strip().upper()
        
        # Validate and format date
        date_clean = self._parse_date(date_filed)
        
        return MasterIndexEntry(
            cik=cik_padded,
            company_name=company_name,
            form_type=form_type,
            date_filed=date_clean,
            filename=filename.strip()
        )
    
    def _parse_date(self, date_str: str) -> str:
        """Parse and validate the date string."""
        # Remove any extra whitespace
        date_str = date_str.strip()
        
        # Common formats: YYYY-MM-DD, YYYYMMDD, MM/DD/YYYY
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str
        elif re.match(r'\d{8}', date_str):
            # YYYYMMDD format
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        elif re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
            # MM/DD/YYYY format
            month, day, year = date_str.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            raise ValueError(f"Invalid date format: {date_str}")
    
    def _should_include_entry(self, entry: MasterIndexEntry) -> bool:
        """Determine if an entry should be included in the results."""
        return entry.form_type in self.TARGET_FORMS
    
    def filter_by_forms(self, entries: List[MasterIndexEntry], 
                       forms: List[str] = None) -> List[MasterIndexEntry]:
        """Filter entries by specific form types."""
        if forms is None:
            forms = list(self.TARGET_FORMS)
        
        forms_upper = [f.upper() for f in forms]
        return [entry for entry in entries if entry.form_type in forms_upper]
    
    def group_by_cik(self, entries: List[MasterIndexEntry]) -> dict:
        """Group entries by CIK."""
        cik_groups = {}
        for entry in entries:
            if entry.cik not in cik_groups:
                cik_groups[entry.cik] = []
            cik_groups[entry.cik].append(entry)
        return cik_groups