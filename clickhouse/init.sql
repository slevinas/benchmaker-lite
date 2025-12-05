CREATE DATABASE IF NOT EXISTS otel;

-- existing content below (your benchmark_results etc.)




-- Simple table to store benchmark run summaries.
CREATE TABLE IF NOT EXISTS benchmark_results (
    timestamp     DateTime DEFAULT now(),
    endpoint      String,
    avg_latency   Float64,
    p95_latency   Float64,
    p99_latency   Float64,
    min_latency   Float64,
    max_latency   Float64,
    total_requests UInt32
) ENGINE = MergeTree()
ORDER BY (timestamp, endpoint);

