from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FNModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class CompleteOAuthRequest(FNModel):
    flow_id: str | None = Field(default=None, alias="flowId")

class CosmeticDto(FNModel):
    id: str | None = None
    type: str | None = None
    name: str | None = None
    description: str | None = None
    rarity: str | None = None
    series: str | None = None
    set: str | None = None
    icon: str | None = None
    introduction: CosmeticIntroductionDto | None = None
    images: CosmeticImagesDto | None = None
    tags: list[str] | None = None

class CosmeticDtoPaginatedResultDto(FNModel):
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")
    data: list[CosmeticDto] | None = None

class CosmeticImagesDto(FNModel):
    small_icon: str | None = Field(default=None, alias="smallIcon")
    icon: str | None = None
    large_icon: str | None = Field(default=None, alias="largeIcon")

class CosmeticIntroductionDto(FNModel):
    chapter: int | None = None
    season: int | None = None
    absolute_season: int | None = Field(default=None, alias="absoluteSeason")

class ExchangeCodeRequest(FNModel):
    code: str | None = None
    redirect_uri: str | None = Field(default=None, alias="redirectUri")
    client_id: str | None = Field(default=None, alias="clientId")
    client_secret: str | None = Field(default=None, alias="clientSecret")

class LinkAccountRequest(FNModel):
    code: str | None = None
    redirect_uri: str | None = Field(default=None, alias="redirectUri")
    client_id: str | None = Field(default=None, alias="clientId")
    client_secret: str | None = Field(default=None, alias="clientSecret")

class MapDataDto(FNModel):
    version: str | None = None
    chapter: int | None = None
    season: int | None = None
    patch: str | None = None
    release_date: str | None = Field(default=None, alias="releaseDate")
    image_url: str | None = Field(default=None, alias="imageUrl")
    pois: list[PoiDto] | None = None

class MapHistoryEntryDto(FNModel):
    version: str | None = None
    chapter: int | None = None
    season: int | None = None
    patch: str | None = None
    release_date: str | None = Field(default=None, alias="releaseDate")
    has_image: bool | None = Field(default=None, alias="hasImage")
    image_url: str | None = Field(default=None, alias="imageUrl")
    has_pois: bool | None = Field(default=None, alias="hasPois")

class PatchInfoDto(FNModel):
    patch: str | None = None
    is_current: bool | None = Field(default=None, alias="isCurrent")
    archived_at: str | None = Field(default=None, alias="archivedAt")
    weapon_count: int | None = Field(default=None, alias="weaponCount")
    mode_counts: dict[str, int] | None = Field(default=None, alias="modeCounts")

class PoiDto(FNModel):
    name: str | None = None
    x: float | None = None
    y: float | None = None
    type: str | None = None

class ProblemDetails(FNModel):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None

class RarityDefinitionDto(FNModel):
    name: str | None = None
    color: str | None = None
    sort_order: int | None = Field(default=None, alias="sortOrder")

