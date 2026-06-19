from __future__ import annotations

from typing import Any

from ._base import Resource

class BattlePassResource(Resource):
    def get(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Battle Pass content and rewards."""
        return self._t.request("GET", "/shop/battlepass", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncBattlePassResource(Resource):
    async def get(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Battle Pass content and rewards."""
        return await self._t.request("GET", "/shop/battlepass", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
