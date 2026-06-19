from __future__ import annotations

from ..models import CosmeticDto, CosmeticDtoPaginatedResultDto
from ._base import Resource

class CosmeticsResource(Resource):
    def get_all(self, *, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, search: str | None = None, season: str | None = None, chapter: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return self._t.request("GET", "/cosmetics/all", "v2",
            params={"page": page, "pageSize": page_size, "type": type, "rarity": rarity, "set": set, "search": search, "season": season, "chapter": chapter, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    def get_new(self, *, page: int | None = None, page_size: int | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return self._t.request("GET", "/cosmetics/new", "v2",
            params={"page": page, "pageSize": page_size, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    def search(self, q: str, *, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return self._t.request("GET", "/cosmetics/search", "v2",
            params={"q": q, "page": page, "pageSize": page_size, "type": type, "rarity": rarity, "set": set, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    def get_by_id(self, id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDto:
        return self._t.request("GET", f"/cosmetics/{id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDto, is_list=False)


class AsyncCosmeticsResource(Resource):
    async def get_all(self, *, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, search: str | None = None, season: str | None = None, chapter: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return await self._t.request("GET", "/cosmetics/all", "v2",
            params={"page": page, "pageSize": page_size, "type": type, "rarity": rarity, "set": set, "search": search, "season": season, "chapter": chapter, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    async def get_new(self, *, page: int | None = None, page_size: int | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return await self._t.request("GET", "/cosmetics/new", "v2",
            params={"page": page, "pageSize": page_size, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    async def search(self, q: str, *, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto:
        return await self._t.request("GET", "/cosmetics/search", "v2",
            params={"q": q, "page": page, "pageSize": page_size, "type": type, "rarity": rarity, "set": set, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDtoPaginatedResultDto, is_list=False)

    async def get_by_id(self, id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDto:
        return await self._t.request("GET", f"/cosmetics/{id}", "v2",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=CosmeticDto, is_list=False)
