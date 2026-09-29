---
name: fortnite-api
description: Write correct Python code against the Fortnite API at api-fortnite.com using the official `fortnite-api-sdk` package (`import fortnite_api`, `FortniteAPI` / `AsyncFortniteAPI`). Use this skill whenever the user writes, fixes, or reviews code that imports `fortnite_api` or depends on `fortnite-api-sdk`, or asks for Fortnite data in Python - item shop, cosmetics, weapons, map, news, playlists, battle pass, sprites, AES keys, Fortnite Crew, tournaments / event leaderboards, cash prizes, Power Rankings, player stats, ranked progress, account lookup, friends, quests, OAuth / x-fortnite-token, custom matches, tournament replays or .replay file parsing - even if they do not name the SDK. Also use it when upgrading code from fortnite-api-sdk 0.1.x to 0.2.x. Do NOT use it for fortnite-api.com (a different, unrelated service with its own `fortnite-api` package), other unofficial Fortnite APIs, Epic's own endpoints called directly, or the TypeScript SDK `@yaelouuu/fortnite-api`.
---

# fortnite-api-sdk (Python)

The `fortnite-api-sdk` package is a generated, fully typed client for **https://api-fortnite.com**
(base URL `https://prod.api-fortnite.com/api`). It has a sync client and an async client with
identical method names and signatures, 26 resources, 146 endpoint methods plus `health()` and
`health_version()`.

The public surface is small: `FortniteAPI`, `AsyncFortniteAPI`, `FortniteAPIError`, and the
`fortnite_api.models` module. Everything else (`_transport`, `resources`) is internal.

Before writing a call you are not sure about, open the matching reference file (see the
resource map at the end) - it lists every method's exact signature, return type and HTTP path,
extracted from the SDK source. Guessing method names is the most common way to produce broken code
with this SDK, because several names differ from the URL (for example `tournaments.get_current()`
calls `/events/global`).

## Install and API key

```bash
uv add fortnite-api-sdk        # or: pip install fortnite-api-sdk
```

The distribution is `fortnite-api-sdk`, the import name is `fortnite_api`. Python 3.10+.
Every request sends an `x-api-key` header; a free key is available at https://api-fortnite.com.
Read it from the environment rather than hard-coding it:

```python
import os
from fortnite_api import FortniteAPI

client = FortniteAPI(api_key=os.environ["FORTNITE_API_KEY"])
```

An empty `api_key` raises `ValueError` immediately.

## Creating clients

```python
from fortnite_api import FortniteAPI, AsyncFortniteAPI

# Sync - prefer the context manager so the httpx connection pool is closed
with FortniteAPI(api_key=key) as client:
    shop = client.shop.get_current()

# Async - same methods, awaited; use `async with`
async with AsyncFortniteAPI(api_key=key) as client:
    shop = await client.shop.get_current()
```

Constructor: `FortniteAPI(api_key, *, base_url=DEFAULT_BASE_URL, timeout=30.0, fortnite_token=None)`
(same for `AsyncFortniteAPI`). Without a context manager call `client.close()` /
`await client.close()`. Create one client and reuse it; do not build a client per request.

`client.health()` and `client.health_version()` hit `/health` and `/health/version` (raw JSON).

## User tokens (`x-fortnite-token`)

Some endpoints act on behalf of a specific Epic account and need that player's Fortnite OAuth access
token in the `x-fortnite-token` header. There are two ways to supply it:

- **Per call** - every endpoint method except the `parsing.*` uploads accepts a keyword-only
  `fortnite_token=` argument. Use this when one client serves several players.
- **Client-wide** - `FortniteAPI(api_key=..., fortnite_token="...")` sends it on every request.
  A per-call value wins over the client-wide one.

Tokens come from the OAuth helpers (`client.oauth.get_token()` -> user visits the URL ->
`client.oauth.complete({"flowId": ...})`), see `references/accounts-and-auth.md`. Each reference
entry has a **Token:** line when the API description states a requirement; entries without it do
not document one. Typical token-only endpoints: `quests.get`, `profile.get_level`,
`tournaments.get_tracker`, `tournaments.get_tracker_eligibility`, `tournaments.get_player`,
`tournaments.get_player_session`, `events.get_player_history`, `power_rankings.get_player`,
`fn.get_privacy` / `update_privacy` / `get_entitlement` / `request_entitlement`,
`sprites.get_collection` / `get_all_collections` / `publish_collection` / `unpublish_collection`.

When a token-free alternative exists, prefer it: `power_rankings.search()` and
`power_rankings.get_from_archive()` instead of `get_player()`;
`tournaments.get_player_window_matches()` / `events.get_player_window_standing()` instead of
`get_player_matches()`.

## Errors

Every non-2xx response raises `fortnite_api.FortniteAPIError`:

```python
from fortnite_api import FortniteAPIError

try:
    stats = client.stats.get(account_id)
except FortniteAPIError as err:
    err.status    # int HTTP status (401 bad key, 403 missing/wrong token, 404, 429 ...)
    err.message   # str - taken from the body's "error" / "title" / "detail"
    err.data      # raw error body (dict), or {"error": "Request failed"} if not JSON
    str(err)      # "[404] Not found"
```

Also: a 2xx body shaped `{"success": false, ...}` is raised as `FortniteAPIError` with
`status == 422`. Network failures and timeouts are **not** wrapped - they surface as `httpx`
exceptions (`httpx.TimeoutException`, `httpx.ConnectError`, ...), so catch `httpx.HTTPError` too
if you need resilience. Pydantic `ValidationError` is possible if the API returns a shape that
contradicts the spec, but models are lenient (all fields optional), so it is rare.

There is no built-in retry or rate limiting. For 429 or 5xx, implement backoff yourself.

## Return values

**Typed endpoints** return Pydantic v2 models from `fortnite_api.models` (the return annotation in
the reference tells you which). Rules that matter when writing code against them:

- Use **attribute access with snake_case names**: `lb.entries`, `entry.points_earned`,
  `shop.storefronts`. `lb["entries"]` raises `TypeError` - that was the 0.1.x style.
- Every field is **optional** (`X | None = None`). Guard lists with `or []` and check for `None`
  before arithmetic: `for e in lb.entries or []:`.
- The camelCase API name is the **alias** (`points_earned` <-> `pointsEarned`). Models accept either
  when constructed (`populate_by_name=True`).
