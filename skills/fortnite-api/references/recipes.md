# Recipes

End-to-end programs that use only real SDK methods. Each one was type-checked with `mypy --strict`
against fortnite-api-sdk 0.2.0. All read the key from `FORTNITE_API_KEY`.

## Contents

1. Daily item shop digest
2. Tournament leaderboard for a window, with pagination
3. Player lookup and stats
4. Async concurrent fetches with `asyncio.gather`
5. Parsing a local replay file
6. OAuth device-code flow, then a token-only call

## 1. Daily item shop digest

Typed model traversal with `or []` guards. Works on the free plan.

```python
"""Daily item shop digest, grouped by section (works on the free plan)."""

import os
from collections import defaultdict

from fortnite_api import FortniteAPI, FortniteAPIError


def main() -> None:
    with FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"]) as client:
        try:
            shop = client.shop.get_current(lang="en")
        except FortniteAPIError as err:
            raise SystemExit(f"Could not load the shop: {err}") from err

        sections: dict[str, list[str]] = defaultdict(list)
        for storefront in shop.storefronts or []:
            for entry in storefront.catalog_entries or []:
                price = next((p.final_price for p in entry.prices or [] if p.final_price is not None), None)
                name = entry.title or entry.dev_name or entry.offer_id or "?"
                label = f"{name} - {price} V-Bucks" if price is not None else name
                sections[entry.section_display_name or storefront.name or "Other"].append(label)

        print(f"Item shop (expires {shop.expiration})")
        for section, items in sorted(sections.items()):
            print(f"\n## {section} ({len(items)})")
            for item in sorted(items):
                print(f"- {item}")


if __name__ == "__main__":
    main()
```

## 2. Tournament leaderboard for a window, with pagination

Finds an event window from `tournaments.get_current()`, pages until `total_pages`, then resolves account IDs to display names in batches of 100. `account.get_display_names` returns raw JSON, so the shape is handled defensively. Requires a `pro` or `custom` plan.

```python
"""Full leaderboard for one tournament window, with pagination and display names."""

import os
from typing import Any

from fortnite_api import FortniteAPI
from fortnite_api.models import EventLeaderboardEntryDto


def fetch_all_entries(
    client: FortniteAPI, event_id: str, window_id: str, max_pages: int = 50
) -> list[EventLeaderboardEntryDto]:
    entries: list[EventLeaderboardEntryDto] = []
    page = 0
    while page < max_pages:
        lb = client.tournaments.get_leaderboard(event_id=event_id, event_window_id=window_id, page=page)
        entries.extend(lb.entries or [])
        page += 1
        if lb.total_pages is None or page >= lb.total_pages:
            break
    return entries


def display_names(client: FortniteAPI, account_ids: list[str]) -> dict[str, str]:
    """account.get_display_names returns raw JSON - normalise it defensively."""
    names: dict[str, str] = {}
    for start in range(0, len(account_ids), 100):  # bulk lookups are capped at 100 ids
        raw: Any = client.account.get_display_names(account_ids[start : start + 100])
        rows = raw if isinstance(raw, list) else (raw or {}).get("accounts", [])
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                names[row["id"]] = row.get("displayName") or row["id"]
    return names


def main() -> None:
    with FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"]) as client:
        # 1. Pick an event window from the current tournament list.
        events = client.tournaments.get_current()
        windows: list[tuple[str, str]] = []
        for tournament in events:
            for region_events in (tournament.regions or {}).values():
                for event in region_events:
                    for window in event.event_windows or []:
                        if event.event_id and window.event_window_id:
                            windows.append((event.event_id, window.event_window_id))
        if not windows:
            raise SystemExit("No tournament windows found")
        event_id, window_id = windows[0]  # in real code, pick by name / region / begin_time

        # 2. Page through the leaderboard.
        entries = fetch_all_entries(client, event_id, window_id)

        # 3. Resolve account ids to names for the top 20.
        top = sorted(entries, key=lambda e: e.rank or 10**9)[:20]
        ids = sorted({aid for e in top for aid in e.team_account_ids or []})
        names = display_names(client, ids)
        for e in top:
            team = ", ".join(names.get(a, a) for a in e.team_account_ids or [])
            rank = f"{e.rank:>5}" if e.rank is not None else "    ?"
            print(f"#{rank}  {e.points_earned or 0:>4} pts  {team}")


if __name__ == "__main__":
    main()
```

## 3. Player lookup and stats

Name -> account ID -> stats. `stats.get` and `profile.get_ranked` are untyped, so the recipe prints the raw JSON first; build on the keys you actually see. `power_rankings.get_from_archive` is typed and needs no user token.

```python
"""Look up a player by name (Epic or console) and print stats and ranked progress."""

import json
import os
import sys
from typing import Any

from fortnite_api import FortniteAPI, FortniteAPIError


def resolve_account_id(client: FortniteAPI, name: str, platform: str | None = None) -> str | None:
    try:
        if platform:  # "psn", "xbl", "steam", "nintendo", "twitch", "github"
            account: Any = client.account.get_by_external_display_name(platform, name, case_insensitive=True)
        else:
            account = client.account.get_by_display_name(name)
    except FortniteAPIError as err:
        if err.status == 404:
            return None
        raise
    if isinstance(account, list):  # external lookups may return several matches
        account = account[0] if account else {}
    return account.get("id") if isinstance(account, dict) else None


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "Ninja"
    with FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"]) as client:
        account_id = resolve_account_id(client, name)
        if account_id is None:
            raise SystemExit(f"No account named {name!r}")

        stats: Any = client.stats.get(account_id)  # raw JSON - inspect before relying on keys
        print(json.dumps(stats, indent=2)[:2000])

        ranked: Any = client.profile.get_ranked(account_id=account_id)
        print(json.dumps(ranked, indent=2)[:2000])

        archive = client.power_rankings.get_from_archive(account_id)  # typed, no user token needed
        print("Power Ranking:", archive.model_dump(by_alias=True))


if __name__ == "__main__":
    main()
```

