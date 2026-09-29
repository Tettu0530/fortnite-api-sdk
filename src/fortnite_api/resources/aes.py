from __future__ import annotations

from typing import Any

from ._base import Resource

class AesResource(Resource):
    def get_keys(self, *, fortnite_token: str | None = None) -> Any:
        """Current AES main key and dynamic pak keys.

        ``GET /api/v1/aes``
        """
        return self._t.request("GET", "/aes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Every build whose AES keys and mappings we hold.

        ``GET /api/v1/aes/history``
        """
        return self._t.request("GET", "/aes/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_mappings(self, *, fortnite_token: str | None = None) -> Any:
        """Current .usmap mappings download URLs.

        ``GET /api/v1/mappings``
        """
        return self._t.request("GET", "/mappings", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncAesResource(Resource):
    async def get_keys(self, *, fortnite_token: str | None = None) -> Any:
        """Current AES main key and dynamic pak keys.

        ``GET /api/v1/aes``
        """
        return await self._t.request("GET", "/aes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_history(self, *, fortnite_token: str | None = None) -> Any:
        """Every build whose AES keys and mappings we hold.

        ``GET /api/v1/aes/history``
        """
        return await self._t.request("GET", "/aes/history", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_mappings(self, *, fortnite_token: str | None = None) -> Any:
        """Current .usmap mappings download URLs.

        ``GET /api/v1/mappings``
        """
        return await self._t.request("GET", "/mappings", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
