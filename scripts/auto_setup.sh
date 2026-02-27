#!/bin/bash
# Auto-Setup Script for QA-FRAMEWORK
# This script automates the setup process after PostgreSQL, Redis, and Stripe are configured

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if required environment variables are set
check_env_vars() {
    log "Checking environment variables..."
    
    local missing=()
    
    # Required variables
    if [ -z "$DATABASE_URL" ]; then
        missing+=("DATABASE_URL")
    fi
    
    if [ -z "$JWT_SECRET_KEY" ]; then
        missing+=("JWT_SECRET_KEY")
    fi
    
    if [ "$ENABLE_BILLING" = "true" ]; then
        if [ -z "$STRIPE_API_KEY" ]; then
            missing+=("STRIPE_API_KEY")
        fi
        if [ -z "$STRIPE_WEBHOOK_SECRET" ]; then
            missing+=("STRIPE_WEBHOOK_SECRET")
        fi
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing required environment variables:"
        for var in "${missing[@]}"; do
            echo "  - $var"
        done
        echo ""
        echo "Set them before running this script:"
        echo "  export DATABASE_URL='your_database_url'"
        echo "  export JWT_SECRET_KEY='your_secret_key'"
        exit 1
    fi
    
    success "All required environment variables are set"
}

# Test database connection
test_database() {
    log "Testing database connection..."
    
    cd dashboard/backend
    
    if python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

async def test():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('Database connection successful')

asyncio.run(test())
" 2>&1; then
        success "Database connection successful"
    else
        error "Database connection failed"
        exit 1
    fi
    
    cd ../..
}

# Test Redis connection
test_redis() {
    log "Testing Redis connection..."
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" ping | grep -q "PONG"; then
            success "Redis connection successful"
        else
            warning "Redis connection failed - caching will be disabled"
        fi
    else
        warning "redis-cli not found - skipping Redis test"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    cd dashboard/backend
    
    # Check if alembic is configured
    if [ -f "alembic.ini" ]; then
        if alembic upgrade head; then
            success "Database migrations completed"
        else
            error "Database migrations failed"
            exit 1
        fi
    else
        warning "Alembic not configured - skipping migrations"
    fi
    
    cd ../..
}

# Create Stripe products and prices
setup_stripe() {
    if [ "$ENABLE_BILLING" != "true" ]; then
        log "Billing disabled - skipping Stripe setup"
        return
    fi
    
    log "Setting up Stripe products and prices..."
    
    # This would normally call Stripe API to create products/prices
    # For now, just verify API key is valid
    
    if curl -s -o /dev/null -w "%{http_code}" \
        https://api.stripe.com/v1/products \
        -u "$STRIPE_API_KEY:" | grep -q "200"; then
        success "Stripe API key is valid"
    else
        error "Stripe API key is invalid"
        exit 1
    fi
}

# Create admin user
create_admin_user() {
    log "Creating admin user..."
    
    cd dashboard/backend
    
    if python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.user import User, Tenant
from services.auth_service import hash_password
import os

async def create_admin():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == 'admin'))
        if result.scalar_one_or_none():
            print('Admin user already exists')
            return
        
        # Create tenant
        tenant = Tenant(name='Admin Tenant', slug='admin')
        session.add(tenant)
        await session.commit()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            hashed_password=hash_password('changeme123'),
            tenant_id=tenant.id,
            subscription_plan='enterprise',
            subscription_status='active'
        )
        session.add(admin)
        await session.commit()
        print('Admin user created successfully')

asyncio.run(create_admin())
" 2>&1; then
        success "Admin user created/verified"
    else
        warning "Admin user creation failed - may already exist"
    fi
    
    cd ../..
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Production environment - skipping SSL generation (use Let's Encrypt)"
        return
    fi
    
    log "Generating self-signed SSL certificates..."
    
    mkdir -p dashboard/backend/ssl
    
    if [ ! -f "dashboard/backend/ssl/key.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -nodes \
            -keyout dashboard/backend/ssl/key.pem \
            -out dashboard/backend/ssl/cert.pem \
            -days 365 \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
            2>/dev/null
        
        success "SSL certificates generated"
    else
        log "SSL certificates already exist"
    fi
}

# Update configuration files
update_config() {
    log "Updating configuration files..."
    
    # Update .env file with production values
    if [ ! -f "dashboard/backend/.env" ]; then
        cp dashboard/backend/.env.example dashboard/backend/.env
        success "Created .env file from template"
    fi
}

# Start services
start_services() {
    log "Starting services..."
    
    # Check if already running
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        warning "Backend already running"
    else
        cd dashboard/backend
        nohup uvicorn main:app --host 0.0.0.0 --port 8001 --reload > logs/backend.log 2>&1 &
        success "Backend started on port 8001"
        cd ../..
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "========================================"
    echo "   QA-FRAMEWORK Setup Complete! ✅"
    echo "========================================"
    echo ""
    echo "Services:"
    echo "  • Backend API: http://localhost:8001"
    echo "  • API Docs: http://localhost:8001/docs"
    echo "  • Health Check: http://localhost:8001/health"
    echo ""
    echo "Admin Credentials:"
    echo "  • Username: admin"
    echo "  • Password: changeme123"
    echo "  ⚠️  Change password immediately!"
    echo ""
    echo "Next Steps:"
    echo "  1. Verify services: curl http://localhost:8001/health"
    echo "  2. Change admin password"
    echo "  3. Configure webhook endpoints in Stripe"
    echo "  4. Start frontend: cd dashboard/frontend && npm start"
    echo ""
}

# Main execution
main() {
    log "Starting QA-FRAMEWORK automated setup..."
    echo ""
    
    check_env_vars
    test_database
    test_redis
    run_migrations
    setup_stripe
    create_admin_user
    generate_ssl_certs
    update_config
    start_services
    print_summary
}

# Run main function
main "$@"
