# Catalog resources: shop, cosmetics, weapons, map, news, playlists, calendar, battlepass, sprites, aes, assets, crew

Static and semi-static game data. Almost none of it needs a user token - only the sprite
*collection* methods act on a specific player.

Signatures, return types, HTTP paths and descriptions below are extracted from the SDK source
(`fortnite_api/resources/*.py`); only the guidance section is hand-written. All methods exist with
the same signature on `AsyncFortniteAPI` (add `await`). "Token:" lines appear only where the API
description states something about `x-fortnite-token`. "Plans:" lines come from the `x-plans`
extension of the bundled OpenAPI spec (which api-fortnite.com plans may call the endpoint).

## Guidance

- **Item shop:** `shop.get_current()` returns `ShopResponseDto`. Offers live in
  `shop.storefronts[*].catalog_entries[*]` (`ShopCatalogEntryDto`: `title`, `dev_name`,
  `section_display_name`, `prices[*].final_price` / `regular_price` / `currency_type`,
  `item_grants[*].template_id` and `.cosmetic`). Filter server-side with `type=`, `section=`,
  `rarity=`, `search=`, `lang=`.
- **Cosmetics:** `get_all` / `get_new` / `search` are paginated (`page`, `page_size`, `total`,
  `total_pages`, `data: list[CosmeticDto]`). `get_all(season=, chapter=)` take `int`.
  `search(q, ...)` takes the query positionally.
- **Weapons:** `weapons.get()` returns `list[WeaponListItemDto]`; pin a patch with `major=` /
  `minor=` or `date=`. `stats` and `images` on the weapon are untyped (`Any`) - key access.
- **Map:** `map.get_image()` returns the resolved image **URL string** (or `None`), not bytes -
  download it yourself if you need the file. `mode=` is `"br"` (default), `"og"` or
  `"rotating:<codename>"`.
- **Battle Pass:** use `battlepass.get(season=...)` (v2, `BattlePassCatalog`) and
  `battlepass.get_seasons()` (`list[BattlePassSeasonDto]`, has `is_current`).
  `battlepass.get_legacy()` is deprecated.
- **Season dates:** `calendar.get_season()` -> `SeasonEntryDto` (`season_number`,
  `season_date_begin`, `season_date_end`).
- **Untyped here:** `playlists.*`, `aes.*`, `assets.*`, `crew.*`, `battlepass.get_legacy`,
  `sprites.unpublish_collection` return raw JSON.

## Contents

