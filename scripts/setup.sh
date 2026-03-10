#!/bin/bash
# QA-FRAMEWORK - Development Setup Script

set -e

echo "🛠️ QA-FRAMEWORK Development Setup"
echo "Started: $(date)"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check Python version
check_python() {
    log_info "Checking Python version..."
    python3 --version
    pip3 --version
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."

    cd dashboard/backend

    # Create virtual environment
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt

    # Copy environment file
    if [ ! -f ".env" ]; then
        log_info "Creating .env file..."
        cp .env.example .env
        echo ""
        echo -e "${YELLOW}⚠️  Please edit dashboard/backend/.env with your configuration${NC}"
    fi

    # Run migrations
    log_info "Running database migrations..."
    alembic upgrade head

    cd ../..
    log_success "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend..."

    cd dashboard/frontend

    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    else
        log_info "Node modules already installed, skipping..."
    fi

    # Copy environment file
    if [ ! -f ".env.local" ]; then
        log_info "Creating .env.local file..."
        cp .env.example .env.local
        echo ""
        echo -e "${YELLOW}⚠️  Please edit dashboard/frontend/.env.local with your configuration${NC}"
    fi

    cd ../..
    log_success "Frontend setup complete"
}

# Install global dependencies
install_global_deps() {
    log_info "Installing global dependencies..."

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${YELLOW}Node.js not found. Please install Node.js 18+ first.${NC}"
        exit 1
    fi

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Python3 not found. Please install Python 3.11+ first.${NC}"
        exit 1
    fi

    log_success "Global dependencies ready"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."

    mkdir -p reports/{load,security,regression,e2e-screenshots}
    mkdir -p logs
    mkdir -p dashboard/backend/alembic/versions

    log_success "Directories created"
}

# Main setup flow
main() {
    check_python
    install_global_deps
    create_directories
    setup_backend
    setup_frontend

    echo ""
    log_success "🎉 Development setup completed!"
    echo ""
    echo "Next steps:"
    echo "  1. Edit dashboard/backend/.env with your configuration"
    echo "  2. Edit dashboard/frontend/.env.local with your configuration"
    echo "  3. Start backend: cd dashboard/backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "  4. Start frontend: cd dashboard/frontend && npm run dev"
    echo "  5. Open http://localhost:5173"
    echo ""
    echo "For testing:"
    echo "  - Backend tests: cd dashboard/backend && pytest"
    echo "  - Frontend tests: cd dashboard/frontend && npm test"
    echo "  - Load tests: locust -f tests/load/locustfile.py"
    echo ""
    echo "For deployment:"
    echo "  - ./scripts/deploy.sh"
    echo ""
}

main
