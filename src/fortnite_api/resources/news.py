from __future__ import annotations

from typing import Any

from ._base import Resource

class NewsResource(Resource):
    def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all in-game news across all modes."""
        return self._t.request("GET", "/news", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_br(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Battle Royale news."""
        return self._t.request("GET", "/news/br", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_creative(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Creative mode news."""
        return self._t.request("GET", "/news/creative", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_stw(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Save the World news."""
        return self._t.request("GET", "/news/stw", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncNewsResource(Resource):
    async def get_all(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all in-game news across all modes."""
        return await self._t.request("GET", "/news", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_br(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Battle Royale news."""
        return await self._t.request("GET", "/news/br", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_creative(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Creative mode news."""
        return await self._t.request("GET", "/news/creative", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_stw(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get Save the World news."""
        return await self._t.request("GET", "/news/stw", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
