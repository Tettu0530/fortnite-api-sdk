from __future__ import annotations

from typing import Any

from ..models import PatchInfoDto, RarityDefinitionDto, WeaponListItemDto
from ._base import Resource

class WeaponsResource(Resource):
    def get(self, *, patch: str | None = None, category: str | None = None, search: str | None = None, rarity: str | None = None, type: str | None = None, ammo_type: str | None = None, gamemode: str | None = None, item_type: str | None = None, lang: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, fortnite_token: str | None = None) -> list[WeaponListItemDto]:
        """Get weapons for a given patch, with optional filters.

        ``GET /api/v2/weapons``
        """
        return self._t.request("GET", "/weapons", "v2",
            params={"patch": patch, "category": category, "search": search, "rarity": rarity, "type": type, "ammoType": ammo_type, "gamemode": gamemode, "itemType": item_type, "lang": lang, "major": major, "minor": minor, "date": date, "secondary": secondary}, json_body=None, fortnite_token=fortnite_token,
            response_type=list[WeaponListItemDto])

    def get_by_id(self, id: str, *, major: int | None = None, minor: int | None = None, date: str | None = None, fortnite_token: str | None = None) -> WeaponListItemDto:
        """Get a single weapon by its WID (e.g. WID_Assault_...) with full stats.

        ``GET /api/v2/weapons/{id}``
        """
        return self._t.request("GET", f"/weapons/{id}", "v2",
            params={"major": major, "minor": minor, "date": date}, json_body=None, fortnite_token=fortnite_token,
            response_type=WeaponListItemDto)

    def get_lootpool(self, *, gamemode: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, with_stats: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get the resolved loot pool for a gamemode: one entry per item with per-container chances (P(item |
        one roll of that container)) and the underlying per-drop-list rows under `sources`, self-extracted
        from game data + live hotfixes.

        ``GET /api/v2/weapons/lootpool``
        """
        return self._t.request("GET", "/weapons/lootpool", "v2",
            params={"gamemode": gamemode, "major": major, "minor": minor, "date": date, "secondary": secondary, "withStats": with_stats}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_patches(self, *, fortnite_token: str | None = None) -> list[PatchInfoDto]:
        """Get all available weapon patches, with the current patch flagged.

        ``GET /api/v2/weapons/patches``
        """
        return self._t.request("GET", "/weapons/patches", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[PatchInfoDto])

    def get_rarities(self, *, fortnite_token: str | None = None) -> list[RarityDefinitionDto]:
        """Get rarity definitions and their display colors.

        ``GET /api/v2/weapons/rarity``
        """
        return self._t.request("GET", "/weapons/rarity", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[RarityDefinitionDto])


class AsyncWeaponsResource(Resource):
    async def get(self, *, patch: str | None = None, category: str | None = None, search: str | None = None, rarity: str | None = None, type: str | None = None, ammo_type: str | None = None, gamemode: str | None = None, item_type: str | None = None, lang: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, fortnite_token: str | None = None) -> list[WeaponListItemDto]:
        """Get weapons for a given patch, with optional filters.

        ``GET /api/v2/weapons``
        """
        return await self._t.request("GET", "/weapons", "v2",
            params={"patch": patch, "category": category, "search": search, "rarity": rarity, "type": type, "ammoType": ammo_type, "gamemode": gamemode, "itemType": item_type, "lang": lang, "major": major, "minor": minor, "date": date, "secondary": secondary}, json_body=None, fortnite_token=fortnite_token,
            response_type=list[WeaponListItemDto])

    async def get_by_id(self, id: str, *, major: int | None = None, minor: int | None = None, date: str | None = None, fortnite_token: str | None = None) -> WeaponListItemDto:
        """Get a single weapon by its WID (e.g. WID_Assault_...) with full stats.

        ``GET /api/v2/weapons/{id}``
        """
        return await self._t.request("GET", f"/weapons/{id}", "v2",
            params={"major": major, "minor": minor, "date": date}, json_body=None, fortnite_token=fortnite_token,
            response_type=WeaponListItemDto)

    async def get_lootpool(self, *, gamemode: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, with_stats: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get the resolved loot pool for a gamemode: one entry per item with per-container chances (P(item |
        one roll of that container)) and the underlying per-drop-list rows under `sources`, self-extracted
        from game data + live hotfixes.

        ``GET /api/v2/weapons/lootpool``
        """
        return await self._t.request("GET", "/weapons/lootpool", "v2",
            params={"gamemode": gamemode, "major": major, "minor": minor, "date": date, "secondary": secondary, "withStats": with_stats}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_patches(self, *, fortnite_token: str | None = None) -> list[PatchInfoDto]:
        """Get all available weapon patches, with the current patch flagged.

        ``GET /api/v2/weapons/patches``
        """
        return await self._t.request("GET", "/weapons/patches", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[PatchInfoDto])

    async def get_rarities(self, *, fortnite_token: str | None = None) -> list[RarityDefinitionDto]:
        """Get rarity definitions and their display colors.

        ``GET /api/v2/weapons/rarity``
        """
        return await self._t.request("GET", "/weapons/rarity", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[RarityDefinitionDto])
