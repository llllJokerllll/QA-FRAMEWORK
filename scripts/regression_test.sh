#!/bin/bash
# QA-FRAMEWORK Regression Testing Suite
# Comprehensive test execution for stability validation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REPORT_DIR="reports/regression"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${REPORT_DIR}/regression_${TIMESTAMP}"

# Create report directory
mkdir -p "${REPORT_DIR}"

echo -e "${BLUE}🧪 QA-FRAMEWORK Regression Testing Suite${NC}"
echo "Started: $(date)"
echo "Report: ${REPORT_FILE}"
echo ""

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Function to run test suite and track results
run_test_suite() {
    local suite_name=$1
    local test_path=$2
    local markers=$3
    
    echo -e "${YELLOW}Running: ${suite_name}${NC}"
    
    local cmd="pytest ${test_path} -v --tb=short --html=${REPORT_FILE}_${suite_name}.html --self-contained-html"
    
    if [ -n "$markers" ]; then
        cmd="pytest ${test_path} -v -m ${markers} --tb=short --html=${REPORT_FILE}_${suite_name}.html --self-contained-html"
    fi
    
    if $cmd; then
        echo -e "  ${GREEN}✓${NC} ${suite_name} passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗${NC} ${suite_name} failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
}

# 1. Unit Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}1️⃣ UNIT TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
run_test_suite "unit-core" "tests/unit/test_*.py" "unit"
run_test_suite "unit-domain" "tests/unit/domain/" "unit"
run_test_suite "unit-infrastructure" "tests/unit/infrastructure/" "unit"
run_test_suite "unit-auth" "tests/unit/auth/" "unit"

# 2. Integration Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}2️⃣ INTEGRATION TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
run_test_suite "integration" "tests/integration/" "integration"

# 3. Security Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}3️⃣ SECURITY TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
run_test_suite "security" "tests/security/" "security"

# 4. Performance Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}4️⃣ PERFORMANCE TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
run_test_suite "performance" "tests/performance/" "performance"

# 5. E2E Tests (if available)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}5️⃣ END-TO-END TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ -d "tests/e2e" ] && [ "$(ls -A tests/e2e/*.py 2>/dev/null)" ]; then
    run_test_suite "e2e" "tests/e2e/" "e2e"
else
    echo -e "${YELLOW}⚠${NC} No E2E tests found, skipping"
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
fi

# 6. Parallel Execution Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}6️⃣ PARALLEL EXECUTION TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Running tests with pytest-xdist (4 workers)${NC}"
pytest tests/ -v -n 4 --tb=short --html=${REPORT_FILE}_parallel.html --self-contained-html || true

# Generate summary report
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 REGRESSION TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Total Suites: ${TOTAL_TESTS}"
echo -e "  ${GREEN}Passed:${NC} ${PASSED_TESTS}"
echo -e "  ${RED}Failed:${NC} ${FAILED_TESTS}"
echo -e "  ${YELLOW}Skipped:${NC} ${SKIPPED_TESTS}"
echo ""

# Calculate pass rate
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "Pass Rate: ${PASS_RATE}%"
    
    if [ $PASS_RATE -ge 95 ]; then
        echo -e "${GREEN}✅ REGRESSION TESTS PASSED (≥95%)${NC}"
        echo "Status: READY FOR PRODUCTION"
        exit 0
    elif [ $PASS_RATE -ge 80 ]; then
        echo -e "${YELLOW}⚠️ REGRESSION TESTS PARTIAL (80-95%)${NC}"
        echo "Status: REVIEW FAILURES BEFORE DEPLOY"
        exit 1
    else
        echo -e "${RED}❌ REGRESSION TESTS FAILED (<80%)${NC}"
        echo "Status: NOT READY FOR PRODUCTION"
        exit 1
    fi
else
    echo -e "${RED}❌ NO TESTS EXECUTED${NC}"
    exit 1
fi
