from __future__ import annotations

from typing import Any

from ._base import Resource

class CrewResource(Resource):
    def get_current(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite Crew pack.

        ``GET /api/v1/crew/current``
        """
        return self._t.request("GET", "/crew/current", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Get the history of past Fortnite Crew packs.

        ``GET /api/v1/crew/history``
        """
        return self._t.request("GET", "/crew/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncCrewResource(Resource):
    async def get_current(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite Crew pack.

        ``GET /api/v1/crew/current``
        """
        return await self._t.request("GET", "/crew/current", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Get the history of past Fortnite Crew packs.

        ``GET /api/v1/crew/history``
        """
        return await self._t.request("GET", "/crew/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
