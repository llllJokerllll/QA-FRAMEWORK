#!/usr/bin/env python3
"""
Performance Test Setup Validator

Validates that all performance testing components are properly configured.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False


def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {dirpath}")
        return False


def validate_locustfile(filepath):
    """Validate locustfile syntax"""
    try:
        with open(filepath, "r") as f:
            code = f.read()
        compile(code, filepath, "exec")
        print(f"✅ Locustfile syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Locustfile has syntax error: {e}")
        return False


def check_python_imports():
    """Check if required Python packages are installed"""
    imports_ok = True

    try:
        import locust

        print(f"✅ Locust installed (version: {locust.__version__})")
    except ImportError:
        print(f"❌ Locust not installed. Run: pip install locust==2.20.0")
        imports_ok = False

    try:
        import config

        print(f"✅ Performance config module accessible")
    except ImportError as e:
        print(f"⚠️  Config module import warning: {e}")

    return imports_ok


def main():
    """Main validation function"""
    script_dir = Path(__file__).parent
    perf_dir = script_dir / "tests" / "performance"

    print("=" * 70)
    print("QA-FRAMEWORK Performance Test Setup Validator")
    print("=" * 70)
    print()

    all_checks_passed = True

    # Check directories
    print("📁 Checking Directories:")
    print("-" * 70)
    all_checks_passed &= check_directory_exists(
        str(perf_dir), "Performance tests directory"
    )
    all_checks_passed &= check_directory_exists(
        str(perf_dir / "results"), "Results directory"
    )
    print()

    # Check configuration files
    print("⚙️  Checking Configuration Files:")
    print("-" * 70)
    all_checks_passed &= check_file_exists(
        str(perf_dir / "config.py"), "Performance config"
    )
    all_checks_passed &= check_file_exists(
        str(perf_dir / "locustfile.py"), "Locust test file"
    )
    all_checks_passed &= check_file_exists(
        str(perf_dir / "run_tests.sh"), "Test runner script"
    )
    all_checks_passed &= check_file_exists(
        str(perf_dir / "generate_benchmarks.py"), "Benchmark generator"
    )
    all_checks_passed &= check_file_exists(
        str(perf_dir / "README.md"), "Performance README"
    )
    print()

    # Check documentation
    print("📚 Checking Documentation:")
    print("-" * 70)
    all_checks_passed &= check_file_exists(
        str(perf_dir / "RESULTS.md"), "Results documentation"
    )
    print()

    # Validate locustfile
    print("🔍 Validating Locustfile:")
    print("-" * 70)
    all_checks_passed &= validate_locustfile(str(perf_dir / "locustfile.py"))
    print()

    # Check Python imports
    print("🐍 Checking Python Dependencies:")
    print("-" * 70)
    os.chdir(str(perf_dir))
    all_checks_passed &= check_python_imports()
    print()

    # Check results files
    print("📊 Checking Generated Files:")
    print("-" * 70)
    results_dir = perf_dir / "results"
    if results_dir.exists():
        check_file_exists(str(results_dir / "benchmarks.json"), "Benchmarks JSON")
        check_file_exists(str(results_dir / "benchmarks.md"), "Benchmarks Markdown")
    print()

    # Summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Performance tests are properly configured!")
        print()
        print("To run tests:")
        print("  cd tests/performance")
        print("  ./run_tests.sh load")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running tests.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
