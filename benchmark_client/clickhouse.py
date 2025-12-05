import httpx
import json


# benchmark_client/clickhouse.py
"""
Backwards-compat shim for ClickHouse client.

The real implementation now lives in clickhouse.client.
Import ClickHouseClient / ClickHouseConfig from there instead.
"""

from clickhouse import ClickHouseClient, ClickHouseConfig  # noqa: F401

__all__ = ["ClickHouseClient", "ClickHouseConfig"]



# # CLICKHOUSE_URL = "http://localhost:8123/?query=INSERT INTO benchmark_results FORMAT JSONEachRow"
# CLICKHOUSE_URL = (
#     "http://localhost:8123/?user=default&password=benchmaker"
#     "&query=INSERT INTO benchmark_results FORMAT JSONEachRow"
# )


# async def save_summary(summary: dict, endpoint: str):
#     """
#     Insert a benchmark summary row into ClickHouse via HTTP.
#     """
#     payload = [
#         {
#             "endpoint": endpoint,
#             "avg_latency": summary["avg"],
#             "p95_latency": summary["p95"],
#             "total_requests": summary["count"],
#         }
#     ]

#     async with httpx.AsyncClient() as client:
#         r = await client.post(
#             CLICKHOUSE_URL,
#             content=json.dumps(payload),
#             headers={"Content-Type": "application/json"},
#         )
#         r.raise_for_status()
#         return True
