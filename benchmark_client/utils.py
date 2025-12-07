import statistics
from typing import Sequence, Any, Iterable

import json
import os
import time
import pathlib

import sys

from pathlib import Path  

def _to_jsonable(x):
    import pathlib
    if isinstance(x, dict):
        return {k: _to_jsonable(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_to_jsonable(v) for v in x]
    if isinstance(x, pathlib.Path):
        return str(x)
    return x

def secure_save_file(path, data) -> None:
    """Save file with secure permissions (0600)."""
    filepath = pathlib.Path(path)
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temp_path = filepath.with_suffix('.tmp')
        # print(f"Received data to save: {data}")
        with open(temp_path, "w") as f:
            json.dump(_to_jsonable(data), f, indent=4)   # <-- use converter here
            # json.dump(data, f, indent=4)   
        os.chmod(temp_path, 0o600)
        temp_path.replace(filepath)
        # print(f"[Zigi]Saved secure file: {filepath}")
    except (OSError, IOError) as e:
        print(f"[Zigi]Error: Failed to save file {filepath}: {e}")
        raise SystemExit(f"[Zigi]Cannot save configuration: {e}") from e
    
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

# def print_table(rows: list[list[str]], headers: list[str]) -> None:
#     # Determine column widths
#     cols = list(zip(*([headers] + rows)))
#     widths = [max(len(str(item)) for item in col) for col in cols]

#     # Format row helper
#     def fmt_row(row):
#         return "  ".join(str(val).ljust(widths[i]) for i, val in enumerate(row))

#     print(fmt_row(headers))
#     print("-" * (sum(widths) + (2 * (len(headers)-1))))
#     for row in rows:
#         print(fmt_row(row))
# benchmark_client/utils.py



def print_table(rows: Iterable[Sequence[Any]], headers: Sequence[str]) -> None:
    """
    Pretty-print a table with fixed-width columns.

    - rows: iterable of row sequences (list/tuple/etc.)
    - headers: sequence of column names
    """
    new_rows = [list(r) for r in rows]
    # print(f"\nPrinting table received {rows}")
    # print(f"\nAnd created rows:\n {new_rows}   \n")

    # if not new_rows:
    #     print("(no results)")
    #     return

    # Start widths from headers
    widths: list[int] = [len(str(h)) for h in headers]

    # Extend / grow widths based on data rows
    for row in rows:
        for i, val in enumerate(row):
            s = str(val)
            if i >= len(widths):
                widths.append(len(s))
            else:
                widths[i] = max(widths[i], len(s))

    def fmt_row(cells: Sequence[Any]) -> str:
        # zip to avoid going past widths even if a row is longer/shorter
        return "  ".join(
            str(val).ljust(width)
            for val, width in zip(cells, widths)
        )

    # Print header
    print(fmt_row(headers))

    # Separator line
    total_width = sum(widths) + 2 * (len(widths) - 1)
    print("-" * total_width)

    # Print rows
    for row in rows:
        print(fmt_row(row))
