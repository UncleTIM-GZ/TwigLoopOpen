"""Async ClickHouse client using the HTTP interface."""

import json

import httpx
from shared_config import ClickHouseSettings


class ClickHouseClient:
    """Lightweight async ClickHouse client over HTTP.

    Uses the ClickHouse HTTP interface with ``httpx``.
    Designed for analytics writes (event ingestion) and simple reads.
    """

    def __init__(self, settings: ClickHouseSettings) -> None:
        self._base_url = f"http://{settings.clickhouse_host}:{settings.clickhouse_http_port}"
        self._db = settings.clickhouse_db
        self._auth = (settings.clickhouse_user, settings.clickhouse_password)

    async def execute(self, query: str, params: dict[str, object] | None = None) -> str:
        """Execute a query and return the raw response text.

        Args:
            query: SQL query string.
            params: Optional query parameters forwarded as URL params.

        Returns:
            Raw response body from ClickHouse.
        """
        url_params: dict[str, str] = {"database": self._db, "query": query}
        if params:
            url_params.update({k: str(v) for k, v in params.items()})

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            response = await client.post(
                self._base_url,
                params=url_params,
                auth=self._auth,
            )
            response.raise_for_status()
            return response.text

    async def insert_json(self, table: str, rows: list[dict[str, object]]) -> None:
        """Insert rows using JSONEachRow format.

        Args:
            table: Target table name (without database prefix).
            rows: List of dicts, each representing one row.
        """
        if not rows:
            return

        body = "\n".join(json.dumps(row) for row in rows)
        query = f"INSERT INTO {table} FORMAT JSONEachRow"

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
            response = await client.post(
                self._base_url,
                params={"database": self._db, "query": query},
                content=body.encode(),
                headers={"Content-Type": "application/json"},
                auth=self._auth,
            )
            response.raise_for_status()
