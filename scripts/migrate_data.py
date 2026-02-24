#!/usr/bin/env python3
"""
CLI script for migrating data to multi-tenant architecture.

This script handles the migration of existing data to the new multi-tenant
system, creating a default tenant and migrating all related entities.
"""

import argparse
import asyncio
import logging
import sys
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from dashboard.backend.database import AsyncSessionFactory
from src.domain.entities.tenant import Tenant, TenantPlan, TenantStatus
from src.infrastructure.migration import (
    DataMigrator,
    UserMigrator,
    TestMigrator,
    MigrationReportGenerator,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def migrate_data(
    dry_run: bool = False,
    output_file: Optional[str] = None,
    verbose: bool = False,
) -> int:
    """
    Execute the multi-tenant data migration.

    Args:
        dry_run: If True, simulate migration without making changes
        output_file: Optional file path to save the report
        verbose: If True, enable verbose logging

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        start_time = datetime.utcnow()
        logger.info("Starting multi-tenant data migration")
        logger.info(f"Dry run mode: {dry_run}")

        # Create database engine and session
        from config import settings
        engine = create_async_engine(settings.database_url)
        async with engine.begin() as conn:
            async with AsyncSessionFactory() as session:
                # Step 1: Create default tenant
                logger.info("\n📝 Step 1: Creating default tenant...")
                migrator = DataMigrator(session, dry_run=dry_run)
                default_tenant = await migrator.create_default_tenant()

                if default_tenant is None:
                    logger.warning("Default tenant already exists or would not be created in dry-run mode")

                # Step 2: Migrate users
                logger.info("\n👤 Step 2: Migrating users...")
                user_migrator = UserMigrator(session, dry_run=dry_run)
                await user_migrator.migrate_users(default_tenant)
                user_migrator.finalize()

                # Step 3: Migrate tests
                logger.info("\n🧪 Step 3: Migrating tests...")
                test_migrator = TestMigrator(session, dry_run=dry_run)
                test_results = await test_migrator.migrate_tests(default_tenant)
                test_migrator.finalize()

                # Step 4: Generate report
                logger.info("\n📊 Step 4: Generating migration report...")
                report_gen = MigrationReportGenerator()
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                report = report_gen.generate(
                    migrators=[migrator, user_migrator, test_migrator],
                    overall_status=migrator.stats["status"],
                    execution_time=execution_time,
                )

                # Print report to console
                report_gen.print_console(report)

                # Save report to file if requested
                if output_file:
                    try:
                        report_gen.save_to_file(report, output_file)
                        logger.info(f"Report saved to: {output_file}")
                    except Exception as e:
                        logger.error(f"Failed to save report: {str(e)}")

                # Check if migration was successful
                overall_status = migrator.stats["status"]
                success = (
                    overall_status == DataMigrator.MigrationStatus.COMPLETED
                    and len(report_gen.get_errors(report)) == 0
                )

                if success:
                    logger.info("\n✅ Migration completed successfully!")
                else:
                    logger.warning("\n⚠️  Migration completed with issues.")

                # Return exit code
                return 0 if success else 1

    except Exception as e:
        logger.error(f"\n❌ Migration failed with error: {str(e)}", exc_info=True)
        return 1

    finally:
        # Ensure we clean up database connections
        await engine.dispose()


def main():
    """Main entry point for the migration CLI."""
    parser = argparse.ArgumentParser(
        description="Migrate data to multi-tenant architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run migration (simulated)
  python scripts/migrate_data.py --dry-run

  # Run migration for real
  python scripts/migrate_data.py

  # Run migration with detailed output
  python scripts/migrate_data.py --verbose

  # Run migration and save report
  python scripts/migrate_data.py --output report.json
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without making changes",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to save migration report (JSON format)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Run migration
    exit_code = asyncio.run(migrate_data(
        dry_run=args.dry_run,
        output_file=args.output,
        verbose=args.verbose,
    ))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
