from __future__ import annotations

from typing import Any

from ._base import Resource

class AssetsResource(Resource):
    def get_shop_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get shop asset bundles."""
        return self._t.request("GET", "/assets/bundles/shop", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_tournament_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get tournament asset bundles (images, icons, rewards)."""
        return self._t.request("GET", "/assets/bundles/tournaments", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncAssetsResource(Resource):
    async def get_shop_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get shop asset bundles."""
        return await self._t.request("GET", "/assets/bundles/shop", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_tournament_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get tournament asset bundles (images, icons, rewards)."""
        return await self._t.request("GET", "/assets/bundles/tournaments", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
