#!/usr/bin/env python3
"""
Environment Validation Script for QA-FRAMEWORK

This script checks if all required environment variables and services
are properly configured for production deployment.

Usage:
    python scripts/validate_environment.py
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class EnvironmentValidator:
    """Validates environment configuration for QA-FRAMEWORK."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
        
    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}{text.center(60)}{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    def print_check(self, name: str, status: str, message: str = ""):
        """Print a check result."""
        icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        color = GREEN if status == "success" else RED if status == "error" else YELLOW
        print(f"{icon} {name:<40} {color}{message}{RESET}")
        
        if status == "success":
            self.successes.append(name)
        elif status == "error":
            self.errors.append(f"{name}: {message}")
        else:
            self.warnings.append(f"{name}: {message}")
    
    def check_environment_variables(self):
        """Check required environment variables."""
        self.print_header("Environment Variables Check")
        
        required_vars = {
            "JWT_SECRET_KEY": "JWT secret for token signing",
            "DATABASE_URL": "PostgreSQL connection string",
            "REDIS_URL": "Redis connection string",
            "STRIPE_API_KEY": "Stripe API key for billing",
            "STRIPE_WEBHOOK_SECRET": "Stripe webhook secret",
        }
        
        recommended_vars = {
            "GOOGLE_CLIENT_ID": "Google OAuth client ID",
            "GOOGLE_CLIENT_SECRET": "Google OAuth client secret",
            "GITHUB_CLIENT_ID": "GitHub OAuth client ID",
            "GITHUB_CLIENT_SECRET": "GitHub OAuth client secret",
        }
        
        # Check required variables
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                self.print_check(var, "error", "NOT SET")
            elif "placeholder" in value.lower() or "dev-key" in value.lower():
                self.print_check(var, "warning", "USING PLACEHOLDER")
            else:
                # Mask sensitive values
                masked = value[:10] + "..." if len(value) > 10 else "***"
                self.print_check(var, "success", f"SET ({masked})")
        
        # Check recommended variables
        print(f"\n{YELLOW}Recommended (Optional):{RESET}")
        for var, description in recommended_vars.items():
            value = os.getenv(var)
            if not value:
                self.print_check(var, "warning", "NOT SET (optional)")
            else:
                self.print_check(var, "success", "SET")
    
    async def check_database_connection(self):
        """Check database connectivity."""
        self.print_header("Database Connection Check")
        
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            self.print_check("PostgreSQL", "error", "DATABASE_URL not set")
            return
        
        if "localhost" in database_url or "placeholder" in database_url.lower():
            self.print_check("PostgreSQL", "warning", "Using local/placeholder URL")
            return
        
        try:
            # Try to import and connect
            sys.path.insert(0, str(Path(__file__).parent.parent / "dashboard" / "backend"))
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy import text
            
            engine = create_async_engine(database_url, echo=False)
            
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()
            
            await engine.dispose()
            self.print_check("PostgreSQL", "success", "Connection successful")
            
        except Exception as e:
            self.print_check("PostgreSQL", "error", str(e)[:50])
    
    async def check_redis_connection(self):
        """Check Redis connectivity."""
        self.print_header("Redis Connection Check")
        
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            self.print_check("Redis", "error", "REDIS_URL not set")
            return
        
        if "localhost" in redis_url:
            self.print_check("Redis", "warning", "Using local URL")
            return
        
        try:
            # Try to import and connect
            import redis.asyncio as redis
            
            client = redis.from_url(redis_url, decode_responses=True)
            await client.ping()
            await client.close()
            
            self.print_check("Redis", "success", "Connection successful")
            
        except Exception as e:
            self.print_check("Redis", "error", str(e)[:50])
    
    def check_stripe_configuration(self):
        """Check Stripe configuration."""
        self.print_header("Stripe Configuration Check")
        
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # Check API key
        if not api_key:
            self.print_check("Stripe API Key", "error", "NOT SET")
        elif api_key.startswith("sk_test_"):
            self.print_check("Stripe API Key", "success", "Test mode")
        elif api_key.startswith("sk_live_"):
            self.print_check("Stripe API Key", "success", "Live mode")
        elif "placeholder" in api_key.lower():
            self.print_check("Stripe API Key", "error", "USING PLACEHOLDER")
        else:
            self.print_check("Stripe API Key", "warning", "Unknown format")
        
        # Check webhook secret
        if not webhook_secret:
            self.print_check("Stripe Webhook Secret", "error", "NOT SET")
        elif webhook_secret.startswith("whsec_"):
            self.print_check("Stripe Webhook Secret", "success", "Configured")
        elif "placeholder" in webhook_secret.lower():
            self.print_check("Stripe Webhook Secret", "error", "USING PLACEHOLDER")
        else:
            self.print_check("Stripe Webhook Secret", "warning", "Unknown format")
        
        # Try to validate API key
        if api_key and not "placeholder" in api_key.lower():
            try:
                import stripe
                stripe.api_key = api_key
                # Try to retrieve balance (lightweight API call)
                stripe.Balance.retrieve()
                self.print_check("Stripe API", "success", "API key valid")
            except Exception as e:
                self.print_check("Stripe API", "error", f"API call failed: {str(e)[:30]}")
    
    def check_file_structure(self):
        """Check required files and directories."""
        self.print_header("File Structure Check")
        
        required_files = [
            "dashboard/backend/.env",
            "dashboard/backend/alembic.ini",
            "dashboard/backend/requirements.txt",
            "dashboard/frontend/package.json",
        ]
        
        required_dirs = [
            "dashboard/backend/alembic/versions",
            "dashboard/backend/tests",
            "dashboard/frontend/src",
        ]
        
        for file in required_files:
            path = Path(__file__).parent.parent / file
            if path.exists():
                self.print_check(f"File: {file}", "success", "Exists")
            else:
                self.print_check(f"File: {file}", "error", "Missing")
        
        for dir in required_dirs:
            path = Path(__file__).parent.parent / dir
            if path.exists():
                self.print_check(f"Dir: {dir}", "success", "Exists")
            else:
                self.print_check(f"Dir: {dir}", "error", "Missing")
    
    def check_python_dependencies(self):
        """Check Python dependencies."""
        self.print_header("Python Dependencies Check")
        
        required_packages = [
            "fastapi",
            "sqlalchemy",
            "alembic",
            "stripe",
            "redis",
            "pydantic",
            "pytest",
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.print_check(f"Package: {package}", "success", "Installed")
            except ImportError:
                self.print_check(f"Package: {package}", "error", "Not installed")
    
    def generate_report(self):
        """Generate validation report."""
        self.print_header("Validation Summary")
        
        total_checks = len(self.successes) + len(self.errors) + len(self.warnings)
        
        print(f"Total checks: {total_checks}")
        print(f"{GREEN}✅ Passed: {len(self.successes)}{RESET}")
        print(f"{YELLOW}⚠️  Warnings: {len(self.warnings)}{RESET}")
        print(f"{RED}❌ Failed: {len(self.errors)}{RESET}")
        
        if self.errors:
            print(f"\n{RED}Errors found:{RESET}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print()
        
        if not self.errors:
            print(f"{GREEN}{'🎉 Environment is ready for deployment!':^60}{RESET}\n")
            return 0
        else:
            print(f"{RED}{'⚠️  Environment needs configuration before deployment':^60}{RESET}\n")
            return 1
    
    async def run_all_checks(self):
        """Run all validation checks."""
        self.print_header("QA-FRAMEWORK Environment Validator")
        
        print("Checking environment configuration...\n")
        
        # Run all checks
        self.check_environment_variables()
        await self.check_database_connection()
        await self.check_redis_connection()
        self.check_stripe_configuration()
        self.check_file_structure()
        self.check_python_dependencies()
        
        # Generate report
        return self.generate_report()


async def main():
    """Main entry point."""
    validator = EnvironmentValidator()
    exit_code = await validator.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
