"""Smoke tests against the real API (https://api-fortnite.com).

These tests are marked ``live`` and are deselected by default. Run them with::

    FN_API_KEY=... uv run pytest -m live

Endpoints that need a user token additionally require ``FN_FORTNITE_TOKEN`` (and
``FN_ACCOUNT_ID`` for the account the token belongs to). The assertions check types and
shapes only, never exact values, so that normal data changes do not break the suite.
Endpoints that the API key's plan does not include (HTTP 403) are reported as skipped, not failed
(see ``tests/conftest.py``).
"""

from __future__ import annotations

import os
import re
from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest

from fortnite_api import AsyncFortniteAPI, FortniteAPI
from fortnite_api.models import (
    AllNews,
    AllSpritesResponseDto,
    BattlePassCatalog,
    BattlePassSeasonDto,
    CashPrizeScoringDto,
    CosmeticDto,
    CosmeticDtoPaginatedResultDto,
    GlobalEventDto,
    MapDataDto,
    MapHistoryEntryDto,
    NewsFeed,
    NewsNotice,
    PatchInfoDto,
    PowerRankingSearchDto,
    PowerRankingsPageDto,
    QuestDefinitionsPage,
    RarityDefinitionDto,
    SeasonEntryDto,
    ShopResponseDto,
    SpriteBoonDto,
    SpritesResponseDto,
    SpriteVersionDto,
    WeaponListItemDto,
)

API_KEY = os.environ.get("FN_API_KEY", "")
FORTNITE_TOKEN = os.environ.get("FN_FORTNITE_TOKEN", "")
ACCOUNT_ID = os.environ.get("FN_ACCOUNT_ID", "")

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not API_KEY, reason="set FN_API_KEY to run live tests"),
]
needs_token = pytest.mark.skipif(
    not (FORTNITE_TOKEN and ACCOUNT_ID),
    reason="set FN_FORTNITE_TOKEN and FN_ACCOUNT_ID to run user-token tests",
)


@pytest.fixture
def client() -> Iterator[FortniteAPI]:
    with FortniteAPI(api_key=API_KEY) as c:
        yield c


@pytest.fixture
async def aclient() -> AsyncIterator[AsyncFortniteAPI]:
    async with AsyncFortniteAPI(api_key=API_KEY) as c:
        yield c


def _all_instances(items: list[Any], cls: type) -> bool:
    return all(isinstance(item, cls) for item in items)


def _account_id(payload: Any) -> str | None:
    """Extract an account ID from whichever shape the account lookup returns."""
    if isinstance(payload, list):
        return _account_id(payload[0]) if payload else None
    if isinstance(payload, dict):
        for key in ("id", "accountId", "account_id"):
            if isinstance(payload.get(key), str):
                return str(payload[key])
        for key in ("account", "data", "result"):
            if key in payload:
                return _account_id(payload[key])
    return getattr(payload, "id", None) or getattr(payload, "account_id", None)


# --- service -------------------------------------------------------------------------------


def test_health(client: FortniteAPI) -> None:
    health = client.health()
    assert isinstance(health, dict)
    assert health.get("status") == "ok"


def test_health_version(client: FortniteAPI) -> None:
    assert isinstance(client.health_version(), dict)


# --- shop / calendar / battle pass ---------------------------------------------------------


def test_shop(client: FortniteAPI) -> None:
    shop = client.shop.get_current(lang="en")
    assert isinstance(shop, ShopResponseDto)


def test_calendar_season(client: FortniteAPI) -> None:
    season = client.calendar.get_season()
    assert isinstance(season, SeasonEntryDto)


def test_battlepass_v2(client: FortniteAPI) -> None:
    assert isinstance(client.battlepass.get(), BattlePassCatalog)


def test_battlepass_seasons(client: FortniteAPI) -> None:
    seasons = client.battlepass.get_seasons()
    assert isinstance(seasons, list)
    assert seasons
    assert _all_instances(seasons, BattlePassSeasonDto)


# --- cosmetics -----------------------------------------------------------------------------


def test_cosmetics_pagination_and_get_by_id(client: FortniteAPI) -> None:
    page = client.cosmetics.get_all(page=1, page_size=2)
    assert isinstance(page, CosmeticDtoPaginatedResultDto)
    assert page.total
    assert page.data
    assert _all_instances(page.data, CosmeticDto)
    first_id = page.data[0].id
    assert first_id
    assert isinstance(client.cosmetics.get_by_id(first_id), CosmeticDto)


def test_cosmetics_new_and_search(client: FortniteAPI) -> None:
    assert isinstance(client.cosmetics.get_new(page=1, page_size=2), CosmeticDtoPaginatedResultDto)
    assert isinstance(client.cosmetics.search("peely", page_size=2), CosmeticDtoPaginatedResultDto)


# --- weapons -------------------------------------------------------------------------------


