from __future__ import annotations

from ..models import ShopResponseDto
from ._base import Resource

class ShopResource(Resource):
    def get_current(self, *, type: str | None = None, section: str | None = None, rarity: str | None = None, search: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> ShopResponseDto:
        """Get the current Item Shop."""
        return self._t.request("GET", "/shop", "v1",
            params={"type": type, "section": section, "rarity": rarity, "search": search, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=ShopResponseDto, is_list=False)


class AsyncShopResource(Resource):
    async def get_current(self, *, type: str | None = None, section: str | None = None, rarity: str | None = None, search: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> ShopResponseDto:
        """Get the current Item Shop."""
        return await self._t.request("GET", "/shop", "v1",
            params={"type": type, "section": section, "rarity": rarity, "search": search, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=ShopResponseDto, is_list=False)