class RefreshDeviceRequest(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    device_id: str | None = Field(default=None, alias="deviceId")
    secret: str | None = None

class RefreshTokenRequest(FNModel):
    refresh_token: str | None = Field(default=None, alias="refreshToken")

class SeasonEntryDto(FNModel):
    season_date_begin: str | None = Field(default=None, alias="seasonDateBegin")
    season_date_end: str | None = Field(default=None, alias="seasonDateEnd")
    season_number: int | None = Field(default=None, alias="seasonNumber")
    ex_time: int | None = Field(default=None, alias="exTime")

class ShopBundleDto(FNModel):
    name: str | None = None
    info: str | None = None
    items: int | None = None
    regular_price: int | None = Field(default=None, alias="regularPrice")
    final_price: int | None = Field(default=None, alias="finalPrice")
    discount: int | None = None

class ShopCatalogEntryDto(FNModel):
    offer_id: str | None = Field(default=None, alias="offerId")
    dev_name: str | None = Field(default=None, alias="devName")
    title: str | None = None
    sort_priority: int | None = Field(default=None, alias="sortPriority")
    prices: list[ShopPriceDto] | None = None
    item_grants: list[ShopItemGrantDto] | None = Field(default=None, alias="itemGrants")
    bundle: ShopBundleDto | None = None
    section_id: str | None = Field(default=None, alias="sectionId")
    section_display_name: str | None = Field(default=None, alias="sectionDisplayName")
    section_priority: int | None = Field(default=None, alias="sectionPriority")
    section_background: str | None = Field(default=None, alias="sectionBackground")
    offer_visual: str | None = Field(default=None, alias="offerVisual")
    style_visuals: list[str] | None = Field(default=None, alias="styleVisuals")
    juno_visual: str | None = Field(default=None, alias="junoVisual")
    tile_size: str | None = Field(default=None, alias="tileSize")
    meta_info: list[ShopMetaInfoDto] | None = Field(default=None, alias="metaInfo")

class ShopCosmeticDto(FNModel):
    type: str | None = None
    name: str | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    description: str | None = None
    short_description: str | None = Field(default=None, alias="shortDescription")
    rarity: str | None = None
    images: ShopCosmeticImagesDto | None = None
    set: str | None = None
    introduction: ShopCosmeticIntroductionDto | None = None
    tags: list[str] | None = None

class ShopCosmeticImagesDto(FNModel):
    icon: str | None = None
    large_icon: str | None = Field(default=None, alias="largeIcon")

class ShopCosmeticIntroductionDto(FNModel):
    chapter: int | None = None
    season: int | None = None

class ShopItemGrantDto(FNModel):
    template_id: str | None = Field(default=None, alias="templateId")
    quantity: int | None = None
    cosmetic: ShopCosmeticDto | None = None

class ShopMetaInfoDto(FNModel):
    key: str | None = None
    value: str | None = None

class ShopPriceDto(FNModel):
    currency_type: str | None = Field(default=None, alias="currencyType")
    regular_price: int | None = Field(default=None, alias="regularPrice")
    final_price: int | None = Field(default=None, alias="finalPrice")
    sale_type: str | None = Field(default=None, alias="saleType")

class ShopResponseDto(FNModel):
    refresh_interval_hrs: float | None = Field(default=None, alias="refreshIntervalHrs")
    daily_purchase_hrs: float | None = Field(default=None, alias="dailyPurchaseHrs")
    expiration: str | None = None
    storefronts: list[ShopStorefrontDto] | None = None

class ShopStorefrontDto(FNModel):
    name: str | None = None
    catalog_entries: list[ShopCatalogEntryDto] | None = Field(default=None, alias="catalogEntries")

class WeaponListItemDto(FNModel):
    id: str | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    description: str | None = None
    rarity: str | None = None
    type: str | None = None
    category: str | None = None
    ammo_type: str | None = Field(default=None, alias="ammoType")
    trigger_type: str | None = Field(default=None, alias="triggerType")
    search_tags: str | None = Field(default=None, alias="searchTags")
    in_current_loot_pool: bool | None = Field(default=None, alias="inCurrentLootPool")
    item_type: str | None = Field(default=None, alias="itemType")
    gamemodes: list[str] | None = None
    patch: str | None = None
    tags: list[str] | None = None
    stats: Any | None = None
    images: Any | None = None


__all__ = [
    "CompleteOAuthRequest",
    "CosmeticDto",
    "CosmeticDtoPaginatedResultDto",
    "CosmeticImagesDto",
    "CosmeticIntroductionDto",
    "ExchangeCodeRequest",
    "LinkAccountRequest",
    "MapDataDto",
    "MapHistoryEntryDto",
    "PatchInfoDto",
    "PoiDto",
    "ProblemDetails",
    "RarityDefinitionDto",
    "RefreshDeviceRequest",
    "RefreshTokenRequest",
    "SeasonEntryDto",
    "ShopBundleDto",
    "ShopCatalogEntryDto",
    "ShopCosmeticDto",
    "ShopCosmeticImagesDto",
    "ShopCosmeticIntroductionDto",
    "ShopItemGrantDto",
    "ShopMetaInfoDto",
    "ShopPriceDto",
    "ShopResponseDto",
    "ShopStorefrontDto",
    "WeaponListItemDto",
]

for _m in list(__all__):
    globals()[_m].model_rebuild()
