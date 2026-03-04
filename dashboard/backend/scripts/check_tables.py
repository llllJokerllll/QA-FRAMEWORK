import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from database import AsyncSessionFactory
from sqlalchemy import text


async def check_tables():
    async with AsyncSessionFactory() as db:
        result = await db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' AND table_name LIKE \'cron%\''))
        print('Cron tables found:')
        for row in result:
            print(f'  - {row[0]}')
        print()


if __name__ == "__main__":
    asyncio.run(check_tables())
