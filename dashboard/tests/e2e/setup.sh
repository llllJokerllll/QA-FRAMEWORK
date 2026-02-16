#!/bin/bash
# Setup script for E2E tests - QA-FRAMEWORK Dashboard

set -e

echo "🚀 Setting up environment for E2E tests..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
check_service() {
    local service=$1
    local port=$2
    
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service is running on port $port"
        return 0
    else
        echo -e "${RED}✗${NC} $service is NOT running on port $port"
        return 1
    fi
}

# Check dependencies
echo ""
echo "📋 Checking dependencies..."

# PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL client installed"
else
    echo -e "${YELLOW}!${NC} PostgreSQL client not found"
fi

# Redis
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✓${NC} Redis client installed"
else
    echo -e "${YELLOW}!${NC} Redis client not found"
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION installed"
else
    echo -e "${RED}✗${NC} Node.js not found - REQUIRED"
    exit 1
fi

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION installed"
else
    echo -e "${RED}✗${NC} Python3 not found - REQUIRED"
    exit 1
fi

# Playwright
if python3 -c "import playwright" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Playwright installed"
else
    echo -e "${YELLOW}!${NC} Playwright not installed - installing..."
    cd backend && source venv/bin/activate
    pip install pytest-playwright playwright
    playwright install chromium
fi

echo ""
echo "🔧 Services status:"

# Check services
BACKEND_UP=false
FRONTEND_UP=false

if check_service "Backend" 8000; then
    BACKEND_UP=true
fi

if check_service "Frontend" 3000; then
    FRONTEND_UP=true
fi

# Start services if not running
if [ "$BACKEND_UP" = false ] || [ "$FRONTEND_UP" = false ]; then
    echo ""
    echo "📌 Starting services..."
    
    # Start PostgreSQL if available
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql 2>/dev/null || echo "Could not start PostgreSQL"
        sudo systemctl start redis 2>/dev/null || echo "Could not start Redis"
    fi
    
    # Create .env if not exists
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cp .env.example .env
    fi
    
    # Start backend
    if [ "$BACKEND_UP" = false ]; then
        echo "Starting backend..."
        cd backend
        source venv/bin/activate
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd ..
        sleep 3
    fi
    
    # Start frontend
    if [ "$FRONTEND_UP" = false ]; then
        echo "Starting frontend..."
        cd frontend
        npm install --silent
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        sleep 5
    fi
fi

# Create test user
echo ""
echo "👤 Creating test user..."
curl -s -X POST http://localhost:8000/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpassword123","name":"Test User"}' || echo "User may already exist"

# Final check
echo ""
echo "📊 Final status:"
check_service "Backend" 8000
check_service "Frontend" 3000

echo ""
if check_service "Backend" 8000 && check_service "Frontend" 3000; then
    echo -e "${GREEN}✓ Environment ready for E2E tests!${NC}"
    echo ""
    echo "Run tests with:"
    echo "  cd backend && source venv/bin/activate"
    echo "  pytest ../tests/e2e/ -v -m e2e"
else
    echo -e "${RED}✗ Some services are not running${NC}"
    echo "Please start them manually or check the logs"
fi
