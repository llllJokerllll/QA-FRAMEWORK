"""
JSON Reporter for QA Framework

Simple JSON test report generator.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class JSONReporter:
    """
    JSON report generator for test results.
    
    Generates JSON reports with test results data.
    """
    
    def __init__(self, config=None):
        """
        Initialize JSON reporter.
        
        Args:
            config: Optional configuration (not used in basic implementation)
        """
        self.config = config
        self.results = []
    
    def report(self, result, output_dir: str) -> str:
        """
        Generate JSON report for a test result.
        
        Args:
            result: TestResult object or similar
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_file = output_path / "report.json"
        
        # Generate JSON report
        json_data = self._generate_json(result)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        return str(report_file)
    
    def _generate_json(self, result) -> Dict[str, Any]:
        """
        Generate JSON data for the report.
        
        Args:
            result: Test result object
            
        Returns:
            Dictionary with report data
        """
        # Extract common attributes from result object
        report_data = {
            "report_type": "qa-framework-test",
            "generated_at": datetime.now().isoformat(),
            "test": {
                "name": getattr(result, 'test_name', 'Unknown Test'),
                "classname": getattr(result, 'classname', ''),
                "status": str(getattr(result, 'status', 'unknown')),
                "duration": getattr(result, 'duration', 0),
                "message": getattr(result, 'message', ''),
                "error": getattr(result, 'error', None),
                "tags": getattr(result, 'tags', []),
            }
        }
        
        # Add any additional attributes from the result
        if hasattr(result, '__dict__'):
            for key, value in result.__dict__.items():
                if key not in report_data["test"]:
                    report_data["test"][key] = value
        
        return report_data
