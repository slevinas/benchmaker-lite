# scratch_check_clickhouse.py
import asyncio
from clickhouse import ClickHouseClient

async def main():
    async with ClickHouseClient() as ch:
        print("Ping:", await ch.ping())
        print("Tables in default:")
        print(await ch.execute("SHOW TABLES FROM default"))

asyncio.run(main())
