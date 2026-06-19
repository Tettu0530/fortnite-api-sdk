from __future__ import annotations

from ..models import MapDataDto, MapHistoryEntryDto
from ._base import Resource

class MapResource(Resource):
    def get(self, *, version: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> MapDataDto:
        """Get map data including POIs and minimap metadata for a given version."""
        return self._t.request("GET", "/map", "v1",
            params={"version": version, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=MapDataDto, is_list=False)

    def get_history(self, *, chapter: int | None = None, season: int | None = None, fortnite_token: str | None = None) -> list[MapHistoryEntryDto]:
        """Get map history entries, optionally filtered by chapter and/or season."""
        return self._t.request("GET", "/map/history", "v1",
            params={"chapter": chapter, "season": season}, json_body=None, fortnite_token=fortnite_token,
            model=MapHistoryEntryDto, is_list=True)

    def get_image(self, *, version: str | None = None, fortnite_token: str | None = None) -> str | None:
        """Redirects to the raw map image on GitHub for a given version."""
        return self._t.request_redirect("/map/image", "v1", params={"version": version}, fortnite_token=fortnite_token)


class AsyncMapResource(Resource):
    async def get(self, *, version: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> MapDataDto:
        """Get map data including POIs and minimap metadata for a given version."""
        return await self._t.request("GET", "/map", "v1",
            params={"version": version, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=MapDataDto, is_list=False)

    async def get_history(self, *, chapter: int | None = None, season: int | None = None, fortnite_token: str | None = None) -> list[MapHistoryEntryDto]:
        """Get map history entries, optionally filtered by chapter and/or season."""
        return await self._t.request("GET", "/map/history", "v1",
            params={"chapter": chapter, "season": season}, json_body=None, fortnite_token=fortnite_token,
            model=MapHistoryEntryDto, is_list=True)

    async def get_image(self, *, version: str | None = None, fortnite_token: str | None = None) -> str | None:
        """Redirects to the raw map image on GitHub for a given version."""
        return await self._t.request_redirect("/map/image", "v1", params={"version": version}, fortnite_token=fortnite_token)
