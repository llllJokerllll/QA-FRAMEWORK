#!/bin/bash
# Security Testing Script
# Runs OWASP ZAP, Bandit, npm audit, and Snyk

set -e

echo "🔒 Starting Security Testing..."
echo ""

# 1. Python Security Linting (Bandit)
echo "📦 Running Bandit (Python security linter)..."
bandit -r dashboard/backend/ -f json -o security-reports/bandit-report.json || true
bandit -r dashboard/backend/ -f txt || true
echo "✅ Bandit complete"
echo ""

# 2. NPM Audit (Frontend dependencies)
echo "📦 Running npm audit..."
cd dashboard/frontend
npm audit --json > ../../security-reports/npm-audit.json || true
npm audit || true
cd ../..
echo "✅ npm audit complete"
echo ""

# 3. OWASP ZAP (Web application scanning)
echo "🌐 Running OWASP ZAP scan..."
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t https://qa-framework-backend.railway.app \
    -r security-reports/zap-report.html \
    || true
echo "✅ OWASP ZAP complete"
echo ""

# 4. Snyk (Dependency scanning)
echo "📦 Running Snyk scan..."
snyk test --json > security-reports/snyk-report.json || true
snyk test || true
echo "✅ Snyk complete"
echo ""

# 5. Custom Security Checks
echo "🔍 Running custom security checks..."

# Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
! grep -r "password\s*=\s*['\"]" dashboard/backend/ --include="*.py" || echo "❌ Found hardcoded passwords"
! grep -r "api_key\s*=\s*['\"]" dashboard/backend/ --include="*.py" || echo "❌ Found hardcoded API keys"
! grep -r "secret\s*=\s*['\"]" dashboard/backend/ --include="*.py" || echo "❌ Found hardcoded secrets"
echo "✅ Secret check complete"

# Check for SQL injection vulnerabilities
echo "Checking for SQL injection vulnerabilities..."
! grep -r "execute.*%s" dashboard/backend/ --include="*.py" || echo "⚠️ Potential SQL injection found"
! grep -r "f\".*SELECT" dashboard/backend/ --include="*.py" || echo "⚠️ Potential SQL injection found"
echo "✅ SQL injection check complete"

# Check for XSS vulnerabilities
echo "Checking for XSS vulnerabilities..."
! grep -r "innerHTML" dashboard/frontend/src/ --include="*.tsx" || echo "⚠️ Potential XSS found"
! grep -r "dangerouslySetInnerHTML" dashboard/frontend/src/ --include="*.tsx" || echo "⚠️ Potential XSS found"
echo "✅ XSS check complete"

echo ""
echo "📊 Security Testing Complete!"
echo "Reports saved to: security-reports/"
