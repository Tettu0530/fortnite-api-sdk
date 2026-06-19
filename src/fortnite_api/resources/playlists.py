from __future__ import annotations

from typing import Any

from ._base import Resource

class PlaylistsResource(Resource):
    def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all playlists (game modes)."""
        return self._t.request("GET", "/playlists", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_active(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active playlists."""
        return self._t.request("GET", "/playlists/active", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_by_id(self, playlist_id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a specific playlist by its ID."""
        return self._t.request("GET", f"/playlists/{playlist_id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncPlaylistsResource(Resource):
    async def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all playlists (game modes)."""
        return await self._t.request("GET", "/playlists", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_active(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active playlists."""
        return await self._t.request("GET", "/playlists/active", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_by_id(self, playlist_id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a specific playlist by its ID."""
        return await self._t.request("GET", f"/playlists/{playlist_id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
