"""
Enhanced GitHub Models integration for LLM-enhanced SEC analysis.

This module provides comprehensive integration with GitHub Models API to enhance
SEC analysis results with Charlie Munger-style investment insights.

Features:
- Multiple model support with configurable selection
- Playwright-based web interface testing
- Robust error handling and fallback mechanisms
- Comprehensive testing and validation
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Literal
from pathlib import Path
import requests
from playwright.async_api import async_playwright

from sec_analysis.models.analysis import AnalysisResult

logger = logging.getLogger(__name__)

# Available GitHub Models with their capabilities
GITHUB_MODELS = {
    "gpt-4o": {
        "name": "GPT-4o",
        "provider": "openai",
        "capabilities": ["chat", "analysis"],
        "context_window": 128000,
        "recommended_for": "complex_analysis",
        "cost_tier": "high"
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini", 
        "provider": "openai",
        "capabilities": ["chat", "analysis"],
        "context_window": 128000,
        "recommended_for": "general_analysis",
        "cost_tier": "low"
    },
    "gpt-35-turbo": {
        "name": "GPT-3.5 Turbo",
        "provider": "openai", 
        "capabilities": ["chat"],
        "context_window": 16385,
        "recommended_for": "simple_tasks",
        "cost_tier": "low"
    },
    "llama-3.2-90b-vision-instruct": {
        "name": "Llama 3.2 90B Vision",
        "provider": "meta",
        "capabilities": ["chat", "vision"],
        "context_window": 128000,
        "recommended_for": "multimodal_analysis",
        "cost_tier": "medium"
    },
    "llama-3.1-405b-instruct": {
        "name": "Llama 3.1 405B",
        "provider": "meta",
        "capabilities": ["chat"],
        "context_window": 128000,
        "recommended_for": "complex_reasoning",
        "cost_tier": "high"
    }
}

# Default model for investment analysis
DEFAULT_MODEL = "gpt-4o-mini"

ModelType = Literal[
    "gpt-4o", "gpt-4o-mini", "gpt-35-turbo", 
    "llama-3.2-90b-vision-instruct", "llama-3.1-405b-instruct"
]


class GitHubModelsAnalyzer:
    """
    Enhanced GitHub Models integration for LLM-enhanced SEC analysis.
    
    This class provides comprehensive integration with GitHub Models API,
    including model selection, web interface testing, and robust error handling.
    """
    
    def __init__(self, model: ModelType = DEFAULT_MODEL):
        """
        Initialize the GitHub Models analyzer.
        
        Args:
            model: The model to use for analysis (default: gpt-4o-mini)
        """
        self.api_base = "https://models.inference.ai.azure.com"
        self.model = model
        self.model_info = GITHUB_MODELS.get(model, GITHUB_MODELS[DEFAULT_MODEL])
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # Configuration
        self.timeout = 60  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found. LLM analysis will be disabled.")
        else:
            logger.info(f"GitHub Models initialized with model: {self.model} ({self.model_info['name']})")
    
    def is_available(self) -> bool:
        """
        Check if GitHub Models API is available.
        
        Returns:
            True if API is available, False otherwise
        """
        return self.github_token is not None
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available models.
        
        Returns:
            Dictionary of available models and their capabilities
        """
        return GITHUB_MODELS.copy()
    
    def set_model(self, model: ModelType) -> bool:
        """
        Set the model to use for analysis.
        
        Args:
            model: The model to use
            
        Returns:
            True if model was set successfully, False if model not available
        """
        if model in GITHUB_MODELS:
            self.model = model
            self.model_info = GITHUB_MODELS[model]
            logger.info(f"Model changed to: {model} ({self.model_info['name']})")
            return True
        else:
            logger.error(f"Model '{model}' not available")
            return False
    
    def get_model_recommendation(self, analysis_complexity: str = "general") -> str:
        """
        Get recommended model based on analysis complexity.
        
        Args:
            analysis_complexity: Type of analysis ("simple", "general", "complex", "multimodal")
            
        Returns:
            Recommended model name
        """
        recommendations = {
            "simple": "gpt-35-turbo",
            "general": "gpt-4o-mini", 
            "complex": "gpt-4o",
            "multimodal": "llama-3.2-90b-vision-instruct"
        }
        
        return recommendations.get(analysis_complexity, DEFAULT_MODEL)
    
    async def test_api_connection(self) -> Dict[str, Any]:
        """
        Test the GitHub Models API connection.
        
        Returns:
            Dictionary with connection test results
        """
        if not self.is_available():
            return {
                "status": "failed",
                "error": "No GitHub token available",
                "model": self.model
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Content-Type": "application/json"
            }
            
            # Simple test message
            test_payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": "Test connection. Respond with 'OK' if you can process this message."
                    }
                ],
                "max_tokens": 10,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "model": self.model,
                    "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "usage": result.get("usage", {})
                }
            else:
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "model": self.model
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "model": self.model
            }
    
    async def test_with_playwright(self) -> Dict[str, Any]:
        """
        Test GitHub Models web interface using Playwright.
        
        This function tests the web interface to ensure models are accessible
        and provides additional validation beyond API calls.
        
        Returns:
            Dictionary with web interface test results
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to GitHub Models documentation or interface
                await page.goto("https://github.com/marketplace/models")
                
                # Wait for page to load
                await page.wait_for_load_state("networkidle", timeout=10000)
                
                # Check if we can access the models page
                title = await page.title()
                
                # Look for model availability indicators
                models_visible = await page.locator("text=GPT").count() > 0
                
                await browser.close()
                
                return {
                    "status": "success",
                    "page_title": title,
                    "models_visible": models_visible,
                    "test_type": "playwright_web_interface"
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "test_type": "playwright_web_interface"
            }
    
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
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            # Make the API request with retry logic
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        enhanced_analysis = result["choices"][0]["message"]["content"]
                        
                        logger.info(f"Successfully enhanced analysis using {self.model}")
                        return enhanced_analysis
                    
                    elif response.status_code == 429:  # Rate limited
                        logger.warning(f"Rate limited, retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                        continue
                    
                    else:
                        logger.error(f"API request failed: {response.status_code} - {response.text}")
                        return None
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"Request timeout, attempt {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    else:
                        logger.error("All retry attempts failed")
                        return None
                        
        except Exception as e:
            logger.error(f"Error enhancing analysis: {e}")
            return None
    
    def _format_user_prompt(self, template: str, analysis: AnalysisResult) -> str:
        """
        Format the user prompt template with analysis data.
        
        Args:
            template: The prompt template
            analysis: The analysis result
            
        Returns:
            Formatted prompt string
        """
        try:
            # Create a data dictionary for template formatting
            data = {
                'company_name': analysis.company_name,
                'cik': analysis.cik,
                'form_type': analysis.form_type,
                'analysis_date': analysis.analysis_date,
                'moat_score': analysis.moat_score.total_score,
                'margin_of_safety': analysis.margin_of_safety or 0.0,
                'passes_filters': analysis.munger_filters.passes_all_filters,
                'roe_5_year': analysis.financial_forensics.roe_5_year_avg,
                'debt_ratio': analysis.financial_forensics.debt_equity_ratio,
                'management_ownership': analysis.financial_forensics.management_ownership_pct,
                'bear_case': analysis.valuation_scenarios[0].intrinsic_value,
                'base_case': analysis.valuation_scenarios[1].intrinsic_value,
                'bull_case': analysis.valuation_scenarios[2].intrinsic_value
            }
            
            return template.format(**data)
            
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            return template  # Return unformatted template as fallback
    
    async def comprehensive_test(self) -> Dict[str, Any]:
        """
        Run comprehensive tests of GitHub Models functionality.
        
        Returns:
            Dictionary with comprehensive test results
        """
        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "model": self.model,
            "model_info": self.model_info,
            "tests": {}
        }
        
        # Test 1: Basic availability
        results["tests"]["availability"] = {
            "available": self.is_available(),
            "has_token": self.github_token is not None
        }
        
        if not self.is_available():
            results["overall_status"] = "skipped"
            return results
        
        # Test 2: API Connection
        logger.info("Testing API connection...")
        api_test = await self.test_api_connection()
        results["tests"]["api_connection"] = api_test
        
        # Test 3: Playwright Web Interface
        logger.info("Testing web interface with Playwright...")
        playwright_test = await self.test_with_playwright()
        results["tests"]["playwright"] = playwright_test
        
        # Test 4: Model Information
        results["tests"]["model_info"] = {
            "current_model": self.model,
            "available_models": list(GITHUB_MODELS.keys()),
            "model_capabilities": self.model_info
        }
        
        # Overall status
        api_success = api_test.get("status") == "success"
        playwright_success = playwright_test.get("status") == "success"
        
        if api_success and playwright_success:
            results["overall_status"] = "success"
        elif api_success:
            results["overall_status"] = "partial"  # API works but web interface issues
        else:
            results["overall_status"] = "failed"
        
        return results


def get_recommended_model_for_analysis(analysis_result: AnalysisResult) -> str:
    """
    Get recommended model based on analysis characteristics.
    
    Args:
        analysis_result: The analysis result to evaluate
        
    Returns:
        Recommended model name
    """
    # Complex analysis indicators
    has_complex_financials = (
        len(analysis_result.financial_anomalies) > 3 or
        len(analysis_result.business_model_changes) > 2 or
        analysis_result.financial_forensics.benford_law_score < 5.0
    )
    
    has_high_moat = analysis_result.moat_score.total_score >= 8.0
    
    # Model selection logic
    if has_complex_financials and has_high_moat:
        return "gpt-4o"  # Use most capable model for complex cases
    elif has_complex_financials or has_high_moat:
        return "gpt-4o-mini"  # Good balance of capability and cost
    else:
        return "gpt-35-turbo"  # Simple cases