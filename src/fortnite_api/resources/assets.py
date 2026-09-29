from __future__ import annotations

from typing import Any

from ._base import Resource

class AssetsResource(Resource):
    def get_shop_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get shop asset bundles.

        ``GET /api/v1/assets/bundles/shop``
        """
        return self._t.request("GET", "/assets/bundles/shop", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_tournament_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get tournament asset bundles (images, icons, rewards).

        ``GET /api/v1/assets/bundles/tournaments``
        """
        return self._t.request("GET", "/assets/bundles/tournaments", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncAssetsResource(Resource):
    async def get_shop_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get shop asset bundles.

        ``GET /api/v1/assets/bundles/shop``
        """
        return await self._t.request("GET", "/assets/bundles/shop", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_tournament_bundles(self, *, fortnite_token: str | None = None) -> Any:
        """Get tournament asset bundles (images, icons, rewards).

        ``GET /api/v1/assets/bundles/tournaments``
        """
        return await self._t.request("GET", "/assets/bundles/tournaments", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
