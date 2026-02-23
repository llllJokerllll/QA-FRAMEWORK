#!/bin/bash
# ========================================
# Database Initialization Script
# Runs migrations and creates initial data
# ========================================

set -e

echo "🚀 Initializing QA-FRAMEWORK database..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Database is ready!"

# Run Alembic migrations
echo "📦 Running database migrations..."
cd /app
alembic upgrade head

# Create initial admin user (if not exists)
echo "👤 Creating initial admin user..."
python3 << EOF
from database import init_db, get_db
from models import User
from sqlalchemy import select
from passlib.context import CryptContext
import asyncio
import os

async def create_admin():
    await init_db()

    async with get_db() as db:
        # Check if admin exists
        result = await db.execute(select(User).where(User.email == "admin@qaframework.io"))
        admin = result.scalar_one_or_none()

        if not admin:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = User(
                email="admin@qaframework.io",
                username="admin",
                hashed_password=pwd_context.hash("changeme123"),
                is_active=True,
                is_superuser=True,
            )
            db.add(admin)
            await db.commit()
            print("✅ Admin user created: admin@qaframework.io")
        else:
            print("ℹ️  Admin user already exists")

asyncio.run(create_admin())
EOF

echo "✅ Database initialization complete!"
echo ""
echo "Default credentials:"
echo "  Email: admin@qaframework.io"
echo "  Password: changeme123"
echo "  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"
