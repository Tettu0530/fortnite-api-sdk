from __future__ import annotations

import warnings
from typing import Any

from ..models import BattlePassCatalog, BattlePassSeasonDto
from ._base import Resource

class BattlePassResource(Resource):
    def get(self, *, season: int | None = None, fortnite_token: str | None = None) -> BattlePassCatalog:
        """The current battle pass, or an archived one via `?season=`.

        ``GET /api/v2/battlepass``
        """
        return self._t.request("GET", "/battlepass", "v2",
            params={"season": season}, json_body=None, fortnite_token=fortnite_token,
            response_type=BattlePassCatalog)

    def get_seasons(self, *, fortnite_token: str | None = None) -> list[BattlePassSeasonDto]:
        """Every season we hold a pass for, newest first.

        ``GET /api/v2/battlepass/seasons``
        """
        return self._t.request("GET", "/battlepass/seasons", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[BattlePassSeasonDto])

    def get_legacy(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Deprecated: despite its name this never returned the Battle Pass.

        ``GET /api/v1/shop/battlepass``

        .. deprecated::
            This endpoint is marked as deprecated by the API.
            Use battlepass.get() (GET /api/v2/battlepass) instead.
        """
        warnings.warn(
            'battlepass.get_legacy() calls GET /api/v1/shop/battlepass, which is deprecated by the API. Use battlepass.get() (GET /api/v2/battlepass) instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return self._t.request("GET", "/shop/battlepass", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncBattlePassResource(Resource):
    async def get(self, *, season: int | None = None, fortnite_token: str | None = None) -> BattlePassCatalog:
        """The current battle pass, or an archived one via `?season=`.

        ``GET /api/v2/battlepass``
        """
        return await self._t.request("GET", "/battlepass", "v2",
            params={"season": season}, json_body=None, fortnite_token=fortnite_token,
            response_type=BattlePassCatalog)

    async def get_seasons(self, *, fortnite_token: str | None = None) -> list[BattlePassSeasonDto]:
        """Every season we hold a pass for, newest first.

        ``GET /api/v2/battlepass/seasons``
        """
        return await self._t.request("GET", "/battlepass/seasons", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[BattlePassSeasonDto])

    async def get_legacy(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Deprecated: despite its name this never returned the Battle Pass.

        ``GET /api/v1/shop/battlepass``

        .. deprecated::
            This endpoint is marked as deprecated by the API.
            Use battlepass.get() (GET /api/v2/battlepass) instead.
        """
        warnings.warn(
            'battlepass.get_legacy() calls GET /api/v1/shop/battlepass, which is deprecated by the API. Use battlepass.get() (GET /api/v2/battlepass) instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return await self._t.request("GET", "/shop/battlepass", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
