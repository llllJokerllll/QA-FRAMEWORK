"""
Seed Cron Jobs

Populates the database with initial cron jobs for QA-FRAMEWORK.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.cron import CronJob, CronExecution
from datetime import datetime, timedelta
from typing import List, Optional

from database import AsyncSessionFactory


async def seed_cron_jobs(db: AsyncSession):
    """Seed the database with initial cron jobs"""

    # Initial cron jobs configuration
    initial_jobs = [
        {
            "name": "daily-ai-digest",
            "schedule": "0 13 * * *",
            "description": "Genera digest diario de AI",
            "script_path": "/home/ubuntu/.openclaw/workspace/scripts/daily-ai-digest.sh",
            "status": "active"
        },
        {
            "name": "self-healing",
            "schedule": "*/30 * * * *",
            "description": "Auto-reparación de tests",
            "script_path": "/home/ubuntu/.openclaw/workspace/scripts/self-healing.sh",
            "status": "active"
        },
        {
            "name": "heartbeat",
            "schedule": "0 * * * *",
            "description": "Health check hourly",
            "script_path": "/home/ubuntu/.openclaw/workspace/scripts/heartbeat.sh",
            "status": "active"
        },
        {
            "name": "weekly-report",
            "schedule": "0 9 * * 1",
            "description": "Genera reporte semanal de QA",
            "script_path": "/home/ubuntu/.openclaw/workspace/scripts/weekly-report.sh",
            "status": "active"
        },
        {
            "name": "monthly-backup",
            "schedule": "0 2 1 * *",
            "description": "Backup mensual de datos",
            "script_path": "/home/ubuntu/.openclaw/workspace/scripts/monthly-backup.sh",
            "status": "active"
        },
    ]

    # Check if jobs already exist
    existing_jobs = await db.execute(select(CronJob))
    job_names = [job.name for job in existing_jobs.scalars().all()]

    for job_data in initial_jobs:
        if job_data["name"] in job_names:
            print(f"Skipping {job_data['name']} - already exists")
            continue

        # Create cron job
        job = CronJob(**job_data)
        db.add(job)
        print(f"Created cron job: {job_data['name']}")

    await db.commit()
    print("\n✅ Cron jobs seeded successfully!")


async def seed_executions(db: AsyncSession, num_executions: int = 10):
    """Seed mock execution history for existing jobs"""

    # Get all jobs
    result = await db.execute(select(CronJob))
    jobs = result.scalars().all()

    if not jobs:
        print("No jobs found, skipping execution seeding")
        return

    for job in jobs:
        # Generate mock executions
        for i in range(num_executions):
            # Randomly decide if this execution was successful or failed
            if i % 3 == 0:  # 1 out of 3 executions is failed
                status = "error"
                error_message = "Script execution failed: Timeout exceeded"
                duration = 60.0 + i * 0.5  # Random duration
            elif i % 3 == 1:  # 1 out of 3 executions is skipped
                status = "skipped"
                duration = 0.0
            else:  # 1 out of 3 executions is successful
                status = "success"
                error_message = None
                duration = 30.0 + i * 0.3  # Random duration

            # Calculate timestamps
            hours_ago = num_executions - i
            started_at = datetime.utcnow() - timedelta(hours=hours_ago)

            execution = CronExecution(
                job_id=job.id,
                status=status,
                started_at=started_at,
                finished_at=started_at + timedelta(seconds=duration) if status != "skipped" else None,
                duration=duration,
                output=f"Execution {i+1} for {job.name} completed successfully" if status == "success" else None,
                error_message=error_message
            )

            db.add(execution)
            job.last_run = started_at
            job.success_count += (1 if status == "success" else 0)
            job.error_count += (1 if status == "error" else 0)
            job.avg_duration = (job.avg_duration * (i + 1) + duration) / (i + 2)

        print(f"Added {num_executions} mock executions for job: {job.name}")

    await db.commit()
    print("\n✅ Mock executions seeded successfully!")


async def main():
    """Main function to seed cron jobs"""
    print("🚀 Starting Cron Jobs seeding...\n")

    async with AsyncSessionFactory() as db:
        # Seed jobs
        await seed_cron_jobs(db)

        # Reset the session
        await db.close()

        async with AsyncSessionFactory() as db:
            # Seed executions
            await seed_executions(db)

    print("\n🎉 Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