def test_weapons_list_and_get_by_id(client: FortniteAPI) -> None:
    weapons = client.weapons.get()
    assert weapons
    assert _all_instances(weapons, WeaponListItemDto)
    weapon_id = next((w.id for w in weapons if w.id), None)
    assert weapon_id
    assert isinstance(client.weapons.get_by_id(weapon_id), WeaponListItemDto)


def test_weapons_lootpool(client: FortniteAPI) -> None:
    lootpool = client.weapons.get_lootpool()
    assert isinstance(lootpool, (dict, list))
    assert lootpool


def test_weapons_patches_and_rarities(client: FortniteAPI) -> None:
    patches = client.weapons.get_patches()
    assert patches
    assert _all_instances(patches, PatchInfoDto)
    rarities = client.weapons.get_rarities()
    assert _all_instances(rarities, RarityDefinitionDto)


# --- news / map / playlists ----------------------------------------------------------------


def test_news_all_and_br(client: FortniteAPI) -> None:
    assert isinstance(client.news.get_all(lang="en"), AllNews)
    assert isinstance(client.news.get_br(lang="en"), NewsFeed)


def test_news_festival(client: FortniteAPI) -> None:
    assert isinstance(client.news.get_festival(lang="en"), NewsFeed)


def test_news_notices(client: FortniteAPI) -> None:
    notices = client.news.get_notices(lang="en")
    assert isinstance(notices, list)
    assert _all_instances(notices, NewsNotice)


def test_map(client: FortniteAPI) -> None:
    assert isinstance(client.map.get(), MapDataDto)
    history = client.map.get_history()
    assert isinstance(history, list)
    assert _all_instances(history, MapHistoryEntryDto)
    image = client.map.get_image()
    assert isinstance(image, str)
    assert image.startswith("http")


def test_playlists(client: FortniteAPI) -> None:
    assert client.playlists.get_all() is not None
    assert client.playlists.get_active() is not None


# --- sprites / quests / aes ----------------------------------------------------------------


def test_sprites_catalog(client: FortniteAPI) -> None:
    assert isinstance(client.sprites.get(), SpritesResponseDto)
    assert isinstance(client.sprites.get_all(), AllSpritesResponseDto)


def test_sprites_boons_and_versions(client: FortniteAPI) -> None:
    assert _all_instances(client.sprites.get_boons(), SpriteBoonDto)
    versions = client.sprites.get_versions()
    assert versions
    assert _all_instances(versions, SpriteVersionDto)


def test_quest_definitions(client: FortniteAPI) -> None:
    page = client.quests.get_definitions(limit=5)
    assert isinstance(page, QuestDefinitionsPage)


def test_aes_keys(client: FortniteAPI) -> None:
    keys = client.aes.get_keys()
    assert isinstance(keys, dict)
    assert keys


# --- tournaments / power rankings / account ------------------------------------------------


def test_tournaments_current(client: FortniteAPI) -> None:
    events = client.tournaments.get_current()
    assert isinstance(events, list)
    assert _all_instances(events, GlobalEventDto)


def test_tournaments_cashprizes(client: FortniteAPI) -> None:
    prizes = client.tournaments.get_cashprizes()
    assert isinstance(prizes, dict)
    for window_id, scoring in prizes.items():
        assert isinstance(window_id, str)
        assert _all_instances(scoring, CashPrizeScoringDto)


def test_tournaments_scoring(client: FortniteAPI) -> None:
    assert client.tournaments.get_scoring() is not None


def test_power_rankings_leaderboard(client: FortniteAPI) -> None:
    assert isinstance(client.power_rankings.get_leaderboard(page=1), PowerRankingsPageDto)


def test_power_rankings_search(client: FortniteAPI) -> None:
    assert isinstance(client.power_rankings.search(q="bugha", limit=5), PowerRankingSearchDto)


def test_account_lookup_by_display_name(client: FortniteAPI) -> None:
    account = client.account.get_by_display_name("Ninja")
    assert account
    # Display names can move between accounts, so only the shape of the ID is checked.
    account_id = _account_id(account)
    assert account_id is not None
    assert re.fullmatch(r"[0-9a-f]{32}", account_id)


# --- async ---------------------------------------------------------------------------------


async def test_async_parity(aclient: AsyncFortniteAPI) -> None:
    assert isinstance(await aclient.calendar.get_season(), SeasonEntryDto)
    weapons = await aclient.weapons.get()
    assert _all_instances(weapons, WeaponListItemDto)


# --- user token (x-fortnite-token) ---------------------------------------------------------


@needs_token
def test_token_entitlement(client: FortniteAPI) -> None:
    assert client.fn.get_entitlement(fortnite_token=FORTNITE_TOKEN) is not None


@needs_token
def test_token_profile_level(client: FortniteAPI) -> None:
    assert client.profile.get_level(account_id=ACCOUNT_ID, fortnite_token=FORTNITE_TOKEN) is not None


@needs_token
def test_token_tournament_tracker(client: FortniteAPI) -> None:
    assert client.tournaments.get_tracker(account_id=ACCOUNT_ID, fortnite_token=FORTNITE_TOKEN) is not None
