from __future__ import annotations

from typing import Any

from ._base import Resource

class AesResource(Resource):
    def get_keys(self, *, fortnite_token: str | None = None) -> Any:
        """Current AES main key and dynamic pak keys."""
        return self._t.request("GET", "/aes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_mappings(self, *, fortnite_token: str | None = None) -> Any:
        """Current .usmap mappings download URLs."""
        return self._t.request("GET", "/mappings", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncAesResource(Resource):
    async def get_keys(self, *, fortnite_token: str | None = None) -> Any:
        """Current AES main key and dynamic pak keys."""
        return await self._t.request("GET", "/aes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_mappings(self, *, fortnite_token: str | None = None) -> Any:
        """Current .usmap mappings download URLs."""
        return await self._t.request("GET", "/mappings", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
