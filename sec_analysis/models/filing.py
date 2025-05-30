"""Data models for SEC filings and related entities."""

from datetime import date, datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class Filing(BaseModel):
    """Represents a single SEC filing."""
    
    cik: str = Field(..., min_length=10, max_length=10, description="10-digit CIK")
    company_name: str = Field(..., description="Company name")
    form_type: str = Field(..., description="Filing form type (10-K, 10-Q, 8-K, etc.)")
    date_filed: date = Field(..., description="Date the filing was submitted")
    filename: str = Field(..., description="Filename in SEC archives")
    url: str = Field(..., description="Full URL to the filing")
    

class CompanyMetadata(BaseModel):
    """Metadata for a company organized by CIK."""
    
    cik: str = Field(..., min_length=10, max_length=10, description="10-digit CIK")
    company_name: str = Field(..., description="Official company name")
    ticker: Optional[str] = Field(None, description="Stock ticker symbol")
    forms: List[str] = Field(default_factory=list, description="Available form types")
    first_filed: Optional[date] = Field(None, description="Date of first filing")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    analysis_version: str = Field(default="2.1", description="Analysis schema version")
    
    
class MasterIndexEntry(BaseModel):
    """Represents an entry from the SEC master index file."""
    
    cik: str
    company_name: str
    form_type: str
    date_filed: str
    filename: str
    
    def to_filing(self) -> Filing:
        """Convert to a Filing object with proper URL."""
        base_url = "https://www.sec.gov/Archives/"
        
        # Parse date string - handle different formats
        if len(self.date_filed) == 8:  # YYYYMMDD
            parsed_date = date(
                int(self.date_filed[:4]),
                int(self.date_filed[4:6]),
                int(self.date_filed[6:8])
            )
        else:  # YYYY-MM-DD
            parsed_date = date.fromisoformat(self.date_filed)
        
        return Filing(
            cik=self.cik.zfill(10),
            company_name=self.company_name,
            form_type=self.form_type,
            date_filed=parsed_date,
            filename=self.filename,
            url=f"{base_url}{self.filename}"
        )