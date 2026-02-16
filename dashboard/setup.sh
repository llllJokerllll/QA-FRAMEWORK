#!/bin/bash

# Setup Script for QA-FRAMEWORK Dashboard
# This script installs all necessary dependencies for development and testing

set -e  # Exit on error

echo "🚀 Setting up QA-FRAMEWORK Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[ℹ]${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_status "Python version: $PYTHON_VERSION"

# Install backend dependencies
print_info "Installing backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel
print_status "Pip upgraded"

# Install requirements
print_info "Installing Python packages..."
pip install -r requirements.txt
print_status "Backend dependencies installed"

# Install dev dependencies
print_info "Installing development dependencies..."
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
print_status "Development dependencies installed"

# Run tests
print_info "Running backend tests..."
pytest tests/unit/ -v --tb=short || print_error "Some tests failed"
print_status "Backend tests completed"

# Deactivate virtual environment
deactivate

# Install frontend dependencies
print_info "Installing frontend dependencies..."
cd ../frontend

# Check Node.js version
print_info "Checking Node.js version..."
NODE_VERSION=$(node --version 2>&1)
print_status "Node.js version: $NODE_VERSION"

# Install npm packages
print_info "Installing npm packages..."
npm install
print_status "Frontend dependencies installed"

# Run frontend linting
print_info "Running frontend linting..."
npm run lint || print_info "Linting completed with warnings"

# Build frontend
print_info "Building frontend..."
npm run build
print_status "Frontend build completed"

cd ..

print_status "✅ Setup completed successfully!"
print_info "Next steps:"
echo "  1. Activate backend venv: cd backend && source venv/bin/activate"
echo "  2. Run backend: uvicorn main:app --reload"
echo "  3. Run frontend: cd frontend && npm run dev"
echo "  4. Run tests: cd backend && pytest tests/"
echo ""
echo "📚 Documentation: See README.md and CHANGELOG.md"