from __future__ import annotations

from typing import Any

from ._base import Resource

class StatsResource(Resource):
    def get_bulk(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Get stats for multiple players in one request."""
        return self._t.request("POST", "/stats/bulk", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_leaderboard(self, stat: str, *, limit: int | None = None, offset: int | None = None, window: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the global leaderboard for a specific stat."""
        return self._t.request("GET", f"/stats/leaderboard/{stat}", "v2",
            params={"limit": limit, "offset": offset, "window": window}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get(self, account_id: str, *, start_time: str | None = None, end_time: str | None = None, stats: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get stats for a single player by Epic account ID."""
        return self._t.request("GET", f"/stats/{account_id}", "v2",
            params={"startTime": start_time, "endTime": end_time, "stats": stats}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncStatsResource(Resource):
    async def get_bulk(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Get stats for multiple players in one request."""
        return await self._t.request("POST", "/stats/bulk", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_leaderboard(self, stat: str, *, limit: int | None = None, offset: int | None = None, window: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the global leaderboard for a specific stat."""
        return await self._t.request("GET", f"/stats/leaderboard/{stat}", "v2",
            params={"limit": limit, "offset": offset, "window": window}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get(self, account_id: str, *, start_time: str | None = None, end_time: str | None = None, stats: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get stats for a single player by Epic account ID."""
        return await self._t.request("GET", f"/stats/{account_id}", "v2",
            params={"startTime": start_time, "endTime": end_time, "stats": stats}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
