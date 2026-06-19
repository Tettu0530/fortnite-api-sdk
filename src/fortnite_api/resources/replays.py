from __future__ import annotations

from typing import Any

from ._base import Resource

class ReplaysResource(Resource):
    def download(self, match_id: str, *, fortnite_token: str | None = None) -> bytes:
        """Download a tournament .replay file by match ID."""
        return self._t.request_binary(f"/replays/{match_id}", "v1", fortnite_token=fortnite_token)

    def get_metadata(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the raw chunk manifest (metadata) for a tournament replay."""
        return self._t.request("GET", f"/replays/{match_id}/metadata", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and fully parse a tournament replay by match ID."""
        return self._t.request("GET", f"/replays/{match_id}/parse", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_broadcast(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — full broadcast payload."""
        return self._t.request("GET", f"/replays/{match_id}/parse/broadcast", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_lobby(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — full player lobby."""
        return self._t.request("GET", f"/replays/{match_id}/parse/lobby", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_loot(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — ground loot."""
        return self._t.request("GET", f"/replays/{match_id}/parse/loot", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_map(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — map context."""
        return self._t.request("GET", f"/replays/{match_id}/parse/map", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_stats(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — stats only."""
        return self._t.request("GET", f"/replays/{match_id}/parse/stats", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_timeline(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — match timeline."""
        return self._t.request("GET", f"/replays/{match_id}/parse/timeline", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def parse_zones(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — storm zones."""
        return self._t.request("GET", f"/replays/{match_id}/parse/zones", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncReplaysResource(Resource):
    async def download(self, match_id: str, *, fortnite_token: str | None = None) -> bytes:
        """Download a tournament .replay file by match ID."""
        return await self._t.request_binary(f"/replays/{match_id}", "v1", fortnite_token=fortnite_token)

    async def get_metadata(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the raw chunk manifest (metadata) for a tournament replay."""
        return await self._t.request("GET", f"/replays/{match_id}/metadata", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and fully parse a tournament replay by match ID."""
        return await self._t.request("GET", f"/replays/{match_id}/parse", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_broadcast(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — full broadcast payload."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/broadcast", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_lobby(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — full player lobby."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/lobby", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_loot(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — ground loot."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/loot", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_map(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — map context."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/map", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_stats(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — stats only."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/stats", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_timeline(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — match timeline."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/timeline", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def parse_zones(self, match_id: str, *, fortnite_token: str | None = None) -> Any:
        """Download and parse a tournament replay — storm zones."""
        return await self._t.request("GET", f"/replays/{match_id}/parse/zones", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
