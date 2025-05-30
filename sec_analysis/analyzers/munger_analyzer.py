"""Charlie Munger-style investment analysis engine."""

import math
import random
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from ..models.analysis import (
    AnalysisResult, MoatDurabilityScore, FinancialForensics, 
    ValuationScenario, MungerFilters
)
from ..models.filing import Filing
import logging

logger = logging.getLogger(__name__)


class MungerAnalyzer:
    """
    Implements Charlie Munger's investment analysis framework.
    
    This analyzer applies Munger's four filters and evaluates companies
    using his principles of business analysis and valuation.
    """
    
    def __init__(self):
        """Initialize the Munger analyzer."""
        self.analysis_version = "2.1"
    
    def analyze_company(self, filing: Filing, filing_content: str, 
                       market_price: Optional[float] = None) -> AnalysisResult:
        """
        Perform comprehensive Munger-style analysis on a company filing.
        
        Args:
            filing: The filing information
            filing_content: Raw content of the filing
            market_price: Current market price per share
            
        Returns:
            Complete analysis result
        """
        logger.info(f"Starting Munger analysis for {filing.company_name} ({filing.cik})")
        
        # Extract financial data from filing content
        financial_data = self._extract_financial_data(filing_content)
        
        # Apply Munger's four filters
        munger_filters = self._evaluate_munger_filters(financial_data)
        
        # Calculate moat durability score
        moat_score = self._calculate_moat_score(filing_content, financial_data)
        
        # Perform financial forensics
        forensics = self._perform_financial_forensics(financial_data)
        
        # Generate valuation scenarios
        valuation_scenarios = self._generate_valuation_scenarios(financial_data)
        
        # Identify business changes and anomalies
        business_changes = self._identify_business_changes(filing_content)
        financial_anomalies = self._identify_financial_anomalies(financial_data)
        insider_transactions = self._extract_insider_transactions(filing_content)
        
        # Check for mental model conflicts
        conflicts = self._identify_mental_model_conflicts(
            munger_filters, moat_score, forensics, financial_data
        )
        
        # Create analysis result
        analysis = AnalysisResult(
            cik=filing.cik,
            company_name=filing.company_name,
            analysis_date=date.today(),
            filing_date=filing.date_filed,
            form_type=filing.form_type,
            moat_score=moat_score,
            financial_forensics=forensics,
            munger_filters=munger_filters,
            valuation_scenarios=valuation_scenarios,
            current_market_price=market_price,
            business_model_changes=business_changes,
            financial_anomalies=financial_anomalies,
            insider_transactions=insider_transactions,
            mental_model_conflicts=conflicts,
            version=self.analysis_version,
            analysis_meta={
                "filing_size_bytes": len(filing_content),
                "analysis_duration_seconds": 0,  # Would be calculated in real implementation
                "confidence_score": self._calculate_confidence_score(financial_data)
            }
        )
        
        # Calculate margin of safety
        analysis.update_margin_of_safety()
        
        logger.info(f"Analysis completed for {filing.company_name}")
        return analysis
    
    def _extract_financial_data(self, content: str) -> Dict[str, Any]:
        """
        Extract financial data from filing content.
        
        In a real implementation, this would parse XBRL data or extract
        from specific sections of the filing.
        """
        # Simplified simulation - in reality would parse actual financial statements
        return {
            "net_income": random.uniform(100_000_000, 10_000_000_000),
            "total_revenue": random.uniform(1_000_000_000, 50_000_000_000),
            "total_assets": random.uniform(5_000_000_000, 100_000_000_000),
            "total_debt": random.uniform(1_000_000_000, 20_000_000_000),
            "shareholders_equity": random.uniform(3_000_000_000, 50_000_000_000),
            "cash_flow_operations": random.uniform(500_000_000, 8_000_000_000),
            "capex": random.uniform(200_000_000, 3_000_000_000),
            "depreciation": random.uniform(300_000_000, 2_000_000_000),
            "shares_outstanding": random.uniform(100_000_000, 5_000_000_000),
            "historical_roe": [random.uniform(0.10, 0.25) for _ in range(5)],
            "historical_revenue": [random.uniform(1_000_000_000, 50_000_000_000) for _ in range(5)]
        }
    
    def _evaluate_munger_filters(self, financial_data: Dict[str, Any]) -> MungerFilters:
        """Apply Munger's four investment filters."""
        
        # Filter 1: ROE >15% for 5 consecutive years
        historical_roe = financial_data.get("historical_roe", [])
        roe_above_15 = len(historical_roe) >= 5 and all(roe > 0.15 for roe in historical_roe)
        
        # Filter 2: Debt/Equity <8%
        debt = financial_data.get("total_debt", 0)
        equity = financial_data.get("shareholders_equity", 1)
        debt_equity_ratio = debt / equity if equity > 0 else float('inf')
        debt_equity_ok = debt_equity_ratio < 0.08
        
        # Filter 3: Management ownership >5% (simulated)
        management_ownership = random.uniform(0.01, 0.25)  # Would extract from proxy statements
        management_ok = management_ownership > 0.05
        
        # Filter 4: Consistent earnings growth (simplified check)
        historical_revenue = financial_data.get("historical_revenue", [])
        consistent_growth = len(historical_revenue) >= 3 and all(
            historical_revenue[i] >= historical_revenue[i-1] * 0.95 
            for i in range(1, len(historical_revenue))
        )
        
        return MungerFilters(
            roe_above_15_for_5_years=roe_above_15,
            debt_equity_below_8_percent=debt_equity_ok,
            management_ownership_above_5_percent=management_ok,
            consistent_earnings_growth=consistent_growth
        )
    
    def _calculate_moat_score(self, content: str, financial_data: Dict[str, Any]) -> MoatDurabilityScore:
        """Calculate the moat durability score based on competitive advantages."""
        
        # In real implementation, would analyze:
        # - Market share data from filing
        # - Patent filings and IP strength
        # - Customer concentration and retention metrics
        # - Pricing power evidence from margin trends
        
        # Simplified scoring for demonstration
        market_share = random.uniform(6.0, 9.5)
        patent_strength = random.uniform(5.0, 9.0)
        customer_retention = random.uniform(7.0, 9.5)
        pricing_power = random.uniform(5.5, 8.5)
        
        return MoatDurabilityScore(
            market_share_stability=market_share,
            patent_portfolio_strength=patent_strength,
            customer_retention_rate=customer_retention,
            pricing_power_evidence=pricing_power
        )
    
    def _perform_financial_forensics(self, financial_data: Dict[str, Any]) -> FinancialForensics:
        """Perform forensic analysis of financial statements."""
        
        # Benford's Law analysis (simplified)
        benford_score = random.uniform(0.7, 0.95)  # Would analyze digit distribution
        
        # CAPEX vs Depreciation analysis
        capex = financial_data.get("capex", 0)
        depreciation = financial_data.get("depreciation", 1)
        capex_depreciation_ratio = capex / depreciation if depreciation > 0 else 0
        
        # True Owner Earnings calculation
        net_income = financial_data.get("net_income", 0)
        maintenance_capex = capex * 0.7  # Estimate maintenance portion
        true_owner_earnings = net_income + depreciation - maintenance_capex
        
        # Historical ROE average
        historical_roe = financial_data.get("historical_roe", [])
        roe_5_year_avg = sum(historical_roe) / len(historical_roe) if historical_roe else 0
        
        # Debt/Equity ratio
        debt = financial_data.get("total_debt", 0)
        equity = financial_data.get("shareholders_equity", 1)
        debt_equity_pct = (debt / equity * 100) if equity > 0 else 0
        
        # Management ownership (would extract from proxy statements)
        management_ownership_pct = random.uniform(2.0, 15.0)
        
        return FinancialForensics(
            benford_law_score=benford_score,
            capex_vs_depreciation_ratio=capex_depreciation_ratio,
            true_owner_earnings=true_owner_earnings,
            roe_5_year_avg=roe_5_year_avg * 100,  # Convert to percentage
            debt_equity_ratio=debt_equity_pct,
            management_ownership_pct=management_ownership_pct
        )
    
    def _generate_valuation_scenarios(self, financial_data: Dict[str, Any]) -> List[ValuationScenario]:
        """Generate three valuation scenarios (Base/Bear/Bull)."""
        
        # Extract key metrics
        net_income = financial_data.get("net_income", 0)
        shares = financial_data.get("shares_outstanding", 1)
        earnings_per_share = net_income / shares if shares > 0 else 0
        
        scenarios = []
        
        # Base Case: 8% discount rate, 2% terminal growth
        base_dcf = self._calculate_dcf(financial_data, 0.08, 0.02)
        base_graham = self._calculate_graham_formula(earnings_per_share)
        base_epv = self._calculate_earnings_power_value(earnings_per_share, 0.08)
        base_iv = (base_dcf + base_graham + base_epv) / 3
        
        scenarios.append(ValuationScenario(
            scenario_name="Base",
            discount_rate=0.08,
            terminal_growth_rate=0.02,
            intrinsic_value=base_iv,
            dcf_value=base_dcf,
            graham_formula_value=base_graham,
            earnings_power_value=base_epv
        ))
        
        # Bear Case: 10% discount rate, 1% terminal growth
        bear_dcf = self._calculate_dcf(financial_data, 0.10, 0.01)
        bear_graham = base_graham * 0.8  # Conservative haircut
        bear_epv = self._calculate_earnings_power_value(earnings_per_share, 0.10)
        bear_iv = (bear_dcf + bear_graham + bear_epv) / 3
        
        scenarios.append(ValuationScenario(
            scenario_name="Bear",
            discount_rate=0.10,
            terminal_growth_rate=0.01,
            intrinsic_value=bear_iv,
            dcf_value=bear_dcf,
            graham_formula_value=bear_graham,
            earnings_power_value=bear_epv
        ))
        
        # Bull Case: 6% discount rate, 3% terminal growth
        bull_dcf = self._calculate_dcf(financial_data, 0.06, 0.03)
        bull_graham = base_graham * 1.2  # Optimistic premium
        bull_epv = self._calculate_earnings_power_value(earnings_per_share, 0.06)
        bull_iv = (bull_dcf + bull_graham + bull_epv) / 3
        
        scenarios.append(ValuationScenario(
            scenario_name="Bull",
            discount_rate=0.06,
            terminal_growth_rate=0.03,
            intrinsic_value=bull_iv,
            dcf_value=bull_dcf,
            graham_formula_value=bull_graham,
            earnings_power_value=bull_epv
        ))
        
        return scenarios
    
    def _calculate_dcf(self, financial_data: Dict[str, Any], discount_rate: float, terminal_growth: float) -> float:
        """Simplified DCF calculation."""
        cash_flow = financial_data.get("cash_flow_operations", 0)
        shares = financial_data.get("shares_outstanding", 1)
        
        # Project 10 years of cash flows with growth
        growth_rate = 0.05  # Assume 5% growth
        terminal_value_year = 10
        
        pv_cash_flows = 0
        for year in range(1, terminal_value_year + 1):
            projected_cf = cash_flow * (1 + growth_rate) ** year
            pv_cf = projected_cf / (1 + discount_rate) ** year
            pv_cash_flows += pv_cf
        
        # Terminal value
        terminal_cf = cash_flow * (1 + growth_rate) ** terminal_value_year * (1 + terminal_growth)
        terminal_value = terminal_cf / (discount_rate - terminal_growth)
        pv_terminal = terminal_value / (1 + discount_rate) ** terminal_value_year
        
        total_value = pv_cash_flows + pv_terminal
        return total_value / shares if shares > 0 else 0
    
    def _calculate_graham_formula(self, eps: float) -> float:
        """Benjamin Graham's intrinsic value formula: IV = EPS * (8.5 + 2g)"""
        growth_rate = 5.0  # Assume 5% growth
        return eps * (8.5 + 2 * growth_rate)
    
    def _calculate_earnings_power_value(self, eps: float, discount_rate: float) -> float:
        """Earnings Power Value: Current earnings / discount rate (no growth)"""
        return eps / discount_rate if discount_rate > 0 else 0
    
    def _identify_business_changes(self, content: str) -> List[str]:
        """Identify business model changes from MD&A section."""
        # Simplified - would analyze MD&A section for key changes
        changes = []
        
        # Look for key phrases (simplified)
        change_indicators = [
            "strategic initiative", "business transformation", "new market",
            "acquisition", "divestiture", "restructuring"
        ]
        
        content_lower = content.lower()
        for indicator in change_indicators:
            if indicator in content_lower:
                changes.append(f"Potential {indicator} mentioned in filing")
        
        return changes[:3]  # Limit to top 3
    
    def _identify_financial_anomalies(self, financial_data: Dict[str, Any]) -> List[str]:
        """Identify financial statement anomalies."""
        anomalies = []
        
        # Check for unusual ratios
        revenue = financial_data.get("total_revenue", 0)
        net_income = financial_data.get("net_income", 0)
        
        if revenue > 0:
            profit_margin = net_income / revenue
            if profit_margin > 0.25:
                anomalies.append(f"Unusually high profit margin: {profit_margin:.1%}")
            elif profit_margin < 0:
                anomalies.append("Company reporting losses")
        
        # Check historical revenue variance
        historical_revenue = financial_data.get("historical_revenue", [])
        if len(historical_revenue) >= 2:
            recent_change = (historical_revenue[-1] - historical_revenue[-2]) / historical_revenue[-2]
            if abs(recent_change) > 0.20:
                anomalies.append(f"Large revenue change: {recent_change:.1%} YoY")
        
        return anomalies
    
    def _extract_insider_transactions(self, content: str) -> List[str]:
        """Extract notable insider transaction patterns."""
        # Simplified - would parse insider trading sections
        transactions = []
        
        # Look for insider trading keywords
        insider_keywords = ["insider", "director", "officer", "purchase", "sale", "stock option"]
        content_lower = content.lower()
        
        found_keywords = [keyword for keyword in insider_keywords if keyword in content_lower]
        if found_keywords:
            transactions.append(f"Insider activity mentioned: {', '.join(found_keywords[:3])}")
        
        return transactions
    
    def _identify_mental_model_conflicts(self, filters: MungerFilters, 
                                       moat_score: MoatDurabilityScore,
                                       forensics: FinancialForensics,
                                       financial_data: Dict[str, Any]) -> List[str]:
        """Identify conflicts with the investment thesis."""
        conflicts = []
        
        # High moat score but fails filters
        if moat_score.total_score > 7.0 and not filters.passes_all_filters:
            conflicts.append("High moat score but fails Munger filters - investigate competitive position")
        
        # High debt with strong business
        if forensics.debt_equity_ratio > 50 and moat_score.total_score > 8.0:
            conflicts.append("Strong moat but high leverage - balance sheet risk")
        
        # Low management ownership for strong business
        if (forensics.management_ownership_pct < 3.0 and 
            moat_score.total_score > 8.0 and 
            filters.roe_above_15_for_5_years):
            conflicts.append("Excellent business metrics but low management skin in the game")
        
        return conflicts
    
    def _calculate_confidence_score(self, financial_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        # Simplified confidence scoring based on data availability
        score = 0.5  # Base score
        
        if financial_data.get("net_income", 0) > 0:
            score += 0.1
        if len(financial_data.get("historical_roe", [])) >= 5:
            score += 0.2
        if financial_data.get("total_revenue", 0) > 1_000_000_000:
            score += 0.1
        
        return min(score, 1.0)