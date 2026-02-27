#!/bin/bash
# Health Monitor Script for QA-FRAMEWORK
# Monitors system health and sends alerts if issues detected

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8001}"
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"  # Slack/Discord webhook
LOG_FILE="logs/health_monitor.log"

# Logging
log() {
    timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Check backend health
check_backend() {
    log "Checking backend health..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health" || echo "000")
    
    if [ "$response" = "200" ]; then
        log "✅ Backend is healthy (HTTP $response)"
        return 0
    else
        log "❌ Backend is unhealthy (HTTP $response)"
        send_alert "Backend unhealthy - HTTP $response"
        return 1
    fi
}

# Check database connectivity
check_database() {
    log "Checking database connectivity..."
    
    if python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
import sys

async def test():
    try:
        engine = create_async_engine(os.getenv('DATABASE_URL'))
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        sys.exit(0)
    except Exception as e:
        print(f'Database error: {e}', file=sys.stderr)
        sys.exit(1)

asyncio.run(test())
" 2>&1; then
        log "✅ Database connection successful"
        return 0
    else
        log "❌ Database connection failed"
        send_alert "Database connection failed"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    log "Checking Redis connectivity..."
    
    if redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" ping 2>&1 | grep -q "PONG"; then
        log "✅ Redis is healthy"
        return 0
    else
        log "⚠️  Redis is unavailable (caching disabled)"
        return 0  # Non-critical
    fi
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."
    
    threshold=90
    usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt "$threshold" ]; then
        log "❌ Disk usage is ${usage}% (threshold: ${threshold}%)"
        send_alert "Disk usage critical: ${usage}%"
        return 1
    else
        log "✅ Disk usage is ${usage}%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    log "Checking memory usage..."
    
    threshold=90
    usage=$(free | awk '/Mem:/ {printf "%.0f", ($3/$2) * 100}')
    
    if [ "$usage" -gt "$threshold" ]; then
        log "⚠️  Memory usage is ${usage}% (threshold: ${threshold}%)"
        send_alert "Memory usage high: ${usage}%"
        return 1
    else
        log "✅ Memory usage is ${usage}%"
        return 0
    fi
}

# Check API response time
check_response_time() {
    log "Checking API response time..."
    
    threshold=2.0  # seconds
    response_time=$(curl -s -o /dev/null -w "%{time_total}" "$API_URL/health")
    
    if (( $(echo "$response_time > $threshold" | bc -l) )); then
        log "⚠️  API response time is ${response_time}s (threshold: ${threshold}s)"
        send_alert "API response time high: ${response_time}s"
        return 1
    else
        log "✅ API response time is ${response_time}s"
        return 0
    fi
}

# Send alert (Slack/Discord webhook)
send_alert() {
    local message="$1"
    
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -s -X POST "$ALERT_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"🚨 QA-FRAMEWORK Alert: $message\"}" > /dev/null
    fi
}

# Generate health report
generate_report() {
    log "Generating health report..."
    
    report_file="logs/health_report_$(date +'%Y%m%d_%H%M%S').txt"
    
    {
        echo "QA-FRAMEWORK Health Report"
        echo "Generated: $(date)"
        echo "======================================"
        echo ""
        echo "Backend Status:"
        curl -s "$API_URL/health" | python3 -m json.tool 2>/dev/null || echo "Unavailable"
        echo ""
        echo "Database Status:"
        python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

async def test():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT version()'))
        print(result.scalar())

asyncio.run(test())
" 2>/dev/null || echo "Unavailable"
        echo ""
        echo "Redis Status:"
        redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" info server 2>/dev/null | grep "redis_version" || echo "Unavailable"
        echo ""
        echo "System Resources:"
        echo "  Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
        echo "  Memory Usage: $(free | awk '/Mem:/ {printf "%.1f%%", ($3/$2) * 100}')"
        echo "  CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
        echo ""
        echo "Recent Logs (last 20 lines):"
        tail -20 logs/backend.log 2>/dev/null || echo "No logs available"
    } > "$report_file"
    
    log "Health report saved to: $report_file"
}

# Main health check
main() {
    log "Starting health check..."
    
    mkdir -p logs
    
    errors=0
    
    check_backend || ((errors++))
    check_database || ((errors++))
    check_redis || true  # Non-critical
    check_disk_space || ((errors++))
    check_memory || true  # Warning only
    check_response_time || true  # Warning only
    
    if [ $errors -eq 0 ]; then
        log "✅ All critical health checks passed"
        exit 0
    else
        log "❌ $errors critical health check(s) failed"
        exit 1
    fi
}

# Run
main "$@"
