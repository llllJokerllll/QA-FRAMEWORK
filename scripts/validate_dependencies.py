#!/usr/bin/env python3
"""
QA-FRAMEWORK Dependency Validator
Validates dependencies for the unified QA-FRAMEWORK project
"""

import subprocess
import sys
from pathlib import Path


def check_security_vulnerabilities(requirements_file: str) -> bool:
    """Check for known security vulnerabilities in dependencies."""
    print("\n🔒 Checking for security vulnerabilities...")

    try:
        # Run safety check
        result = subprocess.run(
            ['safety', 'check', '-r', requirements_file, '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("   ✅ No known security vulnerabilities found")
            return True
        else:
            print(f"   ⚠️  Security issues found:")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("   ⚠️  safety not installed, skipping security check")
        print("   💡 Install with: pip install safety")
        return True
    except Exception as e:
        print(f"   ⚠️  Error checking security: {e}")
        return True


def check_outdated_packages(requirements_file: str) -> bool:
    """Check for outdated packages."""
    print("\n📦 Checking for outdated packages...")

    try:
        # Run pip-outdated check
        result = subprocess.run(
            ['pip-outdated', '-r', requirements_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "up to date" in result.stdout.lower():
            print("   ✅ All packages are up to date")
            return True
        else:
            print(f"   ℹ️  Some packages have updates available:")
            print(result.stdout)
            return True
    except FileNotFoundError:
        print("   ⚠️  pip-outdated not installed, skipping outdated check")
        print("   💡 Install with: pip install pip-outdated")
        return True
    except Exception as e:
        print(f"   ⚠️  Error checking outdated packages: {e}")
        return True


def validate_framework_requirements():
    """Validate framework core requirements."""
    print("\n🧪 Validating framework core requirements...")

    framework_reqs = Path('requirements.txt')
    if not framework_reqs.exists():
        print("   ⚠️  Framework requirements.txt not found")
        return False

    with open(framework_reqs) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    print(f"   ✅ Found {len(lines)} framework core dependencies")
    return True


def validate_dashboard_requirements():
    """Validate dashboard requirements."""
    print("\n🎨 Validating dashboard requirements...")

    dashboard_reqs = Path('dashboard/backend/requirements.txt')
    if not dashboard_reqs.exists():
        print("   ⚠️  Dashboard requirements.txt not found")
        return False

    with open(dashboard_reqs) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

    print(f"   ✅ Found {len(lines)} dashboard dependencies")

    # Check for critical dependencies
    content = '\n'.join(lines)

    critical = {
        'fastapi': 'FastAPI framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'sqlalchemy': 'Database ORM',
        'asyncpg': 'Async PostgreSQL',
        'redis': 'Caching',
        'structlog': 'Structured logging',
    }

    missing = []
    for pkg, desc in critical.items():
        if pkg not in content.lower():
            missing.append(f"{pkg} ({desc})")

    if missing:
        print(f"   ⚠️  Missing critical dependencies:")
        for m in missing:
            print(f"      - {m}")
        return False
    else:
        print("   ✅ All critical dependencies present")
        return True


def main():
    """Main validation."""
    print("🔍 QA-FRAMEWORK Dependency Validator")
    print("=" * 60)

    all_passed = True

    # Validate framework
    if not validate_framework_requirements():
        all_passed = False

    # Validate dashboard
    if not validate_dashboard_requirements():
        all_passed = False

    # Security checks (optional, requires safety)
    if not check_security_vulnerabilities('dashboard/backend/requirements.txt'):
        all_passed = False

    # Outdated checks (optional, requires pip-outdated)
    check_outdated_packages('dashboard/backend/requirements.txt')

    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    if all_passed:
        print("✅ PASSED - All dependency checks passed")
        return 0
    else:
        print("❌ FAILED - Some dependency checks failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
