from __future__ import annotations

from typing import Any

from ._transport import DEFAULT_BASE_URL, AsyncTransport, SyncTransport
from .resources import (
    AccountResource,
    AsyncAccountResource,
    AesResource,
    AsyncAesResource,
    AssetsResource,
    AsyncAssetsResource,
    BattlePassResource,
    AsyncBattlePassResource,
    CalendarResource,
    AsyncCalendarResource,
    CosmeticsResource,
    AsyncCosmeticsResource,
    CrewResource,
    AsyncCrewResource,
    CustomMatchResource,
    AsyncCustomMatchResource,
    EventsResource,
    AsyncEventsResource,
    FNResource,
    AsyncFNResource,
    FriendsResource,
    AsyncFriendsResource,
    IdentityResource,
    AsyncIdentityResource,
    MapResource,
    AsyncMapResource,
    NewsResource,
    AsyncNewsResource,
    OAuthResource,
    AsyncOAuthResource,
    ParsingResource,
    AsyncParsingResource,
    PlaylistsResource,
    AsyncPlaylistsResource,
    PowerRankingsResource,
    AsyncPowerRankingsResource,
    ProfileResource,
    AsyncProfileResource,
    QuestsResource,
    AsyncQuestsResource,
    ReplaysResource,
    AsyncReplaysResource,
    ShopResource,
    AsyncShopResource,
    SpritesResource,
    AsyncSpritesResource,
    StatsResource,
    AsyncStatsResource,
    TournamentsResource,
    AsyncTournamentsResource,
    WeaponsResource,
    AsyncWeaponsResource,
)

class FortniteAPI:
    """Client for the Fortnite API (https://api-fortnite.com)."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
    ) -> None:
        self._t = SyncTransport(api_key, base_url, timeout, fortnite_token)
        self.account = AccountResource(self._t)
        self.aes = AesResource(self._t)
        self.assets = AssetsResource(self._t)
        self.battlepass = BattlePassResource(self._t)
        self.calendar = CalendarResource(self._t)
        self.cosmetics = CosmeticsResource(self._t)
        self.crew = CrewResource(self._t)
        self.custom_match = CustomMatchResource(self._t)
        self.events = EventsResource(self._t)
        self.fn = FNResource(self._t)
        self.friends = FriendsResource(self._t)
        self.identity = IdentityResource(self._t)
        self.map = MapResource(self._t)
        self.news = NewsResource(self._t)
        self.oauth = OAuthResource(self._t)
        self.parsing = ParsingResource(self._t)
        self.playlists = PlaylistsResource(self._t)
        self.power_rankings = PowerRankingsResource(self._t)
        self.profile = ProfileResource(self._t)
        self.quests = QuestsResource(self._t)
        self.replays = ReplaysResource(self._t)
        self.shop = ShopResource(self._t)
        self.sprites = SpritesResource(self._t)
        self.stats = StatsResource(self._t)
        self.tournaments = TournamentsResource(self._t)
        self.weapons = WeaponsResource(self._t)

    def health(self) -> Any:
        """``GET /health`` - service health check."""
        return self._t.request("GET", "/health", None)

    def health_version(self) -> Any:
        """``GET /health/version`` - deployed API version information."""
        return self._t.request("GET", "/health/version", None)

    def close(self) -> None:
        self._t.close()

    def __enter__(self) -> FortniteAPI:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncFortniteAPI:
    """Client for the Fortnite API (https://api-fortnite.com)."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
    ) -> None:
        self._t = AsyncTransport(api_key, base_url, timeout, fortnite_token)
        self.account = AsyncAccountResource(self._t)
        self.aes = AsyncAesResource(self._t)
        self.assets = AsyncAssetsResource(self._t)
        self.battlepass = AsyncBattlePassResource(self._t)
        self.calendar = AsyncCalendarResource(self._t)
        self.cosmetics = AsyncCosmeticsResource(self._t)
        self.crew = AsyncCrewResource(self._t)
        self.custom_match = AsyncCustomMatchResource(self._t)
        self.events = AsyncEventsResource(self._t)
        self.fn = AsyncFNResource(self._t)
        self.friends = AsyncFriendsResource(self._t)
        self.identity = AsyncIdentityResource(self._t)
        self.map = AsyncMapResource(self._t)
        self.news = AsyncNewsResource(self._t)
        self.oauth = AsyncOAuthResource(self._t)
        self.parsing = AsyncParsingResource(self._t)
        self.playlists = AsyncPlaylistsResource(self._t)
        self.power_rankings = AsyncPowerRankingsResource(self._t)
        self.profile = AsyncProfileResource(self._t)
        self.quests = AsyncQuestsResource(self._t)
        self.replays = AsyncReplaysResource(self._t)
        self.shop = AsyncShopResource(self._t)
        self.sprites = AsyncSpritesResource(self._t)
        self.stats = AsyncStatsResource(self._t)
        self.tournaments = AsyncTournamentsResource(self._t)
        self.weapons = AsyncWeaponsResource(self._t)

    async def health(self) -> Any:
        """``GET /health`` - service health check."""
        return await self._t.request("GET", "/health", None)

    async def health_version(self) -> Any:
        """``GET /health/version`` - deployed API version information."""
        return await self._t.request("GET", "/health/version", None)

    async def close(self) -> None:
        await self._t.close()

    async def __aenter__(self) -> AsyncFortniteAPI:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

