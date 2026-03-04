import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database import AsyncSessionFactory
from sqlalchemy import text


async def check_data():
    async with AsyncSessionFactory() as db:
        # Check cron_jobs count
        result = await db.execute(text('SELECT COUNT(*) FROM cron_jobs'))
        jobs_count = result.scalar()
        print(f'📊 Total cron jobs: {jobs_count}')

        # Check cron_executions count
        result = await db.execute(text('SELECT COUNT(*) FROM cron_executions'))
        exec_count = result.scalar()
        print(f'📊 Total cron executions: {exec_count}')

        # Get job details
        result = await db.execute(text('SELECT name, schedule, status, success_count, error_count FROM cron_jobs'))
        print(f'\n📋 Cron jobs:')
        for row in result:
            print(f'  - {row.name}: {row.schedule} ({row.status}) - Success: {row.success_count}, Errors: {row.error_count}')
        print()


if __name__ == "__main__":
    asyncio.run(check_data())
