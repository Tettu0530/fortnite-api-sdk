from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FNModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class AllNews(FNModel):
    br: NewsFeed | None = None
    stw: NewsFeed | None = None
    creative: NewsFeed | None = None
    festival: NewsFeed | None = None
    notices: list[NewsNotice] | None = None

class AllSpriteCollectionsResponseDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    version_count: int | None = Field(default=None, alias="versionCount")
    owned_variants: int | None = Field(default=None, alias="ownedVariants")
    total_variants: int | None = Field(default=None, alias="totalVariants")
    owned_families: int | None = Field(default=None, alias="ownedFamilies")
    total_families: int | None = Field(default=None, alias="totalFamilies")
    completion_percent: float | None = Field(default=None, alias="completionPercent")
    currency: list[SpriteCurrencyDto] | None = None
    versions: list[SpriteCollectionResponseDto] | None = None

class AllSpritesResponseDto(FNModel):
    version_count: int | None = Field(default=None, alias="versionCount")
    family_count: int | None = Field(default=None, alias="familyCount")
    versions: list[SpritesResponseDto] | None = None

class BattlePassCatalog(FNModel):
    game_version: str | None = Field(default=None, alias="gameVersion")
    season: int | None = None
    plugin: str | None = None
    generated: str | None = None
    level_rewards: dict[str, int] | None = Field(default=None, alias="levelRewards")
    prices: list[BattlePassPrice] | None = None
    pages: list[BattlePassPage] | None = None

class BattlePassPage(FNModel):
    id: str | None = None
    track: str | None = None
    page: int | None = None
    rewards: list[BattlePassReward] | None = None

class BattlePassPrice(FNModel):
    name: str | None = None
    cost: int | None = None
    currency: str | None = None

class BattlePassReward(FNModel):
    item: str | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    type: str | None = None
    rarity: str | None = None
    icon: str | None = None
    quantity: int | None = None
    price_row: str | None = Field(default=None, alias="priceRow")
    cost: int | None = None
    currency: str | None = None
    tile_size: str | None = Field(default=None, alias="tileSize")
    offer_guid: str | None = Field(default=None, alias="offerGuid")

class BattlePassSeasonDto(FNModel):
    season: int | None = None
    game_version: str | None = Field(default=None, alias="gameVersion")
    is_current: bool | None = Field(default=None, alias="isCurrent")
    pages: int | None = None
    rewards: int | None = None
    generated: str | None = None

class CashPrizePayoutDto(FNModel):
    reward_type: str | None = Field(default=None, alias="rewardType")
    reward_mode: str | None = Field(default=None, alias="rewardMode")
    value: str | None = None
    quantity: float | None = None
    notifies_player: bool | None = Field(default=None, alias="notifiesPlayer")

class CashPrizeRankDto(FNModel):
    threshold: int | None = None
    payouts: list[CashPrizePayoutDto] | None = None

class CashPrizeScoringDto(FNModel):
    scoring_type: str | None = Field(default=None, alias="scoringType")
    ranks: list[CashPrizeRankDto] | None = None

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
    weapon_actor_class: str | None = Field(default=None, alias="weaponActorClass")

class CosmeticDtoPaginatedResultDto(FNModel):
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")
    data: list[CosmeticDto] | None = None

class CosmeticImageSetDto(FNModel):
    id: str | None = None
    type: str | None = None
    name: str | None = None
    icons: CosmeticImagesDto | None = None
    featured: str | None = None
    styles: list[str] | None = None
    lego: str | None = None
    has_renders: bool | None = Field(default=None, alias="hasRenders")

class CosmeticImagesDto(FNModel):
    small_icon: str | None = Field(default=None, alias="smallIcon")
    icon: str | None = None
    large_icon: str | None = Field(default=None, alias="largeIcon")

class CosmeticIntroductionDto(FNModel):
    chapter: int | None = None
    season: int | None = None
    absolute_season: int | None = Field(default=None, alias="absoluteSeason")

class CosmeticMediaDto(FNModel):
    id: str | None = None
    template_id: str | None = Field(default=None, alias="templateId")
    type: str | None = None
    name: str | None = None
    videos: list[CosmeticVideoDto] | None = None
    variants: list[CosmeticVariantMediaDto] | None = None
    captured_at: str | None = Field(default=None, alias="capturedAt")

