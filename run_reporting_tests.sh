#!/usr/bin/env python3
"""
Test runner script for Reporting System tests
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([
        "tests/unit/test_reporting_unit.py",
        "tests/integration/test_reporting_integration.py",
        "-v",
        "--tb=short"
    ]))
