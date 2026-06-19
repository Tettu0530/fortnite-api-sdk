from __future__ import annotations

from typing import Any

from ._base import Resource

class CrewResource(Resource):
    def get_current(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite Crew pack."""
        return self._t.request("GET", "/crew/current", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Get the history of past Fortnite Crew packs."""
        return self._t.request("GET", "/crew/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncCrewResource(Resource):
    async def get_current(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite Crew pack."""
        return await self._t.request("GET", "/crew/current", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Get the history of past Fortnite Crew packs."""
        return await self._t.request("GET", "/crew/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
