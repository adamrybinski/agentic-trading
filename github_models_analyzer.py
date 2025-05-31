"""
GitHub Models integration for LLM-enhanced SEC analysis.

This module provides integration with GitHub Models API to enhance
SEC analysis results with Charlie Munger-style investment insights.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests

from sec_analysis.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)


class GitHubModelsAnalyzer:
    """Integrates with GitHub Models API for LLM analysis."""
    
    def __init__(self):
        """Initialize the GitHub Models analyzer."""
        self.api_base = "https://models.inference.ai.azure.com"
        self.model = "gpt-4o-mini"  # Use the smaller model for cost efficiency
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found. LLM analysis will be disabled.")
    
    def is_available(self) -> bool:
        """Check if GitHub Models API is available."""
        return self.github_token is not None
    
    async def enhance_analysis(self, analysis_result: AnalysisResult, 
                             system_prompt: str, user_prompt_template: str) -> Optional[str]:
        """
        Enhance analysis result with LLM insights.
        
        Args:
            analysis_result: The SEC analysis result to enhance
            system_prompt: Charlie Munger system prompt
            user_prompt_template: User prompt template to format with analysis data
            
        Returns:
            LLM-generated analysis or None if failed
        """
        if not self.is_available():
            logger.warning("GitHub Models not available")
            return None
        
        try:
            # Format the user prompt with analysis data
            user_prompt = self._format_user_prompt(user_prompt_template, analysis_result)
            
            # Call GitHub Models API
            response = await self._call_github_models(system_prompt, user_prompt)
            
            if response:
                logger.info(f"Successfully generated LLM analysis for {analysis_result.company_name}")
                return response
            else:
                logger.error(f"Failed to generate LLM analysis for {analysis_result.company_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error enhancing analysis for {analysis_result.company_name}: {e}")
            return None
    
    def _format_user_prompt(self, template: str, analysis: AnalysisResult) -> str:
        """Format user prompt template with analysis data."""
        # Extract key metrics for formatting
        bear_scenario = analysis.valuation_scenarios[0] if len(analysis.valuation_scenarios) > 0 else None
        base_scenario = analysis.valuation_scenarios[1] if len(analysis.valuation_scenarios) > 1 else None
        bull_scenario = analysis.valuation_scenarios[2] if len(analysis.valuation_scenarios) > 2 else None
        
        # Build red flags list
        red_flags = []
        if analysis.munger_filters.debt_level < 7:
            red_flags.append("High debt levels")
        if analysis.munger_filters.understanding < 7:
            red_flags.append("Complex business model")
        if analysis.munger_filters.prospects < 7:
            red_flags.append("Uncertain long-term prospects")
        if analysis.munger_filters.price < 7:
            red_flags.append("Expensive valuation")
        
        red_flags_text = "\n".join([f"- {flag}" for flag in red_flags]) if red_flags else "- No major red flags identified"
        
        # Format the template
        formatted_prompt = template.format(
            company_name=analysis.company_name,
            cik=analysis.cik,
            form_type=analysis.form_type,
            filing_date=analysis.filing_date,
            moat_score=analysis.moat_score,
            management_score=analysis.munger_filters.management,
            financial_score=analysis.munger_filters.debt_level,
            filter_status="PASS" if analysis.passes_all_filters() else "FAIL",
            investment_grade=analysis.investment_grade,
            margin_of_safety=analysis.margin_of_safety or 0,
            revenue=analysis.revenue or 0,
            net_income=analysis.net_income or 0,
            total_assets=analysis.total_assets or 0,
            total_debt=analysis.total_debt or 0,
            cash=analysis.cash_and_equivalents or 0,
            roe=analysis.roe or 0,
            debt_to_equity=analysis.debt_to_equity or 0,
            moat_assessment=self._get_moat_assessment(analysis.moat_score),
            business_model_changes="Yes" if analysis.business_model_changes else "No",
            mda_sentiment=analysis.mda_sentiment,
            bear_fair_value=bear_scenario.fair_value if bear_scenario else 0,
            bear_margin=bear_scenario.margin_of_safety if bear_scenario else 0,
            base_fair_value=base_scenario.fair_value if base_scenario else 0,
            base_margin=base_scenario.margin_of_safety if base_scenario else 0,
            bull_fair_value=bull_scenario.fair_value if bull_scenario else 0,
            bull_margin=bull_scenario.margin_of_safety if bull_scenario else 0,
            red_flags=red_flags_text
        )
        
        return formatted_prompt
    
    def _get_moat_assessment(self, moat_score: float) -> str:
        """Get textual assessment of moat score."""
        if moat_score >= 8:
            return "Wide economic moat with strong competitive advantages"
        elif moat_score >= 6:
            return "Moderate competitive advantages"
        elif moat_score >= 4:
            return "Some competitive positioning"
        else:
            return "Limited competitive differentiation"
    
    async def _call_github_models(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        """Call GitHub Models API."""
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        try:
            # Use requests for synchronous call (can be made async later if needed)
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Invalid response format: {result}")
                    return None
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling GitHub Models API: {e}")
            return None
    
    def save_enhanced_analysis(self, company_cik: str, analysis_date: str, 
                             enhanced_content: str, reports_path: str):
        """Save LLM-enhanced analysis to file."""
        try:
            reports_dir = Path(reports_path) / analysis_date / company_cik
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Save enhanced analysis
            enhanced_file = reports_dir / f"munger_llm_analysis_{analysis_date.replace('-', '')}.md"
            enhanced_file.write_text(enhanced_content)
            
            logger.info(f"Saved LLM-enhanced analysis: {enhanced_file}")
            
        except Exception as e:
            logger.error(f"Failed to save enhanced analysis for {company_cik}: {e}")