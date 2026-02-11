#!/usr/bin/env python3
"""
Simple test script for Reporting System (without pytest dependency)
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.entities.test_result import TestResult, TestStatus
from infrastructure.config.config_manager import ConfigManager


def test_allure_reporter():
    """Test AllureReporter can be initialized"""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"Testing AllureReporter...")
    print(f"Config loaded: environment={config.test.environment}")
    print(f"Allure dir: {config.reporting.allure if hasattr(config.reporting, 'allure') else 'N/A'}")
    
    try:
        from adapters.reporting.allure_reporter import AllureReporter
        reporter = AllureReporter(config)
        
        assert reporter is not None
        print(f"✓ AllureReporter initialized")
        print(f"  Allure output directory: {reporter.allure_dir}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import AllureReporter: {e}")
        return False
    except Exception as e:
        print(f"✗ Error initializing AllureReporter: {e}")
        return False


def test_html_reporter():
    """Test HTMLReporter can be initialized"""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"Testing HTMLReporter...")
    print(f"HTML enabled: {config.reporting.html if hasattr(config.reporting, 'html') else 'N/A'}")
    
    try:
        from adapters.reporting.html_reporter import HTMLReporter
        reporter = HTMLReporter(config)
        
        assert reporter is not None
        print(f"✓ HTMLReporter initialized")
        print(f"  HTML output directory: {reporter.output_dir}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import HTMLReporter: {e}")
        return False
    except Exception as e:
        print(f"✗ Error initializing HTMLReporter: {e}")
        return False


def test_json_reporter():
    """Test JSONReporter can be initialized"""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"Testing JSONReporter...")
    print(f"JSON enabled: {config.reporting.json if hasattr(config.reporting, 'json') else 'N/A'}")
    
    try:
        from adapters.reporting.json_reporter import JSONReporter
        reporter = JSONReporter(config)
        
        assert reporter is not None
        print(f"✓ JSONReporter initialized")
        print(f"  JSON output directory: {reporter.output_dir}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import JSONReporter: {e}")
        return False
    except Exception as e:
        print(f"✗ Error initializing JSONReporter: {e}")
        return False


def test_report_generation():
    """Test that reporters can generate a report"""
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    print(f"\nTesting report generation...")
    
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
            execution_time=1.0,
            metadata={
                "feature": "reporting_system",
                "test_type": "unit"
            }
        )
        
        # Generate reports
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            print(f"  Generating Allure XML report...")
            allure_reporter.report(result, output_dir=str(tmpdir_path))
            
            print(f"  Generating HTML report...")
            html_reporter.report(result, output_dir=str(tmpdir_path))
            
            print(f"  Generating JSON report...")
            json_reporter.report(result, output_dir=str(tmpdir_path))
            
            # Verify files were created
            xml_files = list(tmpdir_path.glob("*.xml"))
            html_files = list(tmpdir_path.glob("*.html"))
            json_files = list(tmpdir_path.glob("*.json"))
            
            print(f"\n  Generated files:")
            print(f"    Allure XML: {len(xml_files)} files")
            print(f"    HTML: {len(html_files)} files")
            print(f"    JSON: {len(json_files)} files")
            
            assert len(xml_files) > 0, "At least one Allure XML file should be created"
            assert len(html_files) > 0, "At least one HTML file should be created"
            assert len(json_files) > 0, "At least one JSON file should be created"
        
        print(f"\n✓ Report generation successful")
        return True
        
    except Exception as e:
        print(f"\n✗ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test complete integration of all components"""
    print("=" * 60)
    print("REPORTING SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: ConfigManager
    print("\n[1/5] Testing Configuration Management...")
    config_manager = ConfigManager()
    config = config_manager.get_config()
    assert config is not None
    print("  ✓ Configuration loaded successfully")
    
    # Test 2: Allure Reporter
    print("\n[2/5] Testing Allure Reporter...")
    test_allure_result = test_allure_reporter()
    
    # Test 3: HTML Reporter
    print("\n[3/5] Testing HTML Reporter...")
    test_html_result = test_html_reporter()
    
    # Test 4: JSON Reporter
    print("\n[4/5] Testing JSON Reporter...")
    test_json_result = test_json_reporter()
    
    # Test 5: Report Generation
    print("\n[5/5] Testing Report Generation...")
    test_report_result = test_report_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Configuration Management", True),
        ("Allure Reporter", test_allure_result),
        ("HTML Reporter", test_html_result),
        ("JSON Reporter", test_json_result),
        ("Report Generation", test_report_result),
    ]
    
    for test_name, test_result in tests:
        status = "✓ PASSED" if test_result else "✗ FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(test[1] for test in tests)
    
    print(f"\nOverall Result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 Reporting system is fully functional and tested!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")
        return 1


if __name__ == "__main__":
    import os
    os.exit(test_integration())