class CosmeticMediaDtoPaginatedResultDto(FNModel):
    page: int | None = None
    page_size: int | None = Field(default=None, alias="pageSize")
    total: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")
    data: list[CosmeticMediaDto] | None = None

class CosmeticVariantMediaDto(FNModel):
    channel: str | None = None
    tag: str | None = None
    name: str | None = None
    unlockable: bool | None = None
    image: str | None = None
    videos: list[CosmeticVideoDto] | None = None

class CosmeticVideoDto(FNModel):
    title: str | None = None
    asset_type: str | None = Field(default=None, alias="assetType")
    poster: str | None = None
    sources: list[CosmeticVideoSourceDto] | None = None

class CosmeticVideoSourceDto(FNModel):
    url: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")
    media: str | None = None
    bytes: int | None = None

class EpicEventDto(FNModel):
    game_id: str | None = Field(default=None, alias="gameId")
    event_id: str | None = Field(default=None, alias="eventId")
    begin_time: str | None = Field(default=None, alias="beginTime")
    end_time: str | None = Field(default=None, alias="endTime")
    display_data_id: str | None = Field(default=None, alias="displayDataId")
    event_group: str | None = Field(default=None, alias="eventGroup")
    announcement_time: str | None = Field(default=None, alias="announcementTime")
    regions: list[str] | None = None
    region_mappings: dict[str, str] | None = Field(default=None, alias="regionMappings")
    platforms: list[str] | None = None
    platform_mappings: dict[str, str] | None = Field(default=None, alias="platformMappings")
    metadata: EpicEventMetadataDto | None = None
    event_windows: list[EpicEventWindowDto] | None = Field(default=None, alias="eventWindows")
    link: str | None = None

class EpicEventMetadataDto(FNModel):
    tournament_type: str | None = Field(default=None, alias="tournamentType")
    team_lock_type: str | None = Field(default=None, alias="TeamLockType")
    account_lock_type: str | None = Field(default=None, alias="AccountLockType")
    disqualify_type: str | None = Field(default=None, alias="DisqualifyType")
    web_id: str | None = Field(default=None, alias="webId")
    minimum_account_level: int | None = Field(default=None, alias="minimumAccountLevel")
    tracked_stats: list[str] | None = Field(default=None, alias="TrackedStats")
    require_system_features: list[str] | None = Field(default=None, alias="requireSystemFeatures")

class EpicEventWindowDto(FNModel):
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    event_template_id: str | None = Field(default=None, alias="eventTemplateId")
    countdown_begin_time: str | None = Field(default=None, alias="countdownBeginTime")
    begin_time: str | None = Field(default=None, alias="beginTime")
    end_time: str | None = Field(default=None, alias="endTime")
    round: int | None = None
    payout_delay: int | None = Field(default=None, alias="payoutDelay")
    is_tbd: bool | None = Field(default=None, alias="isTBD")
    visibility: str | None = None
    teammate_eligibility: str | None = Field(default=None, alias="teammateEligibility")
    can_live_spectate: bool | None = Field(default=None, alias="canLiveSpectate")
    require_all_tokens: list[str] | None = Field(default=None, alias="requireAllTokens")
    require_any_tokens: list[str] | None = Field(default=None, alias="requireAnyTokens")

class EventLeaderboardDto(FNModel):
    game_id: str | None = Field(default=None, alias="gameId")
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    page: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")
    updated_time: str | None = Field(default=None, alias="updatedTime")
    entries: list[EventLeaderboardEntryDto] | None = None

class EventLeaderboardEntryDto(FNModel):
    game_id: str | None = Field(default=None, alias="gameId")
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    team_id: str | None = Field(default=None, alias="teamId")
    team_account_ids: list[str] | None = Field(default=None, alias="teamAccountIds")
    rank: int | None = None
    points_earned: int | None = Field(default=None, alias="pointsEarned")
    score: int | None = None
    percentile: float | None = None
    point_breakdown: dict[str, Any] | None = Field(default=None, alias="pointBreakdown")
    session_history: list[EventMatchDto] | None = Field(default=None, alias="sessionHistory")

