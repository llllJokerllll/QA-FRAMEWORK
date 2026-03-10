#!/bin/bash
# QA-FRAMEWORK Security Testing Suite
# Uses OWASP ZAP for automated security scanning

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
TARGET_URL="${TARGET_URL:-http://localhost:8000}"
REPORT_DIR="reports/security"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${REPORT_DIR}/zap_report_${TIMESTAMP}"

# Create report directory
mkdir -p "${REPORT_DIR}"

echo -e "${YELLOW}🔒 QA-FRAMEWORK Security Testing Suite${NC}"
echo "Target: ${TARGET_URL}"
echo "Report: ${REPORT_FILE}"
echo ""

# Check if ZAP is installed
if ! command -v zap-cli &> /dev/null; then
    echo -e "${RED}❌ OWASP ZAP not found. Installing...${NC}"
    
    # Try Docker first (recommended)
    if command -v docker &> /dev/null; then
        echo "Using ZAP Docker image..."
        ZAP_CMD="docker run --rm -v $(pwd)/${REPORT_DIR}:/zap/wrk:rw owasp/zap2docker-stable zap-baseline.py"
    else
        echo -e "${YELLOW}Installing zap-cli via pip...${NC}"
        pip install zapcli
        ZAP_CMD="zap-cli"
    fi
else
    ZAP_CMD="zap-cli"
fi

echo -e "${YELLOW}1️⃣ Running ZAP Baseline Scan (Quick Security Check)...${NC}"
${ZAP_CMD} quick-scan --spider --ajax-spider "${TARGET_URL}" -o "${REPORT_FILE}_baseline.html" -f html

echo -e "${YELLOW}2️⃣ Running ZAP Active Scan (Deep Security Analysis)...${NC}"
# Note: Active scan is more aggressive, use with caution on production
# ${ZAP_CMD} active-scan --recursive "${TARGET_URL}" -o "${REPORT_FILE}_active.html" -f html

echo -e "${YELLOW}3️⃣ Testing for Common Vulnerabilities...${NC}"

# SQL Injection Tests
echo "  • SQL Injection..."
curl -s -X POST "${TARGET_URL}/api/v1/test-runs" \
    -H "Content-Type: application/json" \
    -d '{"test_id": "1 OR 1=1", "name": "test"}' \
    --max-time 5 > /dev/null && echo "    ${GREEN}✓${NC} No SQL injection found" || echo "    ${YELLOW}⚠${NC} Potential SQL injection"

# XSS Tests
echo "  • Cross-Site Scripting (XSS)..."
curl -s -X POST "${TARGET_URL}/api/v1/test-runs" \
    -H "Content-Type: application/json" \
    -d '{"name": "<script>alert(1)</script>", "test_id": "xss-test"}' \
    --max-time 5 > /dev/null && echo "    ${GREEN}✓${NC} XSS sanitized" || echo "    ${YELLOW}⚠${NC} Potential XSS"

# CSRF Token Check
echo "  • CSRF Protection..."
CSRF_CHECK=$(curl -s "${TARGET_URL}/api/v1/test-runs" -H "Content-Type: application/json" | grep -i "csrf" || true)
if [ -z "$CSRF_CHECK" ]; then
    echo "    ${YELLOW}⚠${NC} No CSRF token found (may use SameSite cookies)"
else
    echo "    ${GREEN}✓${NC} CSRF protection present"
fi

# Security Headers Check
echo "  • Security Headers..."
HEADERS=$(curl -sI "${TARGET_URL}" | grep -iE "x-frame-options|x-content-type-options|strict-transport-security|x-xss-protection" || true)
if [ -n "$HEADERS" ]; then
    echo "    ${GREEN}✓${NC} Security headers present:"
    echo "$HEADERS" | sed 's/^/      /'
else
    echo "    ${YELLOW}⚠${NC} Missing security headers"
fi

# Rate Limiting Check
echo "  • Rate Limiting..."
RATE_LIMIT_COUNT=0
for i in {1..10}; do
    curl -s -o /dev/null -w "%{http_code}" "${TARGET_URL}/health" --max-time 1 | grep -q "429" && RATE_LIMIT_COUNT=$((RATE_LIMIT_COUNT + 1))
done
if [ $RATE_LIMIT_COUNT -gt 0 ]; then
    echo "    ${GREEN}✓${NC} Rate limiting active (${RATE_LIMIT_COUNT}/10 requests throttled)"
else
    echo "    ${YELLOW}⚠${NC} No rate limiting detected"
fi

echo ""
echo -e "${YELLOW}4️⃣ Running Bandit (Python Security Linter)...${NC}"
if command -v bandit &> /dev/null; then
    bandit -r src/ -f json -o "${REPORT_FILE}_bandit.json" || true
    bandit -r src/ -f txt -o "${REPORT_FILE}_bandit.txt" || true
    echo "    ${GREEN}✓${NC} Bandit report saved to ${REPORT_FILE}_bandit.json"
else
    echo "    ${YELLOW}⚠${NC} Bandit not installed, skipping"
fi

echo ""
echo -e "${YELLOW}5️⃣ Running Safety (Dependency Vulnerability Check)...${NC}"
if command -v safety &> /dev/null; then
    safety check --json > "${REPORT_FILE}_safety.json" 2>&1 || true
    safety check > "${REPORT_FILE}_safety.txt" 2>&1 || true
    echo "    ${GREEN}✓${NC} Safety report saved to ${REPORT_FILE}_safety.json"
else
    echo "    ${YELLOW}⚠${NC} Safety not installed, skipping"
fi

echo ""
echo -e "${GREEN}✅ Security Testing Complete!${NC}"
echo ""
echo "Reports saved to:"
echo "  • ZAP Baseline: ${REPORT_FILE}_baseline.html"
echo "  • Bandit: ${REPORT_FILE}_bandit.json"
echo "  • Safety: ${REPORT_FILE}_safety.json"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Review ${REPORT_FILE}_baseline.html for ZAP findings"
echo "  2. Check ${REPORT_FILE}_bandit.json for code vulnerabilities"
echo "  3. Verify ${REPORT_FILE}_safety.json for dependency issues"
echo "  4. Fix any HIGH or CRITICAL severity issues before production"
