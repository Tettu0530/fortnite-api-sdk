import asyncio
import os

from fortnite_api import AsyncFortniteAPI, FortniteAPI, FortniteAPIError

API_KEY = os.environ.get("FN_API_KEY", "your-api-key")


def sync_demo():
    with FortniteAPI(api_key=API_KEY) as client:
        print("health:", client.health())
        print("season:", client.calendar.get_season().season_number)

        shop = client.shop.get_current(lang="en")
        print("storefronts:", len(shop.storefronts or []))

        page = client.cosmetics.get_all(page=1, page_size=5, rarity="legendary")
        print("legendary cosmetics:", page.total)
        for item in page.data or []:
            print("  -", item.name)

        try:
            client.profile.get_ranked(display_name="Ninja")
        except FortniteAPIError as e:
            print("ranked failed:", e.status, e.message)


async def async_demo():
    async with AsyncFortniteAPI(api_key=API_KEY) as client:
        weapons = await client.weapons.get()
        print("weapons in pool:", len(weapons))
        patches = await client.weapons.get_patches()
        print("current patch:", next((p.patch for p in patches if p.is_current), None))


if __name__ == "__main__":
    sync_demo()
    asyncio.run(async_demo())
