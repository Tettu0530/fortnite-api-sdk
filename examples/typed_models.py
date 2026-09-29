"""Examples of the typed responses and resources added in 0.2.0.

Run with: FN_API_KEY=... uv run python examples/typed_models.py
"""

import asyncio
import os

from fortnite_api import AsyncFortniteAPI, FortniteAPI, FortniteAPIError
from fortnite_api.models import BattlePassCatalog, PowerRankingsPageDto

API_KEY = os.environ.get("FN_API_KEY", "your-api-key")


def sync_demo() -> None:
    with FortniteAPI(api_key=API_KEY) as client:
        print("api version:", client.health_version())

        # Battle Pass v2 (typed)
        bp: BattlePassCatalog = client.battlepass.get()
        print("battle pass season:", bp.season, "pages:", len(bp.pages or []))
        seasons = client.battlepass.get_seasons()
        print("seasons with a pass:", [s.season for s in seasons])

        # Power Rankings (moved from client.tournaments in 0.1.x)
        top: PowerRankingsPageDto = client.power_rankings.get_leaderboard(page=0)
        for entry in (top.entries or [])[:5]:
            print(f"  #{entry.rank}", entry.team_account_display_names, entry.points_earned)
        found = client.power_rankings.search(q="nin", limit=3)
        print("search hits:", found.total)

        # Tournaments (typed)
        for event in client.tournaments.get_current()[:3]:
            print("event:", event.id, event.short_title)

        # News
        br = client.news.get_br(lang="en")
        print("br motds:", len(br.motds or []))
        print("notices:", len(client.news.get_notices()))

        # Sprites
        catalog = client.sprites.get()
        print("sprite families:", len(catalog.sprites or []), "version:", catalog.game_version)

        # Quest definitions
        quests = client.quests.get_definitions(limit=5)
        print("quest definitions:", quests.total)

        # Models convert back to the API's JSON shape
        if top.entries:
            print(top.entries[0].model_dump(by_alias=True, exclude_none=True))

        try:
            client.sprites.get_shared_collection("SomePlayer")
        except FortniteAPIError as e:
            print("shared collection:", e.status, e.message)


async def async_demo() -> None:
    async with AsyncFortniteAPI(api_key=API_KEY) as client:
        weapons = await client.weapons.get(rarity="legendary")
        if weapons and weapons[0].id:
            weapon = await client.weapons.get_by_id(weapons[0].id)
            print("weapon:", weapon.display_name, weapon.ammo_type)
        lootpool = await client.weapons.get_lootpool(gamemode="br")
        print("lootpool loaded:", lootpool is not None)


if __name__ == "__main__":
    sync_demo()
    asyncio.run(async_demo())
