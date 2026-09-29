from __future__ import annotations

from typing import Any

from ._base import Resource

class PlaylistsResource(Resource):
    def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all playlists (game modes).

        ``GET /api/v2/playlists``
        """
        return self._t.request("GET", "/playlists", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_active(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active playlists.

        ``GET /api/v2/playlists/active``
        """
        return self._t.request("GET", "/playlists/active", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_by_id(self, playlist_id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a specific playlist by its ID.

        ``GET /api/v2/playlists/{playlistId}``
        """
        return self._t.request("GET", f"/playlists/{playlist_id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncPlaylistsResource(Resource):
    async def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all playlists (game modes).

        ``GET /api/v2/playlists``
        """
        return await self._t.request("GET", "/playlists", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_active(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active playlists.

        ``GET /api/v2/playlists/active``
        """
        return await self._t.request("GET", "/playlists/active", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_by_id(self, playlist_id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a specific playlist by its ID.

        ``GET /api/v2/playlists/{playlistId}``
        """
        return await self._t.request("GET", f"/playlists/{playlist_id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
