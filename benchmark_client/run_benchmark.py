import asyncio
import time

import httpx

from .utils import summarize_latencies

API_URL = "http://localhost:8000/api/vector/add"
CONCURRENCY = 10
REQUESTS_PER_WORKER = 50


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


async def run_benchmark() -> None:
    latencies: list[float] = []
    tasks = [worker(i, latencies) for i in range(CONCURRENCY)]
    await asyncio.gather(*tasks)

    summary = summarize_latencies(latencies)
    print("=== Benchmark Summary ===")
    print(f"Total requests: {summary['count']}")
    print(f"Avg latency:   {summary['avg']:.4f}s")
    print(f"P95 latency:   {summary['p95']:.4f}s")
    print(f"Min latency:   {summary['min']:.4f}s")
    print(f"Max latency:   {summary['max']:.4f}s")


if __name__ == "__main__":
    asyncio.run(run_benchmark())
