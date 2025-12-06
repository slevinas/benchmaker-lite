# scratch_check_clickhouse.py

import asyncio
from clickhouse.client import ClickHouseClient


async def main():
    async with ClickHouseClient() as ch:
        print("Config:")
        print(f"  host: {ch.config.host}")
        print(f"  port: {ch.config.port}")
        print(f"  user: {ch.config.user}")
        print(f"  db:   {ch.config.database}")
        print(f"  password: {ch.config.password}")

        print("\nPing ClickHouse (SELECT 1):")
        ok = await ch.ping()
        print("  ping:", ok)

        print("\nSHOW TABLES FROM default:")
        txt = await ch.execute("SHOW TABLES FROM default")
        print(txt)


        print("\nSHOW DATABASES:")
        databases = await ch.execute("SHOW DATABASES")
        print(databases)

        print("\nSELECT * FROM benchmark_results:")
        txt = await ch.execute("SELECT * FROM benchmark_results")
        print(txt)

        # print("\nSELECT * FROM benchmark_results:")
        # results = await ch.get_last_benchmarks()
        # print(results)


if __name__ == "__main__":
    asyncio.run(main())