class EventMatchDto(FNModel):
    session_id: str | None = Field(default=None, alias="sessionId")
    end_time: str | None = Field(default=None, alias="endTime")
    tracked_stats: dict[str, float] | None = Field(default=None, alias="trackedStats")

class EventSessionDto(FNModel):
    group_id: str | None = Field(default=None, alias="groupId")
    name: str | None = None
    short_title: str | None = Field(default=None, alias="shortTitle")
    title_line1: str | None = Field(default=None, alias="titleLine1")
    title_line2: str | None = Field(default=None, alias="titleLine2")
    description: str | None = None
    details_description: str | None = Field(default=None, alias="detailsDescription")
    schedule_info: str | None = Field(default=None, alias="scheduleInfo")
    poster: str | None = None
    loading_screen: str | None = Field(default=None, alias="loadingScreen")
    matched_event_id: str | None = Field(default=None, alias="matchedEventId")
    matched_region: str | None = Field(default=None, alias="matchedRegion")
    all_regions: list[str] | None = Field(default=None, alias="allRegions")
    matched_event: EpicEventDto | None = Field(default=None, alias="matchedEvent")

class EventStatRankingDto(FNModel):
    rank: int | None = None
    leaderboard_rank: int | None = Field(default=None, alias="leaderboardRank")
    points_earned: int | None = Field(default=None, alias="pointsEarned")
    games_played: int | None = Field(default=None, alias="gamesPlayed")
    stat_total: float | None = Field(default=None, alias="statTotal")
    stat_per_game: float | None = Field(default=None, alias="statPerGame")
    team_account_ids: list[str] | None = Field(default=None, alias="teamAccountIds")
    team_account_display_names: list[str] | None = Field(default=None, alias="teamAccountDisplayNames")

class EventStatsLeaderboardDto(FNModel):
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    stat_key: str | None = Field(default=None, alias="statKey")
    top: int | None = None
    total_teams: int | None = Field(default=None, alias="totalTeams")
    total_pages: int | None = Field(default=None, alias="totalPages")
    updated_time: str | None = Field(default=None, alias="updatedTime")
    available_stats: list[str] | None = Field(default=None, alias="availableStats")
    rankings: list[EventStatRankingDto] | None = None

class EventTokenEligibilityDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    is_eligible: bool | None = Field(default=None, alias="isEligible")
    verdict: str | None = None
    verified_requirements: list[VerifiedRequirementDto] | None = Field(default=None, alias="verifiedRequirements")
    additional_requirements: list[Any] | None = Field(default=None, alias="additionalRequirements")
    unverified_requirements: list[UnverifiedRequirementDto] | None = Field(default=None, alias="unverifiedRequirements")

class ExchangeCodeRequest(FNModel):
    code: str | None = None
    redirect_uri: str | None = Field(default=None, alias="redirectUri")
    client_id: str | None = Field(default=None, alias="clientId")
    client_secret: str | None = Field(default=None, alias="clientSecret")

class GlobalEventDto(FNModel):
    id: str | None = None
    display_data_id: str | None = Field(default=None, alias="displayDataId")
    name: str | None = None
    short_title: str | None = Field(default=None, alias="shortTitle")
    title_line1: str | None = Field(default=None, alias="titleLine1")
    title_line2: str | None = Field(default=None, alias="titleLine2")
    description: str | None = None
    details_description: str | None = Field(default=None, alias="detailsDescription")
    schedule_info: str | None = Field(default=None, alias="scheduleInfo")
    poster: str | None = None
    loading_screen: str | None = Field(default=None, alias="loadingScreen")
    regions: dict[str, list[EpicEventDto]] | None = None

class InitiateRequest(FNModel):
    custom_key: str | None = None
    players_id: list[str] | None = None

class LinkAccountRequest(FNModel):
    code: str | None = None
    redirect_uri: str | None = Field(default=None, alias="redirectUri")
    client_id: str | None = Field(default=None, alias="clientId")
    client_secret: str | None = Field(default=None, alias="clientSecret")

class LinkRequest(FNModel):
    discord_id: str | None = None
    epic_account_id: str | None = None
    display_name: str | None = None

