"""
Test Cron Jobs API

Tests the cron jobs endpoints.
"""

import asyncio
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database import AsyncSessionFactory
from models.cron import CronJob
from services.cron_service import CronService
from sqlalchemy import select


async def test_cron_api():
    """Test the cron jobs API"""
    print("🧪 Testing Cron Jobs API\n")

    async with AsyncSessionFactory() as db:
        service = CronService(db)

        # Test 1: Get all jobs
        print("Test 1: Get all active jobs")
        jobs = await service.get_jobs()
        print(f"✅ Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"   - {job.name} (ID: {job.id})")
        print()

        # Test 2: Get job by ID
        if jobs:
            print("Test 2: Get job by ID")
            job = await service.get_job(jobs[0].id)
            print(f"✅ Job found: {job.name}")
            print(f"   - Schedule: {job.schedule}")
            print(f"   - Status: {job.status}")
            print(f"   - Success rate: {job.success_rate:.2%}")
            print(f"   - Avg duration: {job.avg_duration:.2f}s")
            print()

        # Test 3: Get executions
        if jobs:
            print("Test 3: Get job executions")
            executions = await service.get_executions(jobs[0].id, limit=5)
            print(f"✅ Found {len(executions)} executions:")
            for exec in executions:
                print(f"   - {exec.status} at {exec.started_at} (duration: {exec.duration}s)")
            print()

        # Test 4: Get stats
        print("Test 4: Get stats")
        stats = await service.get_stats()
        print(f"✅ Statistics:")
        print(f"   - Total jobs: {stats.total_jobs}")
        print(f"   - Active jobs: {stats.active_jobs}")
        print(f"   - Paused jobs: {stats.paused_jobs}")
        print(f"   - Error jobs: {stats.error_jobs}")
        print(f"   - Today's executions: {stats.total_executions_today}")
        print(f"   - Today's success rate: {stats.success_rate_today:.2%}")
        print()

        # Test 5: Run job manually
        if jobs:
            print("Test 5: Run job manually")
            result = await service.run_job(jobs[0].id)
            print(f"✅ Job started: {result}")
            print()

    print("🎉 All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_cron_api())
