# ClickHouse Setup

This directory contains the initialization script for ClickHouse.

- `init.sql` creates a simple `benchmark_results` table used to store
  aggregate statistics for benchmark runs (e.g., average latency).

The table is intentionally simple. The goal of this project is to demonstrate
how benchmark results **could** be stored and queried in an observability /
performance context, not to model every possible metric.
