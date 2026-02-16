#!/bin/bash
# Performance Test Runner for QA-FRAMEWORK Dashboard
# Usage: ./run_tests.sh [load|stress|spike|soak|all]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
HOST="${PERF_TEST_BASE_URL:-http://localhost:8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p "$RESULTS_DIR"

print_header() {
    echo ""
    echo "============================================================"
    echo "  QA-FRAMEWORK Performance Tests"
    echo "  Target: $HOST"
    echo "============================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_api() {
    echo "Checking API availability..."
    if curl -s "$HOST/health" > /dev/null; then
        print_success "API is running at $HOST"
    else
        print_error "API is not available at $HOST"
        echo "Please start the API server first:"
        echo "  cd backend && uvicorn main:app --host 0.0.0.0 --port 8000"
        exit 1
    fi
}

run_load_test() {
    echo ""
    echo "Running Load Test (100 users, 5 minutes)..."
    echo "------------------------------------------------------------"
    
    locust -f "$SCRIPT_DIR/locustfile.py" \
        --host="$HOST" \
        --users 100 \
        --spawn-rate 5 \
        --run-time 5m \
        --headless \
        --html="$RESULTS_DIR/load_test_report.html" \
        --csv="$RESULTS_DIR/load_test"
    
    print_success "Load test completed"
}

run_stress_test() {
    echo ""
    echo "Running Stress Test (200 users, 15 minutes)..."
    echo "------------------------------------------------------------"
    
    locust -f "$SCRIPT_DIR/locustfile.py" \
        --host="$HOST" \
        --users 200 \
        --spawn-rate 10 \
        --run-time 15m \
        --headless \
        --html="$RESULTS_DIR/stress_test_report.html" \
        --csv="$RESULTS_DIR/stress_test" \
        --class-picker StressTestUser
    
    print_success "Stress test completed"
}

run_spike_test() {
    echo ""
    echo "Running Spike Test (200 users burst, 3 minutes)..."
    echo "------------------------------------------------------------"
    
    locust -f "$SCRIPT_DIR/locustfile.py" \
        --host="$HOST" \
        --users 200 \
        --spawn-rate 50 \
        --run-time 3m \
        --headless \
        --html="$RESULTS_DIR/spike_test_report.html" \
        --csv="$RESULTS_DIR/spike_test" \
        --class-picker SpikeTestUser
    
    print_success "Spike test completed"
}

run_soak_test() {
    echo ""
    echo "Running Soak Test (50 users, 60 minutes)..."
    echo "------------------------------------------------------------"
    
    locust -f "$SCRIPT_DIR/locustfile.py" \
        --host="$HOST" \
        --users 50 \
        --spawn-rate 2 \
        --run-time 60m \
        --headless \
        --html="$RESULTS_DIR/soak_test_report.html" \
        --csv="$RESULTS_DIR/soak_test"
    
    print_success "Soak test completed"
}

generate_benchmarks() {
    echo ""
    echo "Generating performance benchmarks..."
    echo "------------------------------------------------------------"
    
    cd "$SCRIPT_DIR"
    python3 generate_benchmarks.py
    
    print_success "Benchmarks generated"
}

show_results() {
    echo ""
    echo "============================================================"
    echo "  Test Results Summary"
    echo "============================================================"
    echo ""
    
    if [ -f "$RESULTS_DIR/benchmarks.md" ]; then
        cat "$RESULTS_DIR/benchmarks.md"
    fi
    
    echo ""
    echo "Result files:"
    ls -lh "$RESULTS_DIR/"
    
    echo ""
    echo "To view HTML reports, open:"
    for report in "$RESULTS_DIR"/*_report.html; do
        if [ -f "$report" ]; then
            echo "  file://$report"
        fi
    done
}

run_all_tests() {
    print_header
    check_api
    
    run_load_test
    run_stress_test
    run_spike_test
    
    generate_benchmarks
    show_results
}

show_help() {
    echo "QA-FRAMEWORK Performance Test Runner"
    echo ""
    echo "Usage: ./run_tests.sh [command]"
    echo ""
    echo "Commands:"
    echo "  load     - Run load test (100 users, 5 min)"
    echo "  stress   - Run stress test (200 users, 15 min)"
    echo "  spike    - Run spike test (200 users burst, 3 min)"
    echo "  soak     - Run soak test (50 users, 60 min)"
    echo "  all      - Run all tests (load, stress, spike)"
    echo "  results  - Show test results and benchmarks"
    echo "  help     - Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  PERF_TEST_BASE_URL - Target API URL (default: http://localhost:8000)"
    echo "  PERF_TEST_USERNAME - Test username (default: testuser)"
    echo "  PERF_TEST_PASSWORD - Test password (default: testpass123)"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh load      # Run load test only"
    echo "  ./run_tests.sh all       # Run all tests"
    echo "  ./run_tests.sh results   # View results"
}

# Main script
case "${1:-help}" in
    load)
        print_header
        check_api
        run_load_test
        generate_benchmarks
        show_results
        ;;
    stress)
        print_header
        check_api
        run_stress_test
        generate_benchmarks
        show_results
        ;;
    spike)
        print_header
        check_api
        run_spike_test
        generate_benchmarks
        show_results
        ;;
    soak)
        print_header
        check_api
        run_soak_test
        generate_benchmarks
        show_results
        ;;
    all)
        run_all_tests
        ;;
    results)
        show_results
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
