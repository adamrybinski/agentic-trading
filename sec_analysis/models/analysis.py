"""Analysis result data models following Munger's investment framework."""

from datetime import date, datetime
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field


class MoatDurabilityScore(BaseModel):
    """Munger-style moat durability assessment."""
    
    market_share_stability: float = Field(..., ge=0, le=10, description="Market share stability score")
    patent_portfolio_strength: float = Field(..., ge=0, le=10, description="Patent portfolio score")
    customer_retention_rate: float = Field(..., ge=0, le=10, description="Customer retention score")
    pricing_power_evidence: float = Field(..., ge=0, le=10, description="Pricing power score")
    
    @property
    def total_score(self) -> float:
        """Calculate weighted total moat durability score."""
        return (
            self.market_share_stability * 0.4 +
            self.patent_portfolio_strength * 0.3 +
            self.customer_retention_rate * 0.2 +
            self.pricing_power_evidence * 0.1
        )


class FinancialForensics(BaseModel):
    """Financial analysis using forensic accounting techniques."""
    
    benford_law_score: float = Field(..., description="Benford's law compliance score")
    capex_vs_depreciation_ratio: float = Field(..., description="CAPEX to depreciation ratio")
    true_owner_earnings: float = Field(..., description="Calculated true owner earnings")
    roe_5_year_avg: float = Field(..., description="5-year average ROE")
    debt_equity_ratio: float = Field(..., description="Debt to equity ratio")
    management_ownership_pct: float = Field(..., description="Management ownership percentage")


class ValuationScenario(BaseModel):
    """Valuation scenario with specific assumptions."""
    
    scenario_name: Literal["Base", "Bear", "Bull"] = Field(..., description="Scenario type")
    discount_rate: float = Field(..., description="Discount rate used")
    terminal_growth_rate: float = Field(..., description="Terminal growth rate")
    intrinsic_value: float = Field(..., description="Calculated intrinsic value")
    dcf_value: float = Field(..., description="DCF valuation")
    graham_formula_value: float = Field(..., description="Benjamin Graham formula value")
    earnings_power_value: float = Field(..., description="Earnings power value")


class MungerFilters(BaseModel):
    """Charlie Munger's 4 investment filters."""
    
    roe_above_15_for_5_years: bool = Field(..., description="ROE >15% for 5 consecutive years")
    debt_equity_below_8_percent: bool = Field(..., description="Debt/Equity <8%")
    management_ownership_above_5_percent: bool = Field(..., description="Management ownership >5%")
    consistent_earnings_growth: bool = Field(..., description="Consistent earnings growth")
    
    @property
    def passes_all_filters(self) -> bool:
        """Check if company passes all Munger filters."""
        return all([
            self.roe_above_15_for_5_years,
            self.debt_equity_below_8_percent,
            self.management_ownership_above_5_percent,
            self.consistent_earnings_growth
        ])


class AnalysisResult(BaseModel):
    """Versioned data model for complete analysis results."""
    
    cik: str = Field(..., min_length=10, max_length=10, description="10-digit CIK")
    company_name: str = Field(..., description="Company name")
    analysis_date: date = Field(..., description="Date of analysis")
    filing_date: date = Field(..., description="Date of the analyzed filing")
    form_type: str = Field(..., description="Type of filing analyzed")
    
    # Core Munger Analysis
    moat_score: MoatDurabilityScore = Field(..., description="Moat durability assessment")
    financial_forensics: FinancialForensics = Field(..., description="Financial forensics results")
    munger_filters: MungerFilters = Field(..., description="Munger's 4 filters assessment")
    
    # Valuation Analysis
    valuation_scenarios: List[ValuationScenario] = Field(..., description="Three valuation scenarios")
    current_market_price: Optional[float] = Field(None, description="Current market price")
    margin_of_safety: Optional[float] = Field(None, description="Calculated margin of safety")
    
    # Business Analysis
    business_model_changes: List[str] = Field(default_factory=list, description="Identified business model changes")
    financial_anomalies: List[str] = Field(default_factory=list, description="Financial statement anomalies")
    insider_transactions: List[str] = Field(default_factory=list, description="Notable insider transactions")
    
    # Mental Model Conflicts
    mental_model_conflicts: List[str] = Field(default_factory=list, description="Identified conflicts with investment thesis")
    
    # Metadata
    version: Literal["2.1"] = Field(default="2.1", description="Analysis schema version")
    analysis_meta: Dict[str, Any] = Field(default_factory=dict, description="Flexible storage for additional metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis creation timestamp")
    
    def calculate_margin_of_safety(self) -> Optional[float]:
        """Calculate margin of safety based on base case valuation."""
        if not self.current_market_price:
            return None
            
        base_scenario = next((s for s in self.valuation_scenarios if s.scenario_name == "Base"), None)
        if not base_scenario:
            return None
            
        return (base_scenario.intrinsic_value - self.current_market_price) / base_scenario.intrinsic_value
    
    def update_margin_of_safety(self):
        """Update the margin of safety field."""
        self.margin_of_safety = self.calculate_margin_of_safety()