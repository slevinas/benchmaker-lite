from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List
import json
import httpx

from .utils import summarize_latencies, print_table
# from benchmark_client.clickhouse import save_summary
from clickhouse import ClickHouseClient 

# REPO_ROOT = Path(__file__).resolve().parents[1]
# ENV_FILE = REPO_ROOT / ".env"
# _load_dotenv(ENV_FILE)
# logger.info(f"[conftest] Loaded .env from {ENV_FILE}")

API_URL = "http://localhost:8000/api/vector/add"
CONCURRENCY = 1
REQUESTS_PER_WORKER = 1


async def save_summary_to_clickhouse(summary: Dict[str, Any]) -> None:
    """
    Save a single benchmark summary into ClickHouse using ClickHouseClient.
    Adjust the mapping to match your actual benchmark_results schema.
    """
    row = {
        "endpoint": API_URL,
        "total_requests": summary["count"],
        "avg_latency": summary["avg"],
        "p95_latency": summary["p95"],
        "p99_latency": summary["p99"],
        "min_latency": summary["min"],
        "max_latency": summary["max"],
        # timestamp column can default to now() in ClickHouse schema
    }

    async with ClickHouseClient() as ch:
        insert_results = await ch.insert_json_each_row("benchmark_results", [row])
        # print("Insert results:", insert_results)

async def worker(worker_id: int, latencies: list[float]) -> None:
    async with httpx.AsyncClient() as client:
        for _ in range(REQUESTS_PER_WORKER):
            payload = {"a": [1, 2, 3], "b": [4, 5, 6]}
            start = time.perf_counter()
            resp = await client.post(API_URL, json=payload)
            duration = time.perf_counter() - start

            # In a real system you’d add error handling / retries.
            resp.raise_for_status()
            latencies.append(duration)
            try:
                body = resp.json()
                print("------------------------------")
                print(" ")
                print(json.dumps(body, indent=2))
                print("------------------------------")
                # logger.debug("upload response JSON: %s", body)  
            except Exception:
                body = {"text": resp.text[:2000]}
                # logger.warning("non-JSON response (showing first 2k chars)")


async def run_benchmark() -> None:
    latencies: list[float] = []
    tasks = [worker(i, latencies) for i in range(CONCURRENCY)]
    await asyncio.gather(*tasks)

    summary = summarize_latencies(latencies)
    # print("=== Benchmark Summary ===")
    # print(f"Total requests: {summary['count']}")
    # print(f"Avg latency:   {summary['avg']:.4f}s")
    # print(f"P95 latency:   {summary['p95']:.4f}s")
    # print(f"Min latency:   {summary['min']:.4f}s")
    # print(f"Max latency:   {summary['max']:.4f}s")
    print("=== Benchmark Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # Save the summary into ClickHouse
    print("\nSaving summary to ClickHouse...")
    # await save_summary(summary, endpoint=API_URL)
    await save_summary_to_clickhouse(summary)
    async with ClickHouseClient() as ch:
        print("\nVerifying saved benchmark results:")
        verification_results_raw = await ch.execute("SELECT * \
                                         FROM benchmark_results \
                                         ORDER BY timestamp DESC")
    print(verification_results_raw)
    # Format ClickHouse output into rows
    parsed = []
    # for line in verification_results_raw.strip().splitlines():
    #     parts = line.split()  # crude split, but works because your table is simple
    #     if len(parts) >= 7:
    #         parsed.append(parts)

    # headers = ["timestamp", "endpoint", "avg", "p95", "p99", "min", "max", "req"]
    # print("\n=== Recent Benchmark Results ===")
    # print_table(parsed, headers)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