class MapCameraDto(FNModel):
    ortho_width: float | None = Field(default=None, alias="orthoWidth")
    world_offset_x: float | None = Field(default=None, alias="worldOffsetX")
    world_offset_y: float | None = Field(default=None, alias="worldOffsetY")
    rotation: float | None = None

class MapDataDto(FNModel):
    version: str | None = None
    chapter: int | None = None
    season: int | None = None
    patch: str | None = None
    release_date: str | None = Field(default=None, alias="releaseDate")
    mode: str | None = None
    island: str | None = None
    display_name: str | None = Field(default=None, alias="displayName")
    image_url: str | None = Field(default=None, alias="imageUrl")
    image_width: int | None = Field(default=None, alias="imageWidth")
    image_height: int | None = Field(default=None, alias="imageHeight")
    world_bounds: MapWorldBoundsDto | None = Field(default=None, alias="worldBounds")
    camera: MapCameraDto | None = None
    pois: list[PoiDto] | None = None
    modes: list[str] | None = None

class MapHistoryEntryDto(FNModel):
    version: str | None = None
    chapter: int | None = None
    season: int | None = None
    patch: str | None = None
    release_date: str | None = Field(default=None, alias="releaseDate")
    has_image: bool | None = Field(default=None, alias="hasImage")
    image_url: str | None = Field(default=None, alias="imageUrl")
    has_pois: bool | None = Field(default=None, alias="hasPois")
    modes: list[str] | None = None

class MapWorldBoundsDto(FNModel):
    min_x: float | None = Field(default=None, alias="minX")
    max_x: float | None = Field(default=None, alias="maxX")
    min_y: float | None = Field(default=None, alias="minY")
    max_y: float | None = Field(default=None, alias="maxY")

class NewsButton(FNModel):
    text: str | None = None
    action: str | None = None
    offer_id: str | None = Field(default=None, alias="offerId")
    link_id: str | None = Field(default=None, alias="linkId")

class NewsFeed(FNModel):
    mode: str | None = None
    tag: str | None = None
    language: str | None = None
    platform: str | None = None
    fetched_at: str | None = Field(default=None, alias="fetchedAt")
    motds: list[NewsMotd] | None = None

class NewsImage(FNModel):
    width: int | None = None
    height: int | None = None
    url: str | None = None

class NewsMotd(FNModel):
    id: str | None = None
    position: int | None = None
    title: str | None = None
    body: str | None = None
    tile_title: str | None = Field(default=None, alias="tileTitle")
    image: str | None = None
    tile_image: str | None = Field(default=None, alias="tileImage")
    images: list[NewsImage] | None = None
    tile_images: list[NewsImage] | None = Field(default=None, alias="tileImages")
    buttons: list[NewsButton] | None = None
    content_hash: str | None = Field(default=None, alias="contentHash")

class NewsNotice(FNModel):
    title: str | None = None
    body: str | None = None
    playlists: list[str] | None = None
    platforms: list[str] | None = None

class PatchInfoDto(FNModel):
    patch: str | None = None
    is_current: bool | None = Field(default=None, alias="isCurrent")
    archived_at: str | None = Field(default=None, alias="archivedAt")
    weapon_count: int | None = Field(default=None, alias="weaponCount")
    mode_counts: dict[str, int] | None = Field(default=None, alias="modeCounts")

class PlayerTokenAccountDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    tokens: list[str] | None = None

class PlayerTokensDto(FNModel):
    accounts: list[PlayerTokenAccountDto] | None = None

class PlayerWindowStandingDto(FNModel):
    found: bool | None = None
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    account_id: str | None = Field(default=None, alias="accountId")
    rank: int | None = None
    points_earned: int | None = Field(default=None, alias="pointsEarned")
    team_account_ids: list[str] | None = Field(default=None, alias="teamAccountIds")
    match_count: int | None = Field(default=None, alias="matchCount")
    matches: list[EventMatchDto] | None = None

class PoiDto(FNModel):
    name: str | None = None
    tag: str | None = None
    type: str | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None

class PowerRankingArchiveDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    rank: int | None = None
    score: int | None = None
    best_rank: int | None = Field(default=None, alias="bestRank")
    peak_pr: int | None = Field(default=None, alias="peakPr")
    delta_pr: int | None = Field(default=None, alias="deltaPr")
    counting_events: int | None = Field(default=None, alias="countingEvents")
    last_updated: str | None = Field(default=None, alias="lastUpdated")
    season_label: str | None = Field(default=None, alias="seasonLabel")

class PowerRankingEntryDto(FNModel):
    game_id: str | None = Field(default=None, alias="gameId")
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    team_id: str | None = Field(default=None, alias="teamId")
    team_account_ids: list[str] | None = Field(default=None, alias="teamAccountIds")
    team_account_display_names: list[str] | None = Field(default=None, alias="teamAccountDisplayNames")
    rank: int | None = None
    points_earned: int | None = Field(default=None, alias="pointsEarned")
    score: int | None = None
    percentile: float | None = None
    point_breakdown: dict[str, Any] | None = Field(default=None, alias="pointBreakdown")
    session_history: list[EventMatchDto] | None = Field(default=None, alias="sessionHistory")

class PowerRankingSearchDto(FNModel):
    query: str | None = None
    total: int | None = None
    results: list[PowerRankingSearchResultDto] | None = None

class PowerRankingSearchResultDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    rank: int | None = None
    score: int | None = None
    counting_events: int | None = Field(default=None, alias="countingEvents")
    peak_pr: int | None = Field(default=None, alias="peakPr")
    delta_pr: int | None = Field(default=None, alias="deltaPr")

class PowerRankingsPageDto(FNModel):
    game_id: str | None = Field(default=None, alias="gameId")
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    page: int | None = None
    total_pages: int | None = Field(default=None, alias="totalPages")
    updated_time: str | None = Field(default=None, alias="updatedTime")
    entries: list[PowerRankingEntryDto] | None = None

class ProblemDetails(FNModel):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None

class PublishCollectionRequest(FNModel):
    visibility: str | None = None
    auto_refresh: bool | None = Field(default=None, alias="autoRefresh")
    device_auth: Any | None = Field(default=None, alias="deviceAuth")

class QuestBundleDefinition(FNModel):
    template_id: str | None = Field(default=None, alias="templateId")
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    large_icon: str | None = Field(default=None, alias="largeIcon")
    schedule: str | None = None
    quests: list[str] | None = None

class QuestDefinition(FNModel):
    template_id: str | None = Field(default=None, alias="templateId")
    name: str | None = None
    name_rich: str | None = Field(default=None, alias="nameRich")
    description: str | None = None
    flavor_text: str | None = Field(default=None, alias="flavorText")
    type: str | None = None
    subtype: str | None = None
    visible: bool | None = None
    sort_priority: int | None = Field(default=None, alias="sortPriority")
    tags: list[str] | None = None
    icon: str | None = None
    icon_source: str | None = Field(default=None, alias="iconSource")
    bundle: str | None = None
    objectives: list[QuestObjectiveDefinition] | None = None
    rewards: list[QuestRewardDefinition] | None = None

class QuestDefinitionResult(FNModel):
    game_version: str | None = Field(default=None, alias="gameVersion")
    quest: QuestDefinition | None = None
    bundle: QuestBundleDefinition | None = None

class QuestDefinitionsPage(FNModel):
    game_version: str | None = Field(default=None, alias="gameVersion")
    generated: str | None = None
    total: int | None = None
    offset: int | None = None
    limit: int | None = None
    quests: list[QuestDefinition] | None = None
    not_found: list[str] | None = Field(default=None, alias="notFound")

class QuestObjectiveDefinition(FNModel):
    id: str | None = None
    stat_name: str | None = Field(default=None, alias="statName")
    description: str | None = None
    count: int | None = None
    stage: int | None = None
    max_stage: int | None = Field(default=None, alias="maxStage")

class QuestRewardDefinition(FNModel):
    template_id: str | None = Field(default=None, alias="templateId")
    quantity: int | None = None
    tier: str | None = None
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    required_token: str | None = Field(default=None, alias="requiredToken")

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

class RegisterAccountRequest(FNModel):
    label: str | None = None
    device_auth_json: str | None = None
    roles: list[str] | None = None

