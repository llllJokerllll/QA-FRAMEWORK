#!/usr/bin/env python3
"""
Environment Configuration Validator

Validates that all required environment variables are properly configured
before starting the application.

Usage:
    python scripts/validate_config.py [--env development|staging|production]
"""

import os
import sys
import secrets
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ConfigCheck:
    name: str
    required: bool
    present: bool
    secure: bool
    message: str


class EnvironmentValidator:
    """Validates environment configuration for QA-FRAMEWORK backend."""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.checks: List[ConfigCheck] = []
        
    def validate(self) -> Tuple[bool, List[ConfigCheck]]:
        """Run all validation checks."""
        self._check_environment()
        self._check_database()
        self._check_jwt()
        self._check_redis()
        self._check_stripe()
        self._check_urls()
        
        all_passed = all(check.present or not check.required for check in self.checks)
        return all_passed, self.checks
    
    def _check_environment(self):
        """Validate ENVIRONMENT variable."""
        env = os.getenv("ENVIRONMENT", "development")
        valid_envs = ["development", "staging", "production"]
        
        self.checks.append(ConfigCheck(
            name="ENVIRONMENT",
            required=False,
            present=True,
            secure=env in valid_envs,
            message=f"Environment: {env}" + (f" (valid: {', '.join(valid_envs)})" if env not in valid_envs else "")
        ))
    
    def _check_database(self):
        """Validate database configuration."""
        db_url = os.getenv("DATABASE_URL")
        required = self.environment == "production"
        
        if db_url:
            # Check for insecure defaults
            insecure_patterns = ["localhost", "127.0.0.1", "qa_user:qa_password"]
            is_secure = not any(pattern in db_url for pattern in insecure_patterns)
            message = "Database URL configured" + (" (⚠️  contains localhost/insecure credentials)" if not is_secure else "")
        else:
            is_secure = False
            message = "DATABASE_URL not set" + (" - REQUIRED in production" if required else " (will use SQLite)")
        
        self.checks.append(ConfigCheck(
            name="DATABASE_URL",
            required=required,
            present=bool(db_url),
            secure=is_secure,
            message=message
        ))
    
    def _check_jwt(self):
        """Validate JWT configuration."""
        secret_key = os.getenv("JWT_SECRET_KEY")
        required = self.environment == "production"
        
        if secret_key:
            # Check minimum length (32 bytes = 256 bits)
            is_secure = len(secret_key) >= 32
            message = "JWT secret configured" + (f" (⚠️  too short: {len(secret_key)} chars, need 32+)" if not is_secure else "")
        else:
            is_secure = False
            message = "JWT_SECRET_KEY not set" + (" - REQUIRED in production" if required else " (will generate temporary)")
        
        self.checks.append(ConfigCheck(
            name="JWT_SECRET_KEY",
            required=required,
            present=bool(secret_key),
            secure=is_secure,
            message=message
        ))
    
    def _check_redis(self):
        """Validate Redis configuration."""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_password = os.getenv("REDIS_PASSWORD")
        
        required = self.environment == "production"
        
        # In production, Redis should not be localhost and should have password
        is_secure = True
        if self.environment == "production":
            if redis_host in ["localhost", "127.0.0.1"]:
                is_secure = False
            if not redis_password:
                is_secure = False
        
        message = f"Redis: {redis_host}:{redis_port}"
        if redis_password:
            message += " (password protected)"
        elif self.environment == "production":
            message += " (⚠️  no password)"
        
        self.checks.append(ConfigCheck(
            name="REDIS",
            required=required,
            present=True,  # Has defaults
            secure=is_secure,
            message=message
        ))
    
    def _check_stripe(self):
        """Validate Stripe configuration."""
        enable_billing = os.getenv("ENABLE_BILLING", "false").lower() == "true"
        api_key = os.getenv("STRIPE_API_KEY")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        required = enable_billing
        
        if enable_billing:
            has_api_key = bool(api_key)
            has_webhook = bool(webhook_secret)
            
            # Check for test keys in production
            is_secure = True
            if self.environment == "production":
                if api_key and api_key.startswith("sk_test_"):
                    is_secure = False
                    self.checks.append(ConfigCheck(
                        name="STRIPE_API_KEY",
                        required=True,
                        present=has_api_key,
                        secure=False,
                        message="⚠️  Using TEST Stripe key in production!"
                    ))
                    return
            
            message = "Stripe configured" if (has_api_key and has_webhook) else "Stripe incomplete"
            if not has_api_key:
                message += " (missing API key)"
            if not has_webhook:
                message += " (missing webhook secret)"
            
            self.checks.append(ConfigCheck(
                name="STRIPE",
                required=required,
                present=has_api_key and has_webhook,
                secure=is_secure,
                message=message
            ))
        else:
            self.checks.append(ConfigCheck(
                name="STRIPE",
                required=False,
                present=True,
                secure=True,
                message="Billing disabled (ENABLE_BILLING=false)"
            ))
    
    def _check_urls(self):
        """Validate application URLs."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        api_url = os.getenv("QA_FRAMEWORK_API_URL", "http://localhost:8001")
        
        # In production, URLs should not be localhost
        is_secure = True
        if self.environment == "production":
            if "localhost" in frontend_url or "localhost" in api_url:
                is_secure = False
        
        self.checks.append(ConfigCheck(
            name="URLs",
            required=False,
            present=True,
            secure=is_secure,
            message=f"Frontend: {frontend_url}, API: {api_url}" + (" (⚠️  localhost in production)" if not is_secure else "")
        ))


def print_report(checks: List[ConfigCheck], environment: str):
    """Print a formatted validation report."""
    print("\n" + "="*70)
    print(f"QA-FRAMEWORK Configuration Validator")
    print(f"Environment: {environment.upper()}")
    print("="*70 + "\n")
    
    # Categorize checks
    passed = [c for c in checks if c.present or not c.required]
    warnings = [c for c in checks if c.present and not c.secure]
    missing = [c for c in checks if not c.present and c.required]
    
    # Print results
    for check in checks:
        status_icon = "✅" if (check.present or not check.required) and check.secure else "⚠️ " if check.present else "❌"
        print(f"{status_icon} {check.name:20} {check.message}")
    
    print("\n" + "="*70)
    
    # Summary
    if missing:
        print(f"\n❌ MISSING REQUIRED CONFIGURATION ({len(missing)} issues)")
        print("\nThe following REQUIRED environment variables are not set:")
        for check in missing:
            print(f"  - {check.name}: {check.message}")
        print("\nSet these variables before starting the application.")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql+asyncpg://user:pass@host:5432/db'")
        print("  export JWT_SECRET_KEY='$(python -c \"import secrets; print(secrets.token_urlsafe(32))\")'")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)} issues)")
        print("\nConfiguration issues detected:")
        for check in warnings:
            print(f"  - {check.name}: {check.message}")
    
    if not missing and not warnings:
        print("\n✅ All configuration checks passed!")
        print("\nYou can safely start the application:")
        print("  cd dashboard/backend")
        print("  uvicorn main:app --reload")
    
    print("="*70 + "\n")


def generate_secret_key():
    """Generate a secure JWT secret key."""
    return secrets.token_urlsafe(32)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate QA-FRAMEWORK environment configuration")
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default=os.getenv("ENVIRONMENT", "development"),
        help="Environment to validate for"
    )
    parser.add_argument(
        "--generate-secret",
        action="store_true",
        help="Generate a secure JWT secret key"
    )
    
    args = parser.parse_args()
    
    if args.generate_secret:
        print(f"\nGenerated JWT Secret Key:")
        print(f"  {generate_secret_key()}")
        print(f"\nAdd to your .env file:")
        print(f"  JWT_SECRET_KEY={generate_secret_key()}\n")
        return 0
    
    # Run validation
    validator = EnvironmentValidator(args.env)
    all_passed, checks = validator.validate()
    
    # Print report
    print_report(checks, args.env)
    
    # Exit with appropriate code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
