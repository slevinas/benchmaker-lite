# clickhouse/client.py

from __future__ import annotations
from pathlib import Path  
import json
import os
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional
import logging
import httpx



from dotenv import load_dotenv

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / ".env"

# Load .env into process environment
load_dotenv(ENV_FILE)
print(f"[clickhouse/client.py] Loaded .env from {ENV_FILE}")


@dataclass
class ClickHouseConfig:
    host: str = "localhost"
    port: int = 8123
    user: str = "default"
    password: str = ""
    database: str = "default"
    timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "ClickHouseConfig":
        
        return cls(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
            user=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", "benchmaker"),
            database=os.getenv("CLICKHOUSE_DB", "default"),
            timeout=float(os.getenv("CLICKHOUSE_TIMEOUT", "10.0")),
        )


class ClickHouseClient:
    """
    Minimal async HTTP client for ClickHouse.

    - Uses ClickHouseConfig.from_env() so credentials stay in env vars.
    - Supports generic SQL execution + JSONEachRow inserts.
    """

    def __init__(self, config: Optional[ClickHouseConfig] = None) -> None:
        self.config = config or ClickHouseConfig.from_env()
        print(f"[ClickHouseClient] Config: {self.config}")
        self._base_url = f"http://{self.config.host}:{self.config.port}"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ClickHouseClient":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ---------- internal helpers ----------

    def _auth_params(self) -> str:
        return (
            f"user={self.config.user}"
            f"&password={self.config.password}"
            f"&database={self.config.database}"
        )

    async def _post(
        self,
        sql: str,
        data: Optional[bytes | str] = None,
    ) -> httpx.Response:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)

        # We pass SQL via the 'query' param. Body is optional (for INSERT).
        params = f"{self._auth_params()}&query={sql}"
        url = f"{self._base_url}/?{params}"
        print(f"ClickHouseClient POST URL: {url}")  # Debugging line

        resp = await self._client.post(url, content=data)
        resp.raise_for_status()
        return resp

    # ---------- public API ----------

    async def execute(self, sql: str) -> str:
        """
        Run an arbitrary SQL statement and return raw text response.
        Good for SELECTs, SHOW TABLES, etc.
        """
        resp = await self._post(sql)
        return resp.text

    async def insert_json_each_row(
        self,
        table: str,
        rows: Iterable[Mapping[str, Any]],
    ) -> None:
        """
        Insert a collection of dicts into `table` using JSONEachRow.
        Column names should match keys in each dict.
        """
        sql = f"INSERT INTO {table} FORMAT JSONEachRow"
        payload = "\n".join(json.dumps(r) for r in rows)
        inser_reslut_from_client = await self._post(sql, data=payload)
        print("Insert response:", inser_reslut_from_client.text)

    async def ping(self) -> bool:
        """
        Simple healthcheck; returns True if SELECT 1 succeeds.
        """
        try:
            txt = await self.execute("SELECT 1")
            return txt.strip() == "1"
        except Exception:
            return False

    async def get_last_benchmarks(
        self,
        limit: int = 10,
    ) -> None:
        """
        Get the last few benchmarks from `table`.
        """
        sql = f"SELECT * FROM default.benchmark_results ORDER BY timestamp DESC LIMIT {limit}"
        payload = {"lim": limit}
        await self.execute(sql)
       