- `extra="allow"`: fields the API sends that are not in the spec are kept, reachable via
  `model.model_extra` or `getattr(model, "someNewField", None)` (they keep the API's key name).
- `model.model_dump(by_alias=True)` returns the original camelCase dict - use it for JSON output or
  when porting 0.1.x dict code. `model_dump_json(by_alias=True)` for a string.
- Some methods return `list[Model]` or `dict[str, list[Model]]`; the SDK already unwraps envelopes
  like `{"status": 200, "patches": [...]}` and `{"success": true, "data": ...}` for you.

**Untyped endpoints** (annotated `-> Any`) return raw JSON (`dict` / `list`) exactly as the API
sends it, after the same envelope unwrapping. Use key access with the API's camelCase keys, and
check the shape at runtime (`print(json.dumps(x, indent=2)[:2000])`) instead of assuming keys; the
reference descriptions list the documented fields. Fully untyped resources: `account`, `aes`, `assets`, `crew`, `custom_match`, `fn`,
`friends`, `identity`, `oauth`, `parsing`, `playlists`, `profile`, `stats`, and `replays` (except
`download()`); several others mix typed and `Any` methods.

Special returns: `replays.download()` -> `bytes`; `map.get_image()` -> `str | None` (the resolved
image URL, not the image).

## Request bodies

Methods taking `body` accept either the Pydantic request model **or** a plain `dict`:

```python
from fortnite_api.models import RefreshDeviceRequest

client.oauth.refresh_device(RefreshDeviceRequest(account_id=a, device_id=d, secret=s))
client.oauth.refresh_device({"accountId": a, "deviceId": d, "secret": s})   # dict: API key names
```

Models are serialised by alias with `None` fields dropped. With a dict you must use the API's own
key names (camelCase where the API uses it). Bodies typed `Any` / `list[str]`
(`stats.get_bulk`, `profile.bulk_track_progress`, `account.bulk_external_*`) take JSON-ready
lists as shown in the references.

## Deprecations

Deprecated endpoints still work but emit `DeprecationWarning` naming the replacement:
`battlepass.get_legacy()` -> use `battlepass.get()`; `replays.parse_broadcast()` -> use
`replays.parse()` or a specific `replays.parse_*`. Do not write new code against them. In tests,
`warnings.simplefilter("error", DeprecationWarning)` turns them into failures.

## Pagination

There is no auto-paginator; loop yourself and stop on the page count the response gives you.

- Tournament / event / Power Rankings leaderboards: `page=` (the README examples start at `0`),
  response has `page` and `total_pages`. Power Rankings: 100 players per page, 100 pages.
- `cosmetics.get_all` / `get_new` / `search`: `page=` + `page_size=`, response has `page`,
  `page_size`, `total`, `total_pages`, `data` (README examples start at `page=1`).
- `stats.get_leaderboard(stat, limit=, offset=)` and `quests.get_definitions(limit=, offset=)`:
  offset-based.
- To find one player in a large leaderboard use `events.get_window_leaderboard_player()` or
  `events.get_player_window_standing(..., rank_hint=, max_pages=)` rather than paging everything.

```python
page = 0
while True:
    lb = client.tournaments.get_leaderboard(event_id=eid, event_window_id=wid, page=page)
    for e in lb.entries or []:
        ...
    page += 1
    if lb.total_pages is None or page >= lb.total_pages:
        break
```

## Plans, quotas and rate limits

The bundled OpenAPI spec tags each endpoint with the plans allowed to call it (shown as
**Plans:** in the references). On the **free** plan only these work:
`shop.get_current`, `calendar.get_season`, `battlepass.get_legacy`, `stats.get`, all ten
`account.*` methods, `replays.download` and `parsing.parse_stats`. Most other endpoints require
`pro` or `custom`; `custom_match.*`, `identity.*` and `tournaments.get_player_session` are
`custom` only. If a call is rejected (`FortniteAPIError`, typically 401/403/429) with a key that
works for other endpoints, check the plan before debugging code and tell the user which plan the
endpoint needs. The spec reflects the SDK's release; the live service is authoritative.

Replay parsing (`replays.parse*`, `parsing.*`) is charged against a per-plan parsing quota. The
`replays.*` docstrings give the cost: most parse endpoints cost 5 credits, `replays.parse_stats`
costs 1. `parsing.*` uploads also use the parsing quota, but their per-call cost is not
documented - so choose the narrowest parse method that answers the question. Some endpoints document their
own limits and caching (for example `tournaments.get_player_session` is cached 10 s and limited to
1200 requests/min per key; `oauth.complete` returns 429 if polled too fast). With the async client,
bound concurrency (e.g. `asyncio.Semaphore`) instead of firing hundreds of requests at once.

## Common pitfalls

- **0.1.x dict access.** In 0.2.x many methods return models: `lb["entries"]` -> `lb.entries`, or
  `lb.model_dump(by_alias=True)["entries"]` for a quick port.
- **Power Rankings moved** from `tournaments` to `client.power_rankings`:
  `get_power_rankings()` -> `power_rankings.get_leaderboard()`,
  `get_power_rankings_player()` -> `power_rankings.get_player()`,
  `search_power_rankings()` -> `power_rankings.search()`.
- **Battle Pass v2.** `battlepass.get(season=None)` now calls `/api/v2/battlepass`, takes `season`
  (int) instead of `lang`, and returns `BattlePassCatalog`. `battlepass.get_seasons()` lists seasons.
- **Removed:** `tournaments.get_tracker_debug()`. `cosmetics.get_all(season=, chapter=)` take `int`.
- **Keyword-only arguments.** Optional parameters (and many required-looking ones such as
  `tournaments.get_leaderboard(event_id=..., event_window_id=...)`) are keyword-only. Check the
  signature: parameters after `*` must be passed by name.
- **Forgetting `await`** on `AsyncFortniteAPI` methods returns a coroutine, not data.
- **Tokens are secrets.** Never log `fortnite_token` values or device-auth secrets.
- **Wrong service.** `fortnite-api.com` is a different API. Its community Python package
  (`fortnite-api` on PyPI) also imports as `fortnite_api` but exposes `fortnite_api.Client`, not
  `FortniteAPI`. If you see `Client(...)` or `fortnite-api` in requirements, this skill does not apply,
  and the two packages cannot be installed side by side.

## Resource map

| Resource (`client.<name>`) | What it covers | Reference |
|---|---|---|
| `shop`, `cosmetics`, `weapons`, `map`, `news`, `playlists`, `calendar`, `battlepass`, `sprites`, `aes`, `assets`, `crew` | Item shop, cosmetics catalog, weapon stats and loot pool, map/POIs/images, news & notices, playlists, season dates, Battle Pass, sprites & collections, AES keys, asset bundles, Fortnite Crew | `references/catalog.md` |
| `tournaments`, `events`, `power_rankings`, `stats`, `profile` | Tournaments and leaderboards, scoring, cash prizes, eligibility, event windows, Power Rankings, player stats and stat leaderboards, ranked / level / Habanero progress | `references/competitive.md` |
| `account`, `friends`, `oauth`, `identity`, `fn`, `quests`, `custom_match` | Account lookup (IDs, names, cross-platform), friends, OAuth flows, Discord identity links, inventory / privacy / entitlements, quests, custom-match key pushes | `references/accounts-and-auth.md` |
| `replays`, `parsing` | Tournament replays by match ID, uploading local `.replay` files for parsing | `references/replays-and-parsing.md` |
| (recipes) | End-to-end programs: shop digest, paginated tournament leaderboard, player lookup + stats, async fan-out, local replay parsing, OAuth token flow | `references/recipes.md` |

Each reference opens with guidance for its area, then lists every method with signature, return
type, HTTP path, token requirement, the top-level fields of the returned model, and a minimal
example. For nested model fields, read the class in `fortnite_api/models.py` of the installed
package (`python -c "import fortnite_api.models as m, inspect; print(inspect.getsource(m.EpicEventDto))"`).
