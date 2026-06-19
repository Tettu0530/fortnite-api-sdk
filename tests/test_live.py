from __future__ import annotations

import os

import pytest

from fortnite_api import AsyncFortniteAPI, FortniteAPI
from fortnite_api.models import CosmeticDtoPaginatedResultDto, SeasonEntryDto, ShopResponseDto

API_KEY = os.environ.get("FN_API_KEY")
pytestmark = pytest.mark.skipif(not API_KEY, reason="set FN_API_KEY to run live tests")


def test_health():
    with FortniteAPI(api_key=API_KEY) as client:
        assert client.health()["status"] == "ok"


def test_typed_responses():
    with FortniteAPI(api_key=API_KEY) as client:
        assert isinstance(client.shop.get_current(lang="en"), ShopResponseDto)
        assert isinstance(client.calendar.get_season(), SeasonEntryDto)
        page = client.cosmetics.get_all(page=1, page_size=2)
        assert isinstance(page, CosmeticDtoPaginatedResultDto)
        assert page.total and page.total > 0
        weapons = client.weapons.get()
        assert weapons and weapons[0].display_name


def test_account_lookup_ninja():
    with FortniteAPI(api_key=API_KEY) as client:
        account = client.account.get_by_display_name("Ninja")
        assert account["id"] == "4735ce9132924caf8a5b17789b40f79c"


async def test_async_parity():
    async with AsyncFortniteAPI(api_key=API_KEY) as client:
        season = await client.calendar.get_season()
        assert isinstance(season, SeasonEntryDto)
