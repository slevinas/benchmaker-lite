import statistics
from typing import Sequence


def summarize_latencies(latencies: Sequence[float]) -> dict:
    if not latencies:
        return {
            "count": 0,
            "avg": 0.0,
            "p95": 0.0,
            "min": 0.0,
            "max": 0.0,
        }

    lat_sorted = sorted(latencies)
    count = len(lat_sorted)
    avg = statistics.mean(lat_sorted)
    p95_index = max(int(0.95 * count) - 1, 0)
    p95 = lat_sorted[p95_index]

    return {
        "count": count,
        "avg": avg,
        "p95": p95,
        "min": lat_sorted[0],
        "max": lat_sorted[-1],
    }
