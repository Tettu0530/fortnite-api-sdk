from __future__ import annotations

from typing import Any

from ..models import AllSpriteCollectionsResponseDto, AllSpritesResponseDto, PublishCollectionRequest, SharedSpriteCollectionDto, SpriteBoonDto, SpriteCollectionResponseDto, SpriteFamilyDto, SpriteSharePublishResultDto, SpriteVersionDto, SpritesResponseDto
from ._base import Resource

class SpritesResource(Resource):
    def get(self, *, search: str | None = None, rarity: str | None = None, variant: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpritesResponseDto:
        """Get the full sprite catalog: families with nested variants, current + PAK-base drop weights,
        normalized drop chances, rarity, icons, boons, the level-up XP curve, and alternate event weight
        sets.

        ``GET /api/v2/sprites``
        """
        return self._t.request("GET", "/sprites", "v2",
            params={"search": search, "rarity": rarity, "variant": variant, "version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=SpritesResponseDto)

    def get_all(self, *, search: str | None = None, rarity: str | None = None, variant: str | None = None, fortnite_token: str | None = None) -> AllSpritesResponseDto:
        """Every season's catalog in one call — the whole sprite archive, grouped by game version, current
        season first.

        ``GET /api/v2/sprites/all``
        """
        return self._t.request("GET", "/sprites/all", "v2",
            params={"search": search, "rarity": rarity, "variant": variant}, json_body=None, fortnite_token=fortnite_token,
            response_type=AllSpritesResponseDto)

    def get_versions(self, *, fortnite_token: str | None = None) -> list[SpriteVersionDto]:
        """Every archived sprite catalog version, newest first.

        ``GET /api/v2/sprites/versions``
        """
        return self._t.request("GET", "/sprites/versions", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[SpriteVersionDto])

    def get_boons(self, *, fortnite_token: str | None = None) -> list[SpriteBoonDto]:
        """Get all SpriteBoons perks with names and descriptions.

        ``GET /api/v2/sprites/boons``
        """
        return self._t.request("GET", "/sprites/boons", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[SpriteBoonDto])

    def get_by_id(self, id: str, *, fortnite_token: str | None = None) -> SpriteFamilyDto:
        """Get a single sprite family by family id, variant id, or name.

        ``GET /api/v2/sprites/{id}``
        """
        return self._t.request("GET", f"/sprites/{id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=SpriteFamilyDto)

    def get_collection(self, *, account_id: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpriteCollectionResponseDto:
        """Get the caller's own sprite collection — the catalog annotated with what they own, each variant
        carrying `owned`, `count`, `xp` and `mastered`, plus their equipped variant, starter sprite, season
        currency and a completion percentage.

        ``GET /api/v2/sprites/collection``
        """
        return self._t.request("GET", "/sprites/collection", "v2",
            params={"accountId": account_id, "version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=SpriteCollectionResponseDto)

    def get_all_collections(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> AllSpriteCollectionsResponseDto:
        """The caller's collection across EVERY season in one call — each season's catalog annotated with what
        they own, plus cumulative cross-season totals.

        ``GET /api/v2/sprites/collection/all``
        """
        return self._t.request("GET", "/sprites/collection/all", "v2",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=AllSpriteCollectionsResponseDto)

    def publish_collection(self, *, body: PublishCollectionRequest | dict[str, Any] | None = None, fortnite_token: str | None = None) -> SpriteSharePublishResultDto:
        """Publish (or refresh) the caller's OWN collection so others can view it — this is the opt-in basis
        for "see another player's collection". Requires the caller's own `x-fortnite-token`; the share is
        keyed to the account that token verifies as, so no one can publish on another account's behalf.

        ``POST /api/v2/sprites/collection/publish``
        """
        return self._t.request("POST", "/sprites/collection/publish", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=SpriteSharePublishResultDto)

    def unpublish_collection(self, *, fortnite_token: str | None = None) -> Any:
        """Remove the caller's shared collection (verified from their own token).

        ``DELETE /api/v2/sprites/collection/publish``
        """
        return self._t.request("DELETE", "/sprites/collection/publish", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_shared_collection(self, account_id_or_name: str, *, fortnite_token: str | None = None) -> SharedSpriteCollectionDto:
        """Get another player's opt-in shared collection by Epic account id or display name. Only returns
        collections the owner has published: public shares resolve by name or id, unlisted shares only by
        exact account id, and private/never-published resolve to 404. No Epic token is required and none of
        the target player's credentials are used.

        ``GET /api/v2/sprites/collection/shared/{accountIdOrName}``
        """
        return self._t.request("GET", f"/sprites/collection/shared/{account_id_or_name}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=SharedSpriteCollectionDto)


class AsyncSpritesResource(Resource):
    async def get(self, *, search: str | None = None, rarity: str | None = None, variant: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpritesResponseDto:
        """Get the full sprite catalog: families with nested variants, current + PAK-base drop weights,
        normalized drop chances, rarity, icons, boons, the level-up XP curve, and alternate event weight
        sets.

        ``GET /api/v2/sprites``
        """
        return await self._t.request("GET", "/sprites", "v2",
            params={"search": search, "rarity": rarity, "variant": variant, "version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=SpritesResponseDto)

    async def get_all(self, *, search: str | None = None, rarity: str | None = None, variant: str | None = None, fortnite_token: str | None = None) -> AllSpritesResponseDto:
        """Every season's catalog in one call — the whole sprite archive, grouped by game version, current
        season first.

        ``GET /api/v2/sprites/all``
        """
        return await self._t.request("GET", "/sprites/all", "v2",
            params={"search": search, "rarity": rarity, "variant": variant}, json_body=None, fortnite_token=fortnite_token,
            response_type=AllSpritesResponseDto)

    async def get_versions(self, *, fortnite_token: str | None = None) -> list[SpriteVersionDto]:
        """Every archived sprite catalog version, newest first.

        ``GET /api/v2/sprites/versions``
        """
        return await self._t.request("GET", "/sprites/versions", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[SpriteVersionDto])

    async def get_boons(self, *, fortnite_token: str | None = None) -> list[SpriteBoonDto]:
        """Get all SpriteBoons perks with names and descriptions.

        ``GET /api/v2/sprites/boons``
        """
        return await self._t.request("GET", "/sprites/boons", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=list[SpriteBoonDto])

    async def get_by_id(self, id: str, *, fortnite_token: str | None = None) -> SpriteFamilyDto:
        """Get a single sprite family by family id, variant id, or name.

        ``GET /api/v2/sprites/{id}``
        """
        return await self._t.request("GET", f"/sprites/{id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=SpriteFamilyDto)

    async def get_collection(self, *, account_id: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpriteCollectionResponseDto:
        """Get the caller's own sprite collection — the catalog annotated with what they own, each variant
        carrying `owned`, `count`, `xp` and `mastered`, plus their equipped variant, starter sprite, season
        currency and a completion percentage.

        ``GET /api/v2/sprites/collection``
        """
        return await self._t.request("GET", "/sprites/collection", "v2",
            params={"accountId": account_id, "version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=SpriteCollectionResponseDto)

    async def get_all_collections(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> AllSpriteCollectionsResponseDto:
        """The caller's collection across EVERY season in one call — each season's catalog annotated with what
        they own, plus cumulative cross-season totals.

        ``GET /api/v2/sprites/collection/all``
        """
        return await self._t.request("GET", "/sprites/collection/all", "v2",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=AllSpriteCollectionsResponseDto)

    async def publish_collection(self, *, body: PublishCollectionRequest | dict[str, Any] | None = None, fortnite_token: str | None = None) -> SpriteSharePublishResultDto:
        """Publish (or refresh) the caller's OWN collection so others can view it — this is the opt-in basis
        for "see another player's collection". Requires the caller's own `x-fortnite-token`; the share is
        keyed to the account that token verifies as, so no one can publish on another account's behalf.

        ``POST /api/v2/sprites/collection/publish``
        """
        return await self._t.request("POST", "/sprites/collection/publish", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=SpriteSharePublishResultDto)

    async def unpublish_collection(self, *, fortnite_token: str | None = None) -> Any:
        """Remove the caller's shared collection (verified from their own token).

        ``DELETE /api/v2/sprites/collection/publish``
        """
        return await self._t.request("DELETE", "/sprites/collection/publish", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_shared_collection(self, account_id_or_name: str, *, fortnite_token: str | None = None) -> SharedSpriteCollectionDto:
        """Get another player's opt-in shared collection by Epic account id or display name. Only returns
        collections the owner has published: public shares resolve by name or id, unlisted shares only by
        exact account id, and private/never-published resolve to 404. No Epic token is required and none of
        the target player's credentials are used.

        ``GET /api/v2/sprites/collection/shared/{accountIdOrName}``
        """
        return await self._t.request("GET", f"/sprites/collection/shared/{account_id_or_name}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=SharedSpriteCollectionDto)
