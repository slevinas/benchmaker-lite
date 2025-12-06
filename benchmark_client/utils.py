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

    def pct(p):
        return lat_sorted[int(count * p)]

    return {
        "count": count,
        "avg": sum(latencies) / count,
        "p95": pct(0.95),
        "p99": pct(0.99),   
        "min": lat_sorted[0],
        "max": lat_sorted[-1],
    }

def print_table(rows: list[list[str]], headers: list[str]) -> None:
    # Determine column widths
    cols = list(zip(*([headers] + rows)))
    widths = [max(len(str(item)) for item in col) for col in cols]

    # Format row helper
    def fmt_row(row):
        return "  ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))

    print(fmt_row(headers))
    print("-" * (sum(widths) + (2 * (len(headers)-1))))
    for row in rows:
        print(fmt_row(row))