## 4. Async concurrent fetches with `asyncio.gather`

One `AsyncFortniteAPI` shared by all tasks, `return_exceptions=True` for independent calls, and a semaphore for per-player fan-out.

```python
"""Fetch several independent resources concurrently, and fan out per-player calls with a limit."""

import asyncio
import os
from typing import Any

from fortnite_api import AsyncFortniteAPI, FortniteAPIError


async def main() -> None:
    async with AsyncFortniteAPI(api_key=os.environ["FORTNITE_API_KEY"]) as client:
        # Independent calls: gather them. return_exceptions keeps one failure from hiding the rest.
        shop, season, news, weapons = await asyncio.gather(
            client.shop.get_current(),
            client.calendar.get_season(),
            client.news.get_br(lang="en"),
            client.weapons.get(),
            return_exceptions=True,
        )
        for label, result in [("shop", shop), ("season", season), ("news", news), ("weapons", weapons)]:
            if isinstance(result, BaseException):
                print(f"{label}: failed - {result}")
        if not isinstance(season, BaseException):
            print("Season", season.season_number, "ends", season.season_date_end)

        # Fan-out: bound concurrency so a long id list does not hammer the API.
        account_ids = ["accountId1", "accountId2", "accountId3"]
        limit = asyncio.Semaphore(5)

        async def stats_for(account_id: str) -> tuple[str, Any]:
            async with limit:
                try:
                    return account_id, await client.stats.get(account_id)
                except FortniteAPIError as err:
                    return account_id, err

        for account_id, stats in await asyncio.gather(*(stats_for(a) for a in account_ids)):
            print(account_id, "error" if isinstance(stats, FortniteAPIError) else "ok")


if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Parsing a local replay file

`parse_stats` works on the `free` plan; `parse_lobby` requires `pro` or `custom`. Start with the narrow stats parse, then fetch the lobby. Longer timeout for big files; cache results because parsing consumes quota. For a tournament match you only have an ID for, use `client.replays.parse_stats(match_id)` / `parse_lobby(match_id)` instead.

```python
"""Parse a local .replay file: narrow stats first, then the lobby for per-player detail."""

import json
import os
import sys
from pathlib import Path
from typing import Any

from fortnite_api import FortniteAPI, FortniteAPIError


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "match.replay")
    # Parsing large replays can exceed the default 30 s timeout.
    with FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"], timeout=180.0) as client:
        try:
            stats: Any = client.parsing.parse_stats(str(path))  # path, bytes, or open binary file
        except FortniteAPIError as err:
            raise SystemExit(f"Parsing failed: {err} {err.data}") from err
        print(json.dumps(stats, indent=2)[:1500])

        with path.open("rb") as handle:
            lobby: Any = client.parsing.parse_lobby(handle, filename=path.name)

        out = path.with_suffix(".lobby.json")
        out.write_text(json.dumps(lobby, indent=2))  # cache it: parsing costs quota
        print(f"Saved lobby data to {out}")


if __name__ == "__main__":
    main()
```

## 6. OAuth device-code flow, then a token-only call

The OAuth responses are untyped and their exact keys are not in the spec, so the recipe prints the key names and looks up the token defensively. Store the returned device auth securely to re-authenticate later with `oauth.refresh_device`.

```python
"""Device-code OAuth flow: get a user token, then call a token-only endpoint."""

import os
import time
from typing import Any

from fortnite_api import FortniteAPI, FortniteAPIError


def main() -> None:
    with FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"]) as client:
        flow: Any = client.oauth.get_token()
        print("Open this URL and log in:", flow)  # the payload carries the flowId and the login URL

        auth: Any = None
        for _ in range(60):
            try:
                result: Any = client.oauth.complete({"flowId": flow["flowId"]})
            except FortniteAPIError as err:
                if err.status == 429:  # polled too fast
                    time.sleep(10)
                    continue
                if "AUTHORIZATION_PENDING" in str(err.data):  # pending reported as an error body
                    time.sleep(5)
                    continue
                raise
            # While the user has not finished, the API answers 202 AUTHORIZATION_PENDING (not an
            # exception). Inspect `result` once to learn the exact field names of the success payload.
            if isinstance(result, dict) and "AUTHORIZATION_PENDING" not in str(result):
                auth = result
                break
            time.sleep(5)
        if auth is None:
            raise SystemExit("User did not authorise in time")

        print("Auth payload keys:", sorted(auth))  # store deviceAuth securely; never log the values
        token = auth.get("accessToken") or auth.get("access_token")
        account_id = auth.get("accountId") or auth.get("account_id")
        if token and account_id:
            level: Any = client.profile.get_level(account_id=account_id, fortnite_token=token)
            print(level)


if __name__ == "__main__":
    main()
```