class SeasonEntryDto(FNModel):
    season_date_begin: str | None = Field(default=None, alias="seasonDateBegin")
    season_date_end: str | None = Field(default=None, alias="seasonDateEnd")
    season_number: int | None = Field(default=None, alias="seasonNumber")
    ex_time: int | None = Field(default=None, alias="exTime")

class SharedSpriteCollectionDto(FNModel):
    visibility: str | None = None
    snapshot_generated_at: str | None = Field(default=None, alias="snapshotGeneratedAt")
    refreshed: bool | None = None
    collection: SpriteCollectionResponseDto | None = None

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

class SpriteBoonDto(FNModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None

class SpriteBoonRefDto(FNModel):
    id: str | None = None
    chance: float | None = None

class SpriteCollectionFamilyDto(FNModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    dex_number: int | None = Field(default=None, alias="dexNumber")
    rarity: str | None = None
    images: SpriteImagesDto | None = None
    owned: bool | None = None
    owned_variants: int | None = Field(default=None, alias="ownedVariants")
    variants: list[SpriteCollectionVariantDto] | None = None

class SpriteCollectionResponseDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    game_version: str | None = Field(default=None, alias="gameVersion")
    generated: str | None = None
    is_current: bool | None = Field(default=None, alias="isCurrent")
    equipped_variant: str | None = Field(default=None, alias="equippedVariant")
    starter_relic: str | None = Field(default=None, alias="starterRelic")
    owned_variants: int | None = Field(default=None, alias="ownedVariants")
    total_variants: int | None = Field(default=None, alias="totalVariants")
    owned_families: int | None = Field(default=None, alias="ownedFamilies")
    total_families: int | None = Field(default=None, alias="totalFamilies")
    completion_percent: float | None = Field(default=None, alias="completionPercent")
    currency: list[SpriteCurrencyDto] | None = None
    sprites: list[SpriteCollectionFamilyDto] | None = None

class SpriteCollectionVariantDto(FNModel):
    id: str | None = None
    variant: str | None = None
    name: str | None = None
    rarity: str | None = None
    images: SpriteImagesDto | None = None
    drop_chance_percent: float | None = Field(default=None, alias="dropChancePercent")
    spawn_chance_percent: float | None = Field(default=None, alias="spawnChancePercent")
    owned: bool | None = None
    count: int | None = None
    xp: int | None = None
    mastered: bool | None = None

class SpriteCurrencyDto(FNModel):
    item: str | None = None
    count: int | None = None

class SpriteEventDto(FNModel):
    name: str | None = None
    weights: dict[str, float] | None = None

class SpriteFamilyDto(FNModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None
    dex_number: int | None = Field(default=None, alias="dexNumber")
    rarity: str | None = None
    acquisition_hint: str | None = Field(default=None, alias="acquisitionHint")
    extract_reward_loot_tier: str | None = Field(default=None, alias="extractRewardLootTier")
    images: SpriteImagesDto | None = None
    tags: list[str] | None = None
    boons: list[SpriteBoonRefDto] | None = None
    spawn_weight: float | None = Field(default=None, alias="spawnWeight")
    spawn_chance_percent: float | None = Field(default=None, alias="spawnChancePercent")
    variants: list[SpriteVariantDto] | None = None

class SpriteImagesDto(FNModel):
    icon: str | None = None
    icon_large: str | None = Field(default=None, alias="iconLarge")

class SpriteLevelDto(FNModel):
    level: int | None = None
    xp: float | None = None

class SpriteSharePublishResultDto(FNModel):
    account_id: str | None = Field(default=None, alias="accountId")
    display_name: str | None = Field(default=None, alias="displayName")
    visibility: str | None = None
    owned_variants: int | None = Field(default=None, alias="ownedVariants")
    total_variants: int | None = Field(default=None, alias="totalVariants")
    completion_percent: float | None = Field(default=None, alias="completionPercent")
    auto_refresh: bool | None = Field(default=None, alias="autoRefresh")
    snapshot_generated_at: str | None = Field(default=None, alias="snapshotGeneratedAt")

class SpriteSpawnEntryDto(FNModel):
    family: str | None = None
    item_definition: str | None = Field(default=None, alias="itemDefinition")
    weight: float | None = None
    spawn_chance_percent: float | None = Field(default=None, alias="spawnChancePercent")
    variants: list[SpriteSpawnVariantDto] | None = None

class SpriteSpawnListDto(FNModel):
    id: str | None = None
    table: str | None = None
    total_weight: float | None = Field(default=None, alias="totalWeight")
    entries: list[SpriteSpawnEntryDto] | None = None
    by_rarity: list[SpriteSpawnRarityDto] | None = Field(default=None, alias="byRarity")

class SpriteSpawnRarityDto(FNModel):
    rarity: str | None = None
    sprites: int | None = None
    weight: float | None = None
    share_percent: float | None = Field(default=None, alias="sharePercent")

class SpriteSpawnVariantDto(FNModel):
    id: str | None = None
    variant: str | None = None
    item_definition: str | None = Field(default=None, alias="itemDefinition")
    weight: float | None = None
    spawn_chance_percent: float | None = Field(default=None, alias="spawnChancePercent")
    chance_within_family_percent: float | None = Field(default=None, alias="chanceWithinFamilyPercent")

class SpriteVariantDto(FNModel):
    id: str | None = None
    variant: str | None = None
    name: str | None = None
    rarity: str | None = None
    enabled: bool | None = None
    images: SpriteImagesDto | None = None
    base_weight: float | None = Field(default=None, alias="baseWeight")
    weight: float | None = None
    drop_chance_percent: float | None = Field(default=None, alias="dropChancePercent")
    spawn_weight: float | None = Field(default=None, alias="spawnWeight")
    spawn_chance_percent: float | None = Field(default=None, alias="spawnChancePercent")
    boons: list[SpriteBoonRefDto] | None = None

class SpriteVersionDto(FNModel):
    version: str | None = None
    generated: str | None = None
    is_current: bool | None = Field(default=None, alias="isCurrent")
    family_count: int | None = Field(default=None, alias="familyCount")

class SpritesResponseDto(FNModel):
    game_version: str | None = Field(default=None, alias="gameVersion")
    generated: str | None = None
    hotfix_applied: bool | None = Field(default=None, alias="hotfixApplied")
    is_current: bool | None = Field(default=None, alias="isCurrent")
    sprites: list[SpriteFamilyDto] | None = None
    level_up_curve: list[SpriteLevelDto] | None = Field(default=None, alias="levelUpCurve")
    events: list[SpriteEventDto] | None = None
    spawn_lists: list[SpriteSpawnListDto] | None = Field(default=None, alias="spawnLists")

class StatTotalDto(FNModel):
    total: float | None = None
    per_game: float | None = Field(default=None, alias="perGame")

class TeamEventGameDto(FNModel):
    game: int | None = None
    session_id: str | None = Field(default=None, alias="sessionId")
    end_time: str | None = Field(default=None, alias="endTime")
    stats: dict[str, float] | None = None

class TeamEventStatsDetailDto(FNModel):
    leaderboard_rank: int | None = Field(default=None, alias="leaderboardRank")
    points_earned: int | None = Field(default=None, alias="pointsEarned")
    games_played: int | None = Field(default=None, alias="gamesPlayed")
    team_account_ids: list[str] | None = Field(default=None, alias="teamAccountIds")
    team_account_display_names: list[str] | None = Field(default=None, alias="teamAccountDisplayNames")
    stats: dict[str, StatTotalDto] | None = None
    games: list[TeamEventGameDto] | None = None

class TeamEventStatsDto(FNModel):
    event_id: str | None = Field(default=None, alias="eventId")
    event_window_id: str | None = Field(default=None, alias="eventWindowId")
    team_identifier: str | None = Field(default=None, alias="teamIdentifier")
    stat_key: str | None = Field(default=None, alias="statKey")
    stat_rank: int | None = Field(default=None, alias="statRank")
    total_teams: int | None = Field(default=None, alias="totalTeams")
    updated_time: str | None = Field(default=None, alias="updatedTime")
    team: TeamEventStatsDetailDto | None = None

class UnverifiedRequirementDto(FNModel):
    type: str | None = None
    key: str | None = None
    label: str | None = None
    description: str | None = None
    threshold: float | None = None
    estimated_current_level: float | None = Field(default=None, alias="estimatedCurrentLevel")
    current_level: int | None = Field(default=None, alias="currentLevel")
    status: str | None = None
    estimated_met: bool | None = Field(default=None, alias="estimatedMet")

class VerifiedRequirementDto(FNModel):
    token: str | None = None
    label: str | None = None
    type: str | None = None
    awarded_by: list[Any] | None = Field(default=None, alias="awardedBy")
    token_group: str | None = Field(default=None, alias="tokenGroup")
    met: bool | None = None

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
    weapon_actor_class: str | None = Field(default=None, alias="weaponActorClass")
    stats: Any | None = None
    images: Any | None = None


__all__ = [
    "AllNews",
    "AllSpriteCollectionsResponseDto",
    "AllSpritesResponseDto",
    "BattlePassCatalog",
    "BattlePassPage",
    "BattlePassPrice",
    "BattlePassReward",
    "BattlePassSeasonDto",
    "CashPrizePayoutDto",
    "CashPrizeRankDto",
    "CashPrizeScoringDto",
    "CompleteOAuthRequest",
    "CosmeticDto",
    "CosmeticDtoPaginatedResultDto",
    "CosmeticImageSetDto",
    "CosmeticImagesDto",
    "CosmeticIntroductionDto",
    "CosmeticMediaDto",
    "CosmeticMediaDtoPaginatedResultDto",
    "CosmeticVariantMediaDto",
    "CosmeticVideoDto",
    "CosmeticVideoSourceDto",
    "EpicEventDto",
    "EpicEventMetadataDto",
    "EpicEventWindowDto",
    "EventLeaderboardDto",
    "EventLeaderboardEntryDto",
    "EventMatchDto",
    "EventSessionDto",
    "EventStatRankingDto",
    "EventStatsLeaderboardDto",
    "EventTokenEligibilityDto",
    "ExchangeCodeRequest",
    "GlobalEventDto",
    "InitiateRequest",
    "LinkAccountRequest",
    "LinkRequest",
    "MapCameraDto",
    "MapDataDto",
    "MapHistoryEntryDto",
    "MapWorldBoundsDto",
    "NewsButton",
    "NewsFeed",
    "NewsImage",
    "NewsMotd",
    "NewsNotice",
    "PatchInfoDto",
    "PlayerTokenAccountDto",
    "PlayerTokensDto",
    "PlayerWindowStandingDto",
    "PoiDto",
    "PowerRankingArchiveDto",
    "PowerRankingEntryDto",
    "PowerRankingSearchDto",
    "PowerRankingSearchResultDto",
    "PowerRankingsPageDto",
    "ProblemDetails",
    "PublishCollectionRequest",
    "QuestBundleDefinition",
    "QuestDefinition",
    "QuestDefinitionResult",
    "QuestDefinitionsPage",
    "QuestObjectiveDefinition",
    "QuestRewardDefinition",
    "RarityDefinitionDto",
    "RefreshDeviceRequest",
    "RefreshTokenRequest",
    "RegisterAccountRequest",
    "SeasonEntryDto",
    "SharedSpriteCollectionDto",
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
    "SpriteBoonDto",
    "SpriteBoonRefDto",
    "SpriteCollectionFamilyDto",
    "SpriteCollectionResponseDto",
    "SpriteCollectionVariantDto",
    "SpriteCurrencyDto",
    "SpriteEventDto",
    "SpriteFamilyDto",
    "SpriteImagesDto",
    "SpriteLevelDto",
    "SpriteSharePublishResultDto",
    "SpriteSpawnEntryDto",
    "SpriteSpawnListDto",
    "SpriteSpawnRarityDto",
    "SpriteSpawnVariantDto",
    "SpriteVariantDto",
    "SpriteVersionDto",
    "SpritesResponseDto",
    "StatTotalDto",
    "TeamEventGameDto",
    "TeamEventStatsDetailDto",
    "TeamEventStatsDto",
    "UnverifiedRequirementDto",
    "VerifiedRequirementDto",
    "WeaponListItemDto",
]

for _m in list(__all__):
    globals()[_m].model_rebuild()
