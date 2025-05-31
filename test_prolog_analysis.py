#!/usr/bin/env python3
"""
SWI-Prolog Testing System for Investment Analysis Data

This script tests the generated Prolog knowledge base files to ensure they can be:
1. Loaded into SWI-Prolog without syntax errors
2. Queried for logical investment analysis
3. Used for decision-making logic

Requirements:
- SWI-Prolog installed (apt-get install swi-prolog)
- Generated .md files with Prolog facts in reports directory
"""

import subprocess
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrologAnalysisTester:
    """Test SWI-Prolog integration for investment analysis."""
    
    def __init__(self, reports_path: str = "reports"):
        """Initialize the Prolog tester."""
        self.reports_path = Path(reports_path)
        self.swipl_available = self._check_swipl_installation()
        
    def _check_swipl_installation(self) -> bool:
        """Check if SWI-Prolog is installed."""
        try:
            result = subprocess.run(['swipl', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"SWI-Prolog found: {result.stdout.strip()}")
                return True
            else:
                logger.warning("SWI-Prolog not found or not working")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("SWI-Prolog not installed. Install with: apt-get install swi-prolog")
            return False
    
    def find_prolog_files(self) -> List[Path]:
        """Find all Prolog analysis files."""
        prolog_files = []
        for date_dir in self.reports_path.iterdir():
            if date_dir.is_dir():
                for file in date_dir.glob("munger_analysis_summary_*.md"):
                    prolog_files.append(file)
        return prolog_files
    
    def validate_prolog_syntax(self, prolog_file: Path) -> Dict[str, Any]:
        """Validate Prolog file syntax using SWI-Prolog."""
        if not self.swipl_available:
            return {"status": "skipped", "reason": "SWI-Prolog not available"}
        
        try:
            # Create a temporary Prolog file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as temp_file:
                # Copy content from .md file to .pl file
                with open(prolog_file, 'r') as f:
                    content = f.read()
                temp_file.write(content)
                temp_pl_file = temp_file.name
            
            # Test loading the file in SWI-Prolog
            test_query = f"""
                consult('{temp_pl_file}'),
                halt.
            """
            
            result = subprocess.run(
                ['swipl', '-g', test_query],
                capture_output=True, text=True, timeout=30
            )
            
            # Clean up temporary file
            Path(temp_pl_file).unlink()
            
            if result.returncode == 0:
                return {
                    "status": "valid",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "status": "invalid",
                    "error": result.stderr,
                    "stdout": result.stdout
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_investment_queries(self, prolog_file: Path) -> Dict[str, Any]:
        """Test investment analysis queries on the Prolog file."""
        if not self.swipl_available:
            return {"status": "skipped", "reason": "SWI-Prolog not available"}
        
        try:
            # Create a temporary Prolog file for testing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pl', delete=False) as temp_file:
                # Copy content from .md file to .pl file
                with open(prolog_file, 'r') as f:
                    content = f.read()
                temp_file.write(content)
                temp_pl_file = temp_file.name
            
            # Test queries - simpler ones first
            test_queries = [
                # Simple query to test basic facts
                "company('0000320193', _, _, _), write('Found Apple Inc'), nl.",
                
                # Count companies
                "findall(CIK, company(CIK, _, _, _), Companies), length(Companies, Count), write('Total companies: '), write(Count), nl.",
                
                # Find excellent investments
                "findall(CIK, excellent_investment(CIK), ExcellentList), length(ExcellentList, ExcellentCount), write('Excellent investments: '), write(ExcellentCount), nl.",
                
                # Find good investments  
                "findall(CIK, good_investment(CIK), GoodList), length(GoodList, GoodCount), write('Good investments: '), write(GoodCount), nl.",
                
                # Check specific facts
                "passes_all_munger_filters('0000320193', Status), write('Apple filters: '), write(Status), nl."
            ]
            
            query_results = {}
            
            for i, query in enumerate(test_queries):
                test_program = f"""
                    consult('{temp_pl_file}'),
                    {query}
                    halt.
                """
                
                result = subprocess.run(
                    ['swipl', '-g', test_program],
                    capture_output=True, text=True, timeout=10  # Reduced timeout
                )
                
                query_results[f"query_{i+1}"] = {
                    "query": query,
                    "success": result.returncode == 0,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip() if result.stderr else None
                }
            
            # Clean up temporary file
            Path(temp_pl_file).unlink()
            
            return {
                "status": "completed",
                "results": query_results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_comprehensive_test(self, prolog_file: Path) -> Dict[str, Any]:
        """Run comprehensive test on a Prolog file."""
        logger.info(f"Testing Prolog file: {prolog_file}")
        
        results = {
            "file": str(prolog_file),
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Syntax validation
        logger.info("Running syntax validation...")
        syntax_result = self.validate_prolog_syntax(prolog_file)
        results["tests"]["syntax"] = syntax_result
        
        if syntax_result["status"] == "valid":
            # Test 2: Investment queries
            logger.info("Running investment queries...")
            query_result = self.test_investment_queries(prolog_file)
            results["tests"]["queries"] = query_result
        else:
            logger.warning("Skipping query tests due to syntax errors")
            results["tests"]["queries"] = {"status": "skipped", "reason": "syntax errors"}
        
        return results
    
    def test_all_prolog_files(self) -> Dict[str, Any]:
        """Test all available Prolog files."""
        prolog_files = self.find_prolog_files()
        
        if not prolog_files:
            logger.warning("No Prolog analysis files found")
            return {"status": "no_files", "results": []}
        
        logger.info(f"Found {len(prolog_files)} Prolog files to test")
        
        all_results = {
            "test_summary": {
                "total_files": len(prolog_files),
                "timestamp": datetime.now().isoformat(),
                "swipl_available": self.swipl_available
            },
            "file_results": []
        }
        
        for prolog_file in prolog_files:
            file_result = self.run_comprehensive_test(prolog_file)
            all_results["file_results"].append(file_result)
        
        # Generate summary statistics
        if all_results["file_results"]:
            syntax_valid = sum(1 for r in all_results["file_results"] 
                             if r["tests"]["syntax"]["status"] == "valid")
            queries_successful = sum(1 for r in all_results["file_results"] 
                                   if r["tests"].get("queries", {}).get("status") == "completed")
            
            all_results["test_summary"].update({
                "syntax_valid_count": syntax_valid,
                "queries_successful_count": queries_successful,
                "overall_success_rate": f"{(queries_successful / len(prolog_files)) * 100:.1f}%"
            })
        
        return all_results
    
    def save_test_results(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """Save test results to a JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"prolog_test_results_{timestamp}.json"
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Test results saved to: {output_path}")
        return output_path


def main():
    """Main function to run Prolog analysis tests."""
    tester = PrologAnalysisTester()
    
    # Run comprehensive tests
    results = tester.test_all_prolog_files()
    
    # Save results
    output_file = tester.save_test_results(results)
    
    # Print summary
    print("\n" + "="*60)
    print("PROLOG ANALYSIS TEST SUMMARY")
    print("="*60)
    
    summary = results.get("test_summary", {})
    print(f"Total files tested: {summary.get('total_files', 0)}")
    print(f"SWI-Prolog available: {summary.get('swipl_available', False)}")
    
    if summary.get("total_files", 0) > 0:
        print(f"Syntax valid: {summary.get('syntax_valid_count', 0)}")
        print(f"Queries successful: {summary.get('queries_successful_count', 0)}")
        print(f"Overall success rate: {summary.get('overall_success_rate', '0%')}")
    
    print(f"Detailed results: {output_file}")
    print("="*60)
    
    # Return exit code based on success
    if summary.get('queries_successful_count', 0) == summary.get('total_files', 0) and summary.get('total_files', 0) > 0:
        return 0
    else:
        return 1 if summary.get('total_files', 0) > 0 else 0  # Don't fail if no files found


if __name__ == "__main__":
    import sys
    sys.exit(main())