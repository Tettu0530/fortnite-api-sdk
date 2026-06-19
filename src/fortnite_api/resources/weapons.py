from __future__ import annotations

from ..models import PatchInfoDto, RarityDefinitionDto, WeaponListItemDto
from ._base import Resource

class WeaponsResource(Resource):
    def get(self, *, patch: str | None = None, category: str | None = None, search: str | None = None, rarity: str | None = None, type: str | None = None, ammo_type: str | None = None, gamemode: str | None = None, item_type: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> list[WeaponListItemDto]:
        """Get weapons for a given patch, with optional filters."""
        return self._t.request("GET", "/weapons", "v2",
            params={"patch": patch, "category": category, "search": search, "rarity": rarity, "type": type, "ammoType": ammo_type, "gamemode": gamemode, "itemType": item_type, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=WeaponListItemDto, is_list=True)

    def get_patches(self, *, fortnite_token: str | None = None) -> list[PatchInfoDto]:
        """Get all available weapon patches, with the current patch flagged."""
        return self._t.request("GET", "/weapons/patches", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=PatchInfoDto, is_list=True)

    def get_rarities(self, *, fortnite_token: str | None = None) -> list[RarityDefinitionDto]:
        """Get rarity definitions and their display colors."""
        return self._t.request("GET", "/weapons/rarity", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=RarityDefinitionDto, is_list=True)


class AsyncWeaponsResource(Resource):
    async def get(self, *, patch: str | None = None, category: str | None = None, search: str | None = None, rarity: str | None = None, type: str | None = None, ammo_type: str | None = None, gamemode: str | None = None, item_type: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> list[WeaponListItemDto]:
        """Get weapons for a given patch, with optional filters."""
        return await self._t.request("GET", "/weapons", "v2",
            params={"patch": patch, "category": category, "search": search, "rarity": rarity, "type": type, "ammoType": ammo_type, "gamemode": gamemode, "itemType": item_type, "lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=WeaponListItemDto, is_list=True)

    async def get_patches(self, *, fortnite_token: str | None = None) -> list[PatchInfoDto]:
        """Get all available weapon patches, with the current patch flagged."""
        return await self._t.request("GET", "/weapons/patches", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=PatchInfoDto, is_list=True)

    async def get_rarities(self, *, fortnite_token: str | None = None) -> list[RarityDefinitionDto]:
        """Get rarity definitions and their display colors."""
        return await self._t.request("GET", "/weapons/rarity", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=RarityDefinitionDto, is_list=True)
