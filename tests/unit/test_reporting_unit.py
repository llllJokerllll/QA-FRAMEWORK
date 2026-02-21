"""
Unit tests for Reporting System (Allure, HTML, JSON)
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.entities.test_result import TestResult, TestStatus
from src.adapters.reporting.allure_reporter import AllureReporter
from src.adapters.reporting.html_reporter import HTMLReporter
from src.adapters.reporting.json_reporter import JSONReporter


class TestAllureReporter:
    """Unit tests for AllureReporter"""
    
    def test_allure_reporter_initialization(self):
        """Test that AllureReporter can be initialized"""
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = AllureReporter(results_dir="allure-results")
        
        assert reporter is not None
        assert reporter.results_dir == "allure-results"
    
    def test_allure_report_report(self):
        """Test that AllureReporter can generate a report"""
        from src.core.entities.test_result import TestResult
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = AllureReporter(results_dir="allure-results")
        
        result = TestResult(
            test_name="test_allure",
            status=TestStatus.PASSED,
            execution_time=1.5,
            metadata={"feature": "reporting"}
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify that allure files were created
            allure_files = list(tmpdir_path.glob("*.xml"))
            assert len(allure_files) > 0


class TestHTMLReporter:
    """Unit tests for HTMLReporter"""
    
    def test_html_reporter_initialization(self):
        """Test that HTMLReporter can be initialized"""
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = HTMLReporter()
        
        assert reporter is not None
        assert reporter.output_dir == "html-results"
    
    def test_html_report_generation(self):
        """Test that HTMLReporter can generate an HTML report"""
        from src.core.entities.test_result import TestResult
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = HTMLReporter()
        
        result = TestResult(
            test_name="test_html",
            status=TestStatus.PASSED,
            execution_time=1.5,
            metadata={"feature": "reporting"}
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify that HTML file was created
            html_files = list(tmpdir_path.glob("*.html"))
            assert len(html_files) > 0


class TestJSONReporter:
    """Unit tests for JSONReporter"""
    
    def test_json_reporter_initialization(self):
        """Test that JSONReporter can be initialized"""
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = JSONReporter()
        
        assert reporter is not None
        assert reporter.output_dir == "json-results"
    
    def test_json_report_generation(self):
        """Test that JSONReporter can generate a JSON report"""
        from src.core.entities.test_result import TestResult
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporter = JSONReporter()
        
        result = TestResult(
            test_name="test_json",
            status=TestStatus.PASSED,
            execution_time=1.5,
            metadata={"feature": "reporting"}
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify that JSON file was created
            json_files = list(tmpdir_path.glob("*.json"))
            assert len(json_files) > 0


class TestReportingIntegration:
    """Integration tests for the entire reporting system"""
    
    def test_allure_html_integration(self):
        """Test that Allure and HTML reporters work together"""
        from src.core.entities.test_result import TestResult
        from src.infrastructure.config.config_manager import ConfigManager
        
        allure_reporter = AllureReporter(results_dir="allure-results")
        html_reporter = HTMLReporter()
        
        result = TestResult(
            test_name="test_allure_html_integration",
            status=TestStatus.PASSED,
            execution_time=2.0,
            metadata={"reporters": ["allure", "html"]}
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Generate both reports
            allure_reporter.report(result, output_dir=str(tmpdir_path))
            html_reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify that both report types were generated
            xml_files = list(tmpdir_path.glob("*.xml"))
            html_files = list(tmpdir_path.glob("*.html"))
            
            assert len(xml_files) > 0, "Allure XML files should be created"
            assert len(html_files) > 0, "HTML files should be created"
    
    def test_full_reporting_pipeline(self):
        """Test the complete reporting pipeline"""
        from src.core.entities.test_result import TestResult
        from src.infrastructure.config.config_manager import ConfigManager
        
        reporters = {
            "allure": AllureReporter(config),
            "html": HTMLReporter(config),
            "json": JSONReporter(config)
        }
        
        # Create multiple test results
        results = [
            TestResult(f"test_{i}", TestStatus.PASSED, 1.0, {"feature": f"feature_{i}"})
            for i in range(5)
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Generate reports with all reporters
            for name, reporter in reporters.items():
                for i, result in enumerate(results):
                    reporter.report(result, output_dir=str(tmpdir_path / name))
            
            # Verify files were created
            all_files = list(tmpdir_path.glob("**/*"))
            assert len(all_files) > 0, "Some report files should be created"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