- [`client.shop`](#clientshop)
- [`client.cosmetics`](#clientcosmetics)
- [`client.weapons`](#clientweapons)
- [`client.map`](#clientmap)
- [`client.news`](#clientnews)
- [`client.playlists`](#clientplaylists)
- [`client.calendar`](#clientcalendar)
- [`client.battlepass`](#clientbattlepass)
- [`client.sprites`](#clientsprites)
- [`client.aes`](#clientaes)
- [`client.assets`](#clientassets)
- [`client.crew`](#clientcrew)

## `client.shop`

### `client.shop.get_current(*, type: str | None = None, section: str | None = None, rarity: str | None = None, search: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> ShopResponseDto`

- HTTP: `GET /api/v1/shop`
- Plans: `free`, `pro`, `custom`
- Get the current Item Shop.
- `ShopResponseDto` fields: `refresh_interval_hrs` (refreshIntervalHrs): `float | None`, `daily_purchase_hrs` (dailyPurchaseHrs): `float | None`, `expiration`: `str | None`, `storefronts`: `list[ShopStorefrontDto] | None`

```python
result = client.shop.get_current()
print(result.refresh_interval_hrs)
```

## `client.cosmetics`

### `client.cosmetics.get_all(*, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, search: str | None = None, season: int | None = None, chapter: int | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto`

- HTTP: `GET /api/v2/cosmetics/all`
- Plans: `pro`, `custom`
- `CosmeticDtoPaginatedResultDto` fields: `page`: `int | None`, `page_size` (pageSize): `int | None`, `total`: `int | None`, `total_pages` (totalPages): `int | None`, `data`: `list[CosmeticDto] | None`

```python
result = client.cosmetics.get_all()
print(result.page)
```

### `client.cosmetics.get_new(*, page: int | None = None, page_size: int | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto`

- HTTP: `GET /api/v2/cosmetics/new`
- Plans: `pro`, `custom`
- `CosmeticDtoPaginatedResultDto` fields: `page`: `int | None`, `page_size` (pageSize): `int | None`, `total`: `int | None`, `total_pages` (totalPages): `int | None`, `data`: `list[CosmeticDto] | None`

```python
result = client.cosmetics.get_new()
print(result.page)
```

### `client.cosmetics.search(q: str, *, page: int | None = None, page_size: int | None = None, type: str | None = None, rarity: str | None = None, set: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDtoPaginatedResultDto`

- HTTP: `GET /api/v2/cosmetics/search`
- Plans: `pro`, `custom`
- `CosmeticDtoPaginatedResultDto` fields: `page`: `int | None`, `page_size` (pageSize): `int | None`, `total`: `int | None`, `total_pages` (totalPages): `int | None`, `data`: `list[CosmeticDto] | None`

```python
result = client.cosmetics.search("<q>")
print(result.page)
```

### `client.cosmetics.get_by_id(id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> CosmeticDto`

- HTTP: `GET /api/v2/cosmetics/{id}`
- Plans: `pro`, `custom`
- `CosmeticDto` fields: `id`: `str | None`, `type`: `str | None`, `name`: `str | None`, `description`: `str | None`, `rarity`: `str | None`, `series`: `str | None`, `set`: `str | None`, `icon`: `str | None`, `introduction`: `CosmeticIntroductionDto | None`, `images`: `CosmeticImagesDto | None`, `tags`: `list[str] | None`, `weapon_actor_class` (weaponActorClass): `str | None`

```python
result = client.cosmetics.get_by_id("<id>")
print(result.id)
```

## `client.weapons`

### `client.weapons.get(*, patch: str | None = None, category: str | None = None, search: str | None = None, rarity: str | None = None, type: str | None = None, ammo_type: str | None = None, gamemode: str | None = None, item_type: str | None = None, lang: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, fortnite_token: str | None = None) -> list[WeaponListItemDto]`

- HTTP: `GET /api/v2/weapons`
- Plans: `pro`, `custom`
- Get weapons for a given patch, with optional filters.
- `WeaponListItemDto` fields: `id`: `str | None`, `display_name` (displayName): `str | None`, `description`: `str | None`, `rarity`: `str | None`, `type`: `str | None`, `category`: `str | None`, `ammo_type` (ammoType): `str | None`, `trigger_type` (triggerType): `str | None`, `search_tags` (searchTags): `str | None`, `in_current_loot_pool` (inCurrentLootPool): `bool | None`, `item_type` (itemType): `str | None`, `gamemodes`: `list[str] | None`, `patch`: `str | None`, `tags`: `list[str] | None`, `weapon_actor_class` (weaponActorClass): `str | None`, `stats`: `Any | None`, `images`: `Any | None`

```python
result = client.weapons.get()
first = result[0].id if result else None
```

### `client.weapons.get_by_id(id: str, *, major: int | None = None, minor: int | None = None, date: str | None = None, fortnite_token: str | None = None) -> WeaponListItemDto`

- HTTP: `GET /api/v2/weapons/{id}`
- Plans: `pro`, `custom`
- Get a single weapon by its WID (e.g. WID_Assault_...) with full stats.
- `WeaponListItemDto` fields: `id`: `str | None`, `display_name` (displayName): `str | None`, `description`: `str | None`, `rarity`: `str | None`, `type`: `str | None`, `category`: `str | None`, `ammo_type` (ammoType): `str | None`, `trigger_type` (triggerType): `str | None`, `search_tags` (searchTags): `str | None`, `in_current_loot_pool` (inCurrentLootPool): `bool | None`, `item_type` (itemType): `str | None`, `gamemodes`: `list[str] | None`, `patch`: `str | None`, `tags`: `list[str] | None`, `weapon_actor_class` (weaponActorClass): `str | None`, `stats`: `Any | None`, `images`: `Any | None`

```python
result = client.weapons.get_by_id("<id>")
print(result.id)
```

### `client.weapons.get_lootpool(*, gamemode: str | None = None, major: int | None = None, minor: int | None = None, date: str | None = None, secondary: bool | None = None, with_stats: bool | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/weapons/lootpool`
- Plans: `pro`, `custom`
- Get the resolved loot pool for a gamemode: one entry per item with per-container chances (P(item | one roll of that container)) and the underlying per-drop-list rows under `sources`, self-extracted from game data + live hotfixes.

```python
result = client.weapons.get_lootpool()
# raw JSON (dict / list) - use key access
```

### `client.weapons.get_patches(*, fortnite_token: str | None = None) -> list[PatchInfoDto]`

- HTTP: `GET /api/v2/weapons/patches`
- Plans: `pro`, `custom`
- Get all available weapon patches, with the current patch flagged.
- `PatchInfoDto` fields: `patch`: `str | None`, `is_current` (isCurrent): `bool | None`, `archived_at` (archivedAt): `str | None`, `weapon_count` (weaponCount): `int | None`, `mode_counts` (modeCounts): `dict[str, int] | None`

```python
result = client.weapons.get_patches()
first = result[0].patch if result else None
```

### `client.weapons.get_rarities(*, fortnite_token: str | None = None) -> list[RarityDefinitionDto]`

- HTTP: `GET /api/v2/weapons/rarity`
- Plans: `pro`, `custom`
- Get rarity definitions and their display colors.
- `RarityDefinitionDto` fields: `name`: `str | None`, `color`: `str | None`, `sort_order` (sortOrder): `int | None`

```python
result = client.weapons.get_rarities()
first = result[0].name if result else None
```

## `client.map`

### `client.map.get(*, version: str | None = None, mode: str | None = None, lang: str | None = None, fortnite_token: str | None = None) -> MapDataDto`

- HTTP: `GET /api/v1/map`
- Plans: `pro`, `custom`
- Get map data including POIs and minimap metadata for a given version.
- `MapDataDto` fields: `version`: `str | None`, `chapter`: `int | None`, `season`: `int | None`, `patch`: `str | None`, `release_date` (releaseDate): `str | None`, `mode`: `str | None`, `island`: `str | None`, `display_name` (displayName): `str | None`, `image_url` (imageUrl): `str | None`, `image_width` (imageWidth): `int | None`, `image_height` (imageHeight): `int | None`, `world_bounds` (worldBounds): `MapWorldBoundsDto | None`, `camera`: `MapCameraDto | None`, `pois`: `list[PoiDto] | None`, `modes`: `list[str] | None`

```python
result = client.map.get()
print(result.version)
```

### `client.map.get_history(*, chapter: int | None = None, season: int | None = None, fortnite_token: str | None = None) -> list[MapHistoryEntryDto]`

- HTTP: `GET /api/v1/map/history`
- Plans: `pro`, `custom`
- Get map history entries, optionally filtered by chapter and/or season.
- `MapHistoryEntryDto` fields: `version`: `str | None`, `chapter`: `int | None`, `season`: `int | None`, `patch`: `str | None`, `release_date` (releaseDate): `str | None`, `has_image` (hasImage): `bool | None`, `image_url` (imageUrl): `str | None`, `has_pois` (hasPois): `bool | None`, `modes`: `list[str] | None`

```python
result = client.map.get_history()
first = result[0].version if result else None
```

### `client.map.get_image(*, version: str | None = None, mode: str | None = None, fortnite_token: str | None = None) -> str | None`

- HTTP: `GET /api/v1/map/image`
- Returns the resolved URL string (redirect not followed), or `None`.
- Plans: `pro`, `custom`
- Redirects to the raw map image on GitHub for a given version.

```python
result = client.map.get_image()
```

## `client.news`

### `client.news.get_all(*, lang: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> AllNews`

- HTTP: `GET /api/v1/news`
- Plans: `pro`, `custom`
- Current lobby news for every mode, plus the emergency notices.
- `AllNews` fields: `br`: `NewsFeed | None`, `stw`: `NewsFeed | None`, `creative`: `NewsFeed | None`, `festival`: `NewsFeed | None`, `notices`: `list[NewsNotice] | None`

```python
result = client.news.get_all()
print(result.br)
```

### `client.news.get_br(*, lang: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> NewsFeed`

- HTTP: `GET /api/v1/news/br`
- Plans: `pro`, `custom`
- Current Battle Royale lobby news.
- `NewsFeed` fields: `mode`: `str | None`, `tag`: `str | None`, `language`: `str | None`, `platform`: `str | None`, `fetched_at` (fetchedAt): `str | None`, `motds`: `list[NewsMotd] | None`

```python
result = client.news.get_br()
print(result.mode)
```

### `client.news.get_creative(*, lang: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> NewsFeed`

- HTTP: `GET /api/v1/news/creative`
- Plans: `pro`, `custom`
- Current lobby news Epic serves for Creative.
- `NewsFeed` fields: `mode`: `str | None`, `tag`: `str | None`, `language`: `str | None`, `platform`: `str | None`, `fetched_at` (fetchedAt): `str | None`, `motds`: `list[NewsMotd] | None`

```python
result = client.news.get_creative()
print(result.mode)
```

### `client.news.get_festival(*, lang: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> NewsFeed`

- HTTP: `GET /api/v1/news/festival`
- Plans: `pro`, `custom`
- Current Fortnite Festival lobby news.
- `NewsFeed` fields: `mode`: `str | None`, `tag`: `str | None`, `language`: `str | None`, `platform`: `str | None`, `fetched_at` (fetchedAt): `str | None`, `motds`: `list[NewsMotd] | None`

```python
result = client.news.get_festival()
print(result.mode)
```

### `client.news.get_notices(*, lang: str | None = None, fortnite_token: str | None = None) -> list[NewsNotice]`

- HTTP: `GET /api/v1/news/notices`
- Plans: `pro`, `custom`
- Current emergency notices (the in-game warning banners), e.g. a mode leaving or a feature disabled.
- `NewsNotice` fields: `title`: `str | None`, `body`: `str | None`, `playlists`: `list[str] | None`, `platforms`: `list[str] | None`

```python
result = client.news.get_notices()
first = result[0].title if result else None
```

### `client.news.get_stw(*, lang: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> NewsFeed`

- HTTP: `GET /api/v1/news/stw`
- Plans: `pro`, `custom`
- Current lobby news Epic serves for Save the World.
- `NewsFeed` fields: `mode`: `str | None`, `tag`: `str | None`, `language`: `str | None`, `platform`: `str | None`, `fetched_at` (fetchedAt): `str | None`, `motds`: `list[NewsMotd] | None`

```python
result = client.news.get_stw()
print(result.mode)
```

## `client.playlists`

### `client.playlists.get_all(*, lang: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/playlists`
- Plans: `pro`, `custom`
- Get all playlists (game modes).

```python
result = client.playlists.get_all()
# raw JSON (dict / list) - use key access
```

### `client.playlists.get_active(*, lang: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/playlists/active`
- Plans: `pro`, `custom`
- Get currently active playlists.

```python
result = client.playlists.get_active()
# raw JSON (dict / list) - use key access
```

### `client.playlists.get_by_id(playlist_id: str, *, lang: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/playlists/{playlistId}`
- Plans: `pro`, `custom`
- Get a specific playlist by its ID.

```python
result = client.playlists.get_by_id("<playlist_id>")
# raw JSON (dict / list) - use key access
```

## `client.calendar`

### `client.calendar.get_season(*, fortnite_token: str | None = None) -> SeasonEntryDto`

- HTTP: `GET /api/v1/season`
- Plans: `free`, `pro`, `custom`
- Get the current Fortnite season number and start/end dates.
- `SeasonEntryDto` fields: `season_date_begin` (seasonDateBegin): `str | None`, `season_date_end` (seasonDateEnd): `str | None`, `season_number` (seasonNumber): `int | None`, `ex_time` (exTime): `int | None`

```python
result = client.calendar.get_season()
print(result.season_date_begin)
```

## `client.battlepass`

### `client.battlepass.get(*, season: int | None = None, fortnite_token: str | None = None) -> BattlePassCatalog`

- HTTP: `GET /api/v2/battlepass`
- Plans: `pro`, `custom`
- The current battle pass, or an archived one via `?season=`.
- `BattlePassCatalog` fields: `game_version` (gameVersion): `str | None`, `season`: `int | None`, `plugin`: `str | None`, `generated`: `str | None`, `level_rewards` (levelRewards): `dict[str, int] | None`, `prices`: `list[BattlePassPrice] | None`, `pages`: `list[BattlePassPage] | None`

```python
result = client.battlepass.get()
print(result.game_version)
```

### `client.battlepass.get_seasons(*, fortnite_token: str | None = None) -> list[BattlePassSeasonDto]`

- HTTP: `GET /api/v2/battlepass/seasons`
- Plans: `pro`, `custom`
- Every season we hold a pass for, newest first.
- `BattlePassSeasonDto` fields: `season`: `int | None`, `game_version` (gameVersion): `str | None`, `is_current` (isCurrent): `bool | None`, `pages`: `int | None`, `rewards`: `int | None`, `generated`: `str | None`

```python
result = client.battlepass.get_seasons()
first = result[0].season if result else None
```

### `client.battlepass.get_legacy(*, lang: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/shop/battlepass`
- Plans: `free`, `pro`, `custom`
- **Deprecated** (emits `DeprecationWarning`): This endpoint is marked as deprecated by the API. Use battlepass.get() (GET /api/v2/battlepass) instead.
- Deprecated: despite its name this never returned the Battle Pass.

```python
result = client.battlepass.get_legacy()
# raw JSON (dict / list) - use key access
```

## `client.sprites`

### `client.sprites.get(*, search: str | None = None, rarity: str | None = None, variant: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpritesResponseDto`

- HTTP: `GET /api/v2/sprites`
- Plans: `pro`, `custom`
- Get the full sprite catalog: families with nested variants, current + PAK-base drop weights, normalized drop chances, rarity, icons, boons, the level-up XP curve, and alternate event weight sets.
- `SpritesResponseDto` fields: `game_version` (gameVersion): `str | None`, `generated`: `str | None`, `hotfix_applied` (hotfixApplied): `bool | None`, `is_current` (isCurrent): `bool | None`, `sprites`: `list[SpriteFamilyDto] | None`, `level_up_curve` (levelUpCurve): `list[SpriteLevelDto] | None`, `events`: `list[SpriteEventDto] | None`, `spawn_lists` (spawnLists): `list[SpriteSpawnListDto] | None`

```python
result = client.sprites.get()
print(result.game_version)
```

### `client.sprites.get_all(*, search: str | None = None, rarity: str | None = None, variant: str | None = None, fortnite_token: str | None = None) -> AllSpritesResponseDto`

- HTTP: `GET /api/v2/sprites/all`
- Plans: `pro`, `custom`
- Every season's catalog in one call — the whole sprite archive, grouped by game version, current season first.
- `AllSpritesResponseDto` fields: `version_count` (versionCount): `int | None`, `family_count` (familyCount): `int | None`, `versions`: `list[SpritesResponseDto] | None`

```python
result = client.sprites.get_all()
print(result.version_count)
```

### `client.sprites.get_versions(*, fortnite_token: str | None = None) -> list[SpriteVersionDto]`

- HTTP: `GET /api/v2/sprites/versions`
- Plans: `pro`, `custom`
- Every archived sprite catalog version, newest first.
- `SpriteVersionDto` fields: `version`: `str | None`, `generated`: `str | None`, `is_current` (isCurrent): `bool | None`, `family_count` (familyCount): `int | None`

```python
result = client.sprites.get_versions()
first = result[0].version if result else None
```

### `client.sprites.get_boons(*, fortnite_token: str | None = None) -> list[SpriteBoonDto]`

- HTTP: `GET /api/v2/sprites/boons`
- Plans: `pro`, `custom`
- Get all SpriteBoons perks with names and descriptions.
- `SpriteBoonDto` fields: `id`: `str | None`, `name`: `str | None`, `description`: `str | None`

```python
result = client.sprites.get_boons()
first = result[0].id if result else None
```

### `client.sprites.get_by_id(id: str, *, fortnite_token: str | None = None) -> SpriteFamilyDto`

- HTTP: `GET /api/v2/sprites/{id}`
- Plans: `pro`, `custom`
- Get a single sprite family by family id, variant id, or name.
- `SpriteFamilyDto` fields: `id`: `str | None`, `name`: `str | None`, `description`: `str | None`, `dex_number` (dexNumber): `int | None`, `rarity`: `str | None`, `acquisition_hint` (acquisitionHint): `str | None`, `extract_reward_loot_tier` (extractRewardLootTier): `str | None`, `images`: `SpriteImagesDto | None`, `tags`: `list[str] | None`, `boons`: `list[SpriteBoonRefDto] | None`, `spawn_weight` (spawnWeight): `float | None`, `spawn_chance_percent` (spawnChancePercent): `float | None`, `variants`: `list[SpriteVariantDto] | None`

```python
result = client.sprites.get_by_id("<id>")
print(result.id)
```

### `client.sprites.get_collection(*, account_id: str | None = None, version: str | None = None, fortnite_token: str | None = None) -> SpriteCollectionResponseDto`

- HTTP: `GET /api/v2/sprites/collection`
- Plans: `pro`, `custom`
- Token: **required** - the caller's own `x-fortnite-token` (a collection can only be read with its owner's token)
- Get the caller's own sprite collection — the catalog annotated with what they own, each variant carrying `owned`, `count`, `xp` and `mastered`, plus their equipped variant, starter sprite, season currency and a completion percentage.
- `SpriteCollectionResponseDto` fields: `account_id` (accountId): `str | None`, `display_name` (displayName): `str | None`, `game_version` (gameVersion): `str | None`, `generated`: `str | None`, `is_current` (isCurrent): `bool | None`, `equipped_variant` (equippedVariant): `str | None`, `starter_relic` (starterRelic): `str | None`, `owned_variants` (ownedVariants): `int | None`, `total_variants` (totalVariants): `int | None`, `owned_families` (ownedFamilies): `int | None`, `total_families` (totalFamilies): `int | None`, `completion_percent` (completionPercent): `float | None`, `currency`: `list[SpriteCurrencyDto] | None`, `sprites`: `list[SpriteCollectionFamilyDto] | None`

```python
result = client.sprites.get_collection()
print(result.account_id)
```

### `client.sprites.get_all_collections(*, account_id: str | None = None, fortnite_token: str | None = None) -> AllSpriteCollectionsResponseDto`

- HTTP: `GET /api/v2/sprites/collection/all`
- Plans: `pro`, `custom`
- Token: **required** - the caller's own `x-fortnite-token` (a collection can only be read with its owner's token)
- The caller's collection across EVERY season in one call — each season's catalog annotated with what they own, plus cumulative cross-season totals.
- `AllSpriteCollectionsResponseDto` fields: `account_id` (accountId): `str | None`, `display_name` (displayName): `str | None`, `version_count` (versionCount): `int | None`, `owned_variants` (ownedVariants): `int | None`, `total_variants` (totalVariants): `int | None`, `owned_families` (ownedFamilies): `int | None`, `total_families` (totalFamilies): `int | None`, `completion_percent` (completionPercent): `float | None`, `currency`: `list[SpriteCurrencyDto] | None`, `versions`: `list[SpriteCollectionResponseDto] | None`

```python
result = client.sprites.get_all_collections()
print(result.account_id)
```

### `client.sprites.publish_collection(*, body: PublishCollectionRequest | dict[str, Any] | None = None, fortnite_token: str | None = None) -> SpriteSharePublishResultDto`

- HTTP: `POST /api/v2/sprites/collection/publish`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Publish (or refresh) the caller's OWN collection so others can view it — this is the opt-in basis for "see another player's collection". Requires the caller's own `x-fortnite-token`; the share is keyed to the account that token verifies as, so no one can publish on another account's behalf.
- `SpriteSharePublishResultDto` fields: `account_id` (accountId): `str | None`, `display_name` (displayName): `str | None`, `visibility`: `str | None`, `owned_variants` (ownedVariants): `int | None`, `total_variants` (totalVariants): `int | None`, `completion_percent` (completionPercent): `float | None`, `auto_refresh` (autoRefresh): `bool | None`, `snapshot_generated_at` (snapshotGeneratedAt): `str | None`

```python
result = client.sprites.publish_collection()
print(result.account_id)
```

### `client.sprites.unpublish_collection(*, fortnite_token: str | None = None) -> Any`

- HTTP: `DELETE /api/v2/sprites/collection/publish`
- Plans: `pro`, `custom`
- Token: **required** — the caller's own token
- Remove the caller's shared collection (verified from their own token).

```python
result = client.sprites.unpublish_collection()
# raw JSON (dict / list) - use key access
```

### `client.sprites.get_shared_collection(account_id_or_name: str, *, fortnite_token: str | None = None) -> SharedSpriteCollectionDto`

- HTTP: `GET /api/v2/sprites/collection/shared/{accountIdOrName}`
- Plans: `pro`, `custom`
- Token: not required
- Get another player's opt-in shared collection by Epic account id or display name. Only returns collections the owner has published: public shares resolve by name or id, unlisted shares only by exact account id, and private/never-published resolve to 404. No Epic token is required and none of the target player's credentials are used.
- `SharedSpriteCollectionDto` fields: `visibility`: `str | None`, `snapshot_generated_at` (snapshotGeneratedAt): `str | None`, `refreshed`: `bool | None`, `collection`: `SpriteCollectionResponseDto | None`

```python
result = client.sprites.get_shared_collection("<account_id_or_name>")
print(result.visibility)
```

## `client.aes`

### `client.aes.get_keys(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/aes`
- Plans: not stated in the spec
- Current AES main key and dynamic pak keys.

```python
result = client.aes.get_keys()
# raw JSON (dict / list) - use key access
```

### `client.aes.get_history(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/aes/history`
- Plans: not stated in the spec
- Every build whose AES keys and mappings we hold.

```python
result = client.aes.get_history()
# raw JSON (dict / list) - use key access
```

### `client.aes.get_mappings(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/mappings`
- Plans: not stated in the spec
- Current .usmap mappings download URLs.

```python
result = client.aes.get_mappings()
# raw JSON (dict / list) - use key access
```

## `client.assets`

### `client.assets.get_shop_bundles(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/assets/bundles/shop`
- Plans: `pro`, `custom`
- Get shop asset bundles.

```python
result = client.assets.get_shop_bundles()
# raw JSON (dict / list) - use key access
```

### `client.assets.get_tournament_bundles(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/assets/bundles/tournaments`
- Plans: `pro`, `custom`
- Get tournament asset bundles (images, icons, rewards).

```python
result = client.assets.get_tournament_bundles()
# raw JSON (dict / list) - use key access
```

## `client.crew`

### `client.crew.get_current(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/crew/current`
- Plans: `pro`, `custom`
- Get the current Fortnite Crew pack.

```python
result = client.crew.get_current()
# raw JSON (dict / list) - use key access
```

### `client.crew.get_history(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/crew/history`
- Plans: `pro`, `custom`
- Get the history of past Fortnite Crew packs.

```python
result = client.crew.get_history()
# raw JSON (dict / list) - use key access
```

