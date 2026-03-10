#!/bin/bash
# QA-FRAMEWORK - Automated Deployment Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 QA-FRAMEWORK Deployment Script${NC}"
echo "Started: $(date)"
echo ""

# Configuration
FRONTEND_DIR="dashboard/frontend"
BACKEND_DIR="dashboard/backend"
RAILWAY_TOKEN="${RAILWAY_TOKEN:-}"
VERCEL_TOKEN="${VERCEL_TOKEN:-}"

# Functions
log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."

    command -v node >/dev/null 2>&1 || { log_error "Node.js not found"; exit 1; }
    command -v python3 >/dev/null 2>&1 || { log_error "Python3 not found"; exit 1; }
    command -v pip >/dev/null 2>&1 || { log_error "pip not found"; exit 1; }

    log_success "All dependencies found"
}

# Run tests
run_tests() {
    log_info "Running backend tests..."
    cd $BACKEND_DIR
    pytest tests/ -v --tb=short || { log_error "Backend tests failed"; exit 1; }
    cd ../..

    log_info "Running frontend tests..."
    cd $FRONTEND_DIR
    npm test -- --watchAll=false || { log_error "Frontend tests failed"; exit 1; }
    cd ../..

    log_success "All tests passed"
}

# Build frontend
build_frontend() {
    log_info "Building frontend..."
    cd $FRONTEND_DIR
    npm run build || { log_error "Frontend build failed"; exit 1; }
    cd ../..
    log_success "Frontend built successfully"
}

# Deploy backend to Railway
deploy_backend() {
    if [ -z "$RAILWAY_TOKEN" ]; then
        log_error "RAILWAY_TOKEN not set"
        exit 1
    fi

    log_info "Deploying backend to Railway..."

    # Install Railway CLI if not present
    if ! command -v railway &> /dev/null; then
        log_info "Installing Railway CLI..."
        npm install -g @railway/cli
    fi

    # Login and deploy
    railway login --token $RAILWAY_TOKEN
    railway up || { log_error "Backend deployment failed"; exit 1; }

    log_success "Backend deployed to Railway"
}

# Deploy frontend to Vercel
deploy_frontend() {
    if [ -z "$VERCEL_TOKEN" ]; then
        log_error "VERCEL_TOKEN not set"
        exit 1
    fi

    log_info "Deploying frontend to Vercel..."

    # Install Vercel CLI if not present
    if ! command -v vercel &> /dev/null; then
        log_info "Installing Vercel CLI..."
        npm install -g vercel
    fi

    # Deploy
    cd $FRONTEND_DIR
    vercel --prod --token $VERCEL_TOKEN || { log_error "Frontend deployment failed"; exit 1; }
    cd ../..

    log_success "Frontend deployed to Vercel"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    cd $BACKEND_DIR

    # Install alembic if not present
    pip install alembic

    # Run migrations
    alembic upgrade head || { log_error "Migrations failed"; exit 1; }
    cd ../..

    log_success "Migrations completed"
}

# Health check
health_check() {
    log_info "Running health checks..."

    # Check backend
    BACKEND_URL="https://qa-framework-backend.railway.app"
    curl -f $BACKEND_URL/health || { log_error "Backend health check failed"; exit 1; }

    # Check frontend
    FRONTEND_URL="https://frontend-phi-three-52.vercel.app"
    curl -f $FRONTEND_URL || { log_error "Frontend health check failed"; exit 1; }

    log_success "All health checks passed"
}

# Main deployment flow
main() {
    check_dependencies
    run_tests
    build_frontend

    if [ "$SKIP_DEPLOY" != "true" ]; then
        deploy_backend
        deploy_frontend
        run_migrations
        health_check
    else
        log_info "Skipping deployment (SKIP_DEPLOY=true)"
    fi

    echo ""
    log_success "🎉 Deployment completed successfully!"
    echo "Backend: https://qa-framework-backend.railway.app"
    echo "Frontend: https://frontend-phi-three-52.vercel.app"
    echo "Finished: $(date)"
}

# Run main function
main
