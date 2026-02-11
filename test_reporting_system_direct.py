#!/usr/bin/env python3
"""
Test runner script for Reporting System (without pytest dependency)
"""

import sys
from pathlib import Path

# Add src to path correctly
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

print(f"Project root: {project_root}")
print(f"Python path[0]: {sys.path[0]}")

from core.entities.test_result import TestResult, TestStatus
from infrastructure.config.config_manager import ConfigManager


def test_allure_reporter():
    """Test that AllureReporter can be initialized"""
    print("\n[1/5] Testing AllureReporter initialization...")
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"   Config loaded: environment={config.test.environment}")
    print(f"   Allure enabled: {config.reporting.allure}")
    
    try:
        from adapters.reporting.allure_reporter import AllureReporter
        print("   ✓ AllureReporter imported successfully")
        
        reporter = AllureReporter(config)
        print(f"   ✓ AllureReporter initialized")
        print(f"   ✓ Allure output dir: {reporter.allure_dir}")
        
        return True
    except ImportError as e:
        print(f"   ✗ Failed to import AllureReporter: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_html_reporter():
    """Test that HTMLReporter can be initialized"""
    print("\n[2/5] Testing HTMLReporter initialization...")
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"   Config loaded: environment={config.test.environment}")
    print(f"   HTML enabled: {config.reporting.html}")
    
    try:
        from adapters.reporting.html_reporter import HTMLReporter
        print("   ✓ HTMLReporter imported successfully")
        
        reporter = HTMLReporter(config)
        print(f"   ✓ HTMLReporter initialized")
        print(f"   ✓ HTML output dir: {reporter.output_dir}")
        
        return True
    except ImportError as e:
        print(f"   ✗ Failed to import HTMLReporter: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_json_reporter():
    """Test that JSONReporter can be initialized"""
    print("\n[3/5] Testing JSONReporter initialization...")
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"   Config loaded: environment={config.test.environment}")
    print(f"   JSON enabled: {config.reporting.json}")
    
    try:
        from adapters.reporting.json_reporter import JSONReporter
        print("   ✓ JSONReporter imported successfully")
        
        reporter = JSONReporter(config)
        print(f"   ✓ JSONReporter initialized")
        print(f"   ✓ JSON output dir: {reporter.output_dir}")
        
        return True
    except ImportError as e:
        print(f"   ✗ Failed to import JSONReporter: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_report_generation():
    """Test that reports can be generated"""
    print("\n[4/5] Testing report generation...")
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    try:
        from adapters.reporting.allure_reporter import AllureReporter
        from adapters.reporting.html_reporter import HTMLReporter
        from adapters.reporting.json_reporter import JSONReporter
        
        # Initialize reporters
        allure_reporter = AllureReporter(config)
        html_reporter = HTMLReporter(config)
        json_reporter = JSONReporter(config)
        
        # Create test result
        result = TestResult(
            test_name="test_reporting_system",
            status=TestStatus.PASSED,
            execution_time=1.5,
            metadata={
                "feature": "reporting_system",
                "test_type": "unit"
            }
        )
        
        print("   ✓ All reporters initialized")
        print(f"   ✓ Test result created: {result.test_name}")
        
        # Generate reports in temp directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            print(f"   Using temp directory: {tmpdir_path}")
            
            # Generate Allure report
            print("   → Generating Allure report...")
            allure_reporter.report(result, output_dir=str(tmpdir_path / "allure"))
            
            # Generate HTML report
            print("   → Generating HTML report...")
            html_reporter.report(result, output_dir=str(tmpdir_path / "html"))
            
            # Generate JSON report
            print("   → Generating JSON report...")
            json_reporter.report(result, output_dir=str(tmpdir_path / "json"))
            
            # Verify files were created
            print("\n[5/5] Verifying generated reports...")
            xml_files = list(tmpdir_path.glob("allure/**/*.xml"))
            html_files = list(tmpdir_path.glob("html/**/*.html"))
            json_files = list(tmpdir_path.glob("json/**/*.json"))
            
            print(f"   ✓ Allure XML files: {len(xml_files)}")
            print(f"   ✓ HTML files: {len(html_files)}")
            print(f"   ✓ JSON files: {len(json_files)}")
            
            assert len(xml_files) > 0, "Allure XML files should be created"
            assert len(html_files) > 0, "HTML files should be created"
            assert len(json_files) > 0, "JSON files should be created"
        
        print("\n   ✓ Report generation test passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Report generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test complete integration of all components"""
    print("\n[6/5] Testing complete integration...")
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    try:
        from adapters.reporting.allure_reporter import AllureReporter
        from adapters.reporting.html_reporter import HTMLReporter
        from adapters.reporting.json_reporter import JSONReporter
        
        # Initialize all reporters
        reporters = {
            "allure": AllureReporter(config),
            "html": HTMLReporter(config),
            "json": JSONReporter(config)
        }
        
        print("   ✓ All reporters initialized")
        
        # Create test results
        results = [
            TestResult(f"integration_test_{i}", TestStatus.PASSED, 1.0, {"reporter": name})
            for i, name in enumerate(reporters.keys())
        ]
        
        # Generate reports with all reporters
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            print(f"   Using temp directory: {tmpdir_path}")
            
            print("   → Generating reports with all reporters...")
            for name, reporter in reporters.items():
                for i, result in enumerate(results):
                    reporter.report(result, output_dir=str(tmpdir_path / name))
                    print(f"      → {name} report generated for test {i+1}")
            
            # Verify files were created
            print("\n   Verifying generated reports...")
            all_files = list(tmpdir_path.glob("**/*"))
            print(f"   ✓ Total files generated: {len(all_files)}")
            
            assert len(all_files) > 0, "Report files should be created"
        
        print("\n   ✓ Integration test passed")
        return True
        
    except Exception as e:
        print(f"   ✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("=" * 80)
    print("Reporting System - Test Suite")
    print("=" * 80)
    print(f"Python path: {sys.path[0]}")
    
    # Run tests
    tests = [
        ("AllureReporter Initialization", test_allure_reporter),
        ("HTMLReporter Initialization", test_html_reporter),
        ("JSONReporter Initialization", test_json_reporter),
        ("Report Generation", test_report_generation),
        ("Full Integration", test_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Running: {test_name}")
        print(f"{'=' * 60}")
        
        result = test_func()
        results.append((test_name, result))
        
        print(f"\n{test_name}: {'✓ PASSED' if result else '✗ FAILED'}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Reporting system is fully functional.")
        print("=" * 80)
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    import os
    os.exit(main())
