"""
Integration tests for Reporting System
Tests the complete reporting pipeline with real test data
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from src.adapters.http.httpx_client import HTTPXClient
from src.core.entities.test_result import TestResult, TestStatus
from src.adapters.reporting.allure_reporter import AllureReporter
from src.adapters.reporting.html_reporter import HTMLReporter
from src.adapters.reporting.json_reporter import JSONReporter


class TestReportingAPICalls:
    """Integration tests for reporting with actual HTTP calls"""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_allure_xml_generation_with_real_data(self):
        """Test Allure XML generation with real HTTP response"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        response = await client.get("/users")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        # Create test result with real API data
        result = TestResult(
            test_name="test_allure_xml_generation_with_real_data",
            status=TestStatus.PASSED,
            execution_time=2.0,
            metadata={
                "api_endpoint": "/users",
                "response_size": len(data),
                "data_sample": data[:2] if len(data) >= 2 else []
            }
        )
        
        # Test that AllureReporter handles real data
        from src.infrastructure.config.config_manager import ConfigManager
        config = ConfigManager()
        reporter = AllureReporter(config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify XML was created
            xml_files = list(tmpdir_path.glob("*.xml"))
            assert len(xml_files) > 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_html_report_generation_with_real_data(self):
        """Test HTML report generation with real API data"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        response = await client.get("/posts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        # Create test result with real API data
        result = TestResult(
            test_name="test_html_report_generation_with_real_data",
            status=TestStatus.PASSED,
            execution_time=2.5,
            metadata={
                "api_endpoint": "/posts",
                "response_size": len(data),
                "data_sample": data[:3] if len(data) >= 3 else []
            }
        )
        
        # Test that HTMLReporter handles real data
        from src.infrastructure.config.config_manager import ConfigManager
        config = ConfigManager()
        reporter = HTMLReporter(config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify HTML was created
            html_files = list(tmpdir_path.glob("*.html"))
            assert len(html_files) > 0
    
    @pytest.mark.api
    @pytest.mark.asyncio
    async def test_json_report_generation_with_real_data(self):
        """Test JSON report generation with real API data"""
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        response = await client.get("/todos")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        # Create test result with real API data
        result = TestResult(
            test_name="test_json_report_generation_with_real_data",
            status=TestStatus.PASSED,
            execution_time=3.0,
            metadata={
                "api_endpoint": "/todos",
                "response_size": len(data),
                "data_sample": data[:2] if len(data) >= 2 else []
            }
        )
        
        # Test that JSONReporter handles real data
        from src.infrastructure.config.config_manager import ConfigManager
        config = ConfigManager()
        reporter = JSONReporter(config)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify JSON was created
            json_files = list(tmpdir_path.glob("*.json"))
            assert len(json_files) > 0


class TestReportingSystemFullPipeline:
    """Integration tests for the complete reporting system"""
    
    @pytest.mark.api
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_reporting_pipeline(self):
        """Test the complete reporting pipeline from API to reports"""
        from src.infrastructure.config.config_manager import ConfigManager
        config = ConfigManager()
        
        # Step 1: Fetch real data from API
        client = HTTPXClient(base_url="https://jsonplaceholder.typicode.com")
        user_response = await client.get("/users/1")
        post_response = await client.get("/posts/1")
        
        # Step 2: Create test results
        user_result = TestResult(
            test_name="fetch_user_1",
            status=TestStatus.PASSED if user_response.status_code == 200 else TestStatus.FAILED,
            execution_time=1.5,
            metadata={"endpoint": "/users/1", "data": user_response.json()}
        )
        
        post_result = TestResult(
            test_name="fetch_post_1",
            status=TestStatus.PASSED if post_response.status_code == 200 else TestStatus.FAILED,
            execution_time=1.5,
            metadata={"endpoint": "/posts/1", "data": post_response.json()}
        )
        
        # Step 3: Generate reports with all reporters
        reporters = {
            "allure": AllureReporter(config),
            "html": HTMLReporter(config),
            "json": JSONReporter(config)
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Generate reports
            for result in [user_result, post_result]:
                for name, reporter in reporters.items():
                    reporter.report(result, output_dir=str(tmpdir_path / name))
            
            # Step 4: Verify all report files
            all_files = list(tmpdir_path.glob("**/*"))
            assert len(all_files) > 0, "Report files should be created"
            
            # Step 5: Verify specific file types
            xml_files = list(tmpdir_path.glob("*.xml"))
            html_files = list(tmpdir_path.glob("*.html"))
            json_files = list(tmpdir_path.glob("*.json"))
            
            assert len(xml_files) > 0, "Allure XML files should be created"
            assert len(html_files) > 0, "HTML files should be created"
            assert len(json_files) > 0, "JSON files should be created"
    
    @pytest.mark.api
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_reporting_error_handling(self):
        """Test that reporting system handles errors correctly"""
        from src.infrastructure.config.config.config_manager import ConfigManager
        config = ConfigManager()
        reporter = HTMLReporter(config)
        
        # Create failed test result
        result = TestResult(
            test_name="test_error_handling",
            status=TestStatus.FAILED,
            execution_time=0.5,
            error_message="Simulated test failure",
            metadata={"simulated_error": True}
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Even failed tests should generate reports
            reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify report was created (even for failed tests)
            html_files = list(tmpdir_path.glob("*.html"))
            assert len(html_files) > 0, "Report should be generated even for failed test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
