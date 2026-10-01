# Fortnite API SDK (Python)

Python SDK for the Fortnite API at **[api-fortnite.com](https://api-fortnite.com)** — sync **and** async, fully typed.

## Installation

```bash
uv add fortnite-api-sdk        # or: pip install fortnite-api-sdk
```

The import name is `fortnite_api`:

```python
from fortnite_api import FortniteAPI, AsyncFortniteAPI, FortniteAPIError
```

## API Key

Acquire your API Key by creating a Free Account here: https://api-fortnite.com

## Quick Start

```python
from fortnite_api import FortniteAPI

client = FortniteAPI(api_key="your-api-key-here")

# Get current shop
shop = client.shop.get_current()

# Get tournament leaderboard
leaderboard = client.tournaments.get_leaderboard(
    event_id="epicgames_S37_BlitzCupsAllPlatforms_BR",
    event_window_id="S37_BlitzCupsAllPlatforms_Event1_BR",
    page=0,
)

client.close()
```

The client is also a context manager (`with FortniteAPI(...) as client:`), which closes the underlying HTTP connection for you.

### Async

Every method exists on `AsyncFortniteAPI` with an identical signature — just `await` it:

```python
import asyncio
from fortnite_api import AsyncFortniteAPI

async def main():
    async with AsyncFortniteAPI(api_key="your-api-key-here") as client:
        shop = await client.shop.get_current()
        weapons = await client.weapons.get(rarity="mythic")
        print(len(shop.storefronts or []), len(weapons))

asyncio.run(main())
```

All examples below use the sync client; prefix calls with `await` for the async one.

## Features

- ✅ Sync **and** async clients with method-for-method parity
- ✅ Typed Pydantic responses for most endpoints (every endpoint whose OpenAPI 200 response declares a schema); raw JSON for the rest
- ✅ Request bodies accept either the Pydantic request model or a plain `dict`
- ✅ `DeprecationWarning` for endpoints the API marks as deprecated
- ✅ Typed exception hierarchy under `FortniteAPIError` (`AuthError`, `RateLimitError`, `ServerError`, ...)
- ✅ Safe by default: redirects are not followed, path parameters are URL-encoded, credentials never appear in reprs or errors
- ✅ Opt-in retries with backoff for idempotent requests (`RetryConfig`)
- ✅ Pluggable transports (`transport=`) with a public protocol and reusable response interpretation
- ✅ Support for all Fortnite API endpoints (26 resources, 146 methods + `health()` / `health_version()`)
- ✅ Built-in OAuth flow helpers
- ✅ Optional per-call user token (`x-fortnite-token`)

---

## 📚 API Resources

### Shop

Access the Fortnite Item Shop and Battle Pass data.

```python
# Get current item shop (-> ShopResponseDto)
shop = client.shop.get_current(lang="en")
for storefront in shop.storefronts or []:
    print(storefront.name)

# Battle Pass (v2, -> BattlePassCatalog)
battle_pass = client.battlepass.get()
print(battle_pass.season, len(battle_pass.pages or []))

# An archived season's pass
old_pass = client.battlepass.get(season=35)

# Every season with a Battle Pass (-> list[BattlePassSeasonDto])
seasons = client.battlepass.get_seasons()
current = next(s for s in seasons if s.is_current)
```

> `client.battlepass.get_legacy(lang="en")` wraps the old `/api/v1/shop/battlepass` endpoint. It is deprecated by the API and emits a `DeprecationWarning`; please use `battlepass.get()` instead.

---

### Tournaments

Comprehensive tournament data including leaderboards, events, and eligibility tracking.

#### Get Current Events
```python
events = client.tournaments.get_current()
history = client.tournaments.get_global_history()
```

#### Get Tournament Leaderboard
```python
# -> EventLeaderboardDto
leaderboard = client.tournaments.get_leaderboard(
    event_id="epicgames_S37_BlitzCupsAllPlatforms_BR",
    event_window_id="S37_BlitzCupsAllPlatforms_Event1_BR",
    page=0,
)
for entry in leaderboard.entries or []:
    print(entry.rank, entry.score)

# Cumulative leaderboard (ID from the window's payoutTableV2[].scoreId, "cumulative:<id>")
cumulative = client.tournaments.get_leaderboard(
    event_id="epicgames_S37_BlitzCupsAllPlatforms_BR",
    event_window_id="S37_BlitzCupsAllPlatforms_Event1_BR",
    cumulative_id="cumulative:<id>",
)
```

#### Player Matches & Sessions
```python
# Recent tournament matches (x-fortnite-token required for accounts other than the service account)
matches = client.tournaments.get_player_matches(account_id, region="EU", after="2026-09-01")

# The player's current / latest match session (requires the player's own token)
session = client.tournaments.get_player_session(account_id, fortnite_token="userToken")

# A player's standing and matches in one event window (-> PlayerWindowStandingDto)
standing = client.tournaments.get_player_window_matches(
    event_id, event_window_id, account_id, rank_hint=500
)
```

#### Scoring Rules
```python
scoring = client.tournaments.get_scoring()                    # all scoring rules
window_scoring = client.tournaments.get_window_scoring(event_window_id)
```

#### Sessions, Stats & Tokens
```python
sessions = client.tournaments.get_sessions(event_id=event_id)          # -> EventSessionDto
leaders = client.tournaments.get_stat_leaders(event_id, event_window_id, "ELIMS", top=10)
team = client.tournaments.get_team_stats(event_id, event_window_id, "ELIMS", "Ninja")
tokens = client.tournaments.get_tokens(["accountId1", "accountId2"])  # -> PlayerTokensDto
```

#### Tournament Tracker (requires user token)
```python
tracker = client.tournaments.get_tracker(account_id="accountId", fortnite_token="userToken")
```

#### Check Eligibility (requires user token)
Verify if a player meets requirements for major tournaments (e.g. 14 tournaments in 180 days):

```python
eligibility = client.tournaments.get_tracker_eligibility(
    account_id="accountId",
    days=180,
    required_tournaments=14,
    fortnite_token="userToken",
)

# Per-event eligibility (token requirements verified when a user token is provided)
status = client.tournaments.check_eligibility("Ninja", "epicgames_S37_BlitzCups_BR")
```

#### Player Events (requires user token)
```python
events = client.tournaments.get_player(
    account_id="your-account-id", region="EU", platform="Windows", fortnite_token="userToken"
)
```

#### Cash Prizes
```python
prizes = client.tournaments.get_cashprizes()       # -> dict[str, list[CashPrizeScoringDto]]
window = client.tournaments.get_cashprize("S37_BlitzCupsAllPlatforms_Event1_BR")
```

---

### Power Rankings

Power Rankings now live on their own resource, `client.power_rankings` (previously on `client.tournaments`).

```python
# Global Power Rankings page (-> PowerRankingsPageDto)
top = client.power_rankings.get_leaderboard(page=0)
for entry in top.entries or []:
    print(entry.rank, entry.team_account_display_names, entry.points_earned)

# Search by display name, no user token required (-> PowerRankingSearchDto)
results = client.power_rankings.search(q="nin", limit=10)

# Archived rank for any account, no user token required (-> PowerRankingArchiveDto)
archive = client.power_rankings.get_from_archive("accountId")

# Live rank for one player (requires that player's x-fortnite-token)
player = client.power_rankings.get_player("Ninja", fortnite_token="userToken")
```

---

### Events

Event window leaderboards and player standings.

```python
# -> EventLeaderboardDto
board = client.events.get_window_leaderboard(event_id, event_window_id, page=0, round=1)

# A player's rank and the entries around it (-> list[EventLeaderboardEntryDto])
around = client.events.get_window_leaderboard_player(event_id, event_window_id, account_id="accountId")

# -> PlayerWindowStandingDto
standing = client.events.get_player_window_standing(
    event_id, event_window_id, "accountId", rank_hint=1200, max_pages=5
)

# Event participation history (requires user token)
history = client.events.get_player_history("accountId", fortnite_token="userToken")
```

---

### Quests

Access player quest progress, XP, and account level information.

```python
# Requires the user's personal Fortnite OAuth token
quests = client.quests.get("accountId", resolve=True, fortnite_token="userToken")
```

**Authentication Required**: user's Fortnite OAuth token.

#### Quest Definitions (no token required)
```python
# -> QuestDefinitionsPage
page = client.quests.get_definitions(search="eliminations", visible=True, limit=50)
for quest in page.quests or []:
    print(quest.template_id, quest.name)

# A single definition by template ID (-> QuestDefinitionResult)
quest = client.quests.get_definition("Quest:quest_s37_weekly_01")
```

---

### Stats & Profiles

Player statistics and ranked progression.

```python
# Single player stats
stats = client.stats.get("4735ce9132924caf8a5b17789b40f79c")

# Bulk stats
bulk = client.stats.get_bulk(["accountId1", "accountId2"])

# Stat leaderboard
lb = client.stats.get_leaderboard("kills", limit=100)

# Ranked progress (enriched)
ranked = client.profile.get_ranked(display_name="Ninja")
level = client.profile.get_level(account_id="accountId", fortnite_token="userToken")
tracks = client.profile.get_tracks()
```

---

### Calendar

Fortnite in-game calendar and season information.

```python
# Get current season info (-> SeasonEntryDto)
season = client.calendar.get_season()
print(season.season_number, season.season_date_begin, season.season_date_end)
```

---

### Assets / Bundles

Fortnite shop and tournament asset bundles (images, icons, rewards).

```python
shop_bundles = client.assets.get_shop_bundles()
tournament_bundles = client.assets.get_tournament_bundles()
```

---

### Weapons

Comprehensive weapon data including stats and metadata.

```python
# Get all weapons (-> list[WeaponListItemDto])
weapons = client.weapons.get(rarity="legendary", category="assault")

# Pin a specific patch by major/minor version or by date
older = client.weapons.get(major=36, minor=10)

# Single weapon (-> WeaponListItemDto)
weapon = client.weapons.get_by_id(weapons[0].id)

# Current loot pool, optionally with stats
lootpool = client.weapons.get_lootpool(gamemode="br", with_stats=True)

# Available patches (current one flagged)
patches = client.weapons.get_patches()

# Rarity definitions and colors
rarities = client.weapons.get_rarities()
```

---

### OAuth

OAuth authentication flow helpers for obtaining user tokens.

```python
# Device-code flow
flow = client.oauth.get_token()
print(flow)  # contains a flowId and a user-facing URL to authenticate

auth = client.oauth.complete(body={"flowId": flow["flowId"]})
# auth contains the access token + device auth credentials

# Authorization-code flow
url = client.oauth.get_authorize_url(redirect_uri="https://your.app/callback")
linked = client.oauth.link(body={"code": "...", "redirectUri": "https://your.app/callback"})

# Refresh
refreshed = client.oauth.refresh_token(body={"refreshToken": "..."})
silent = client.oauth.refresh_device(body={"accountId": "...", "deviceId": "...", "secret": "..."})

# Revoke device auth credentials
client.oauth.revoke_device(body={"accountId": "...", "deviceId": "...", "secret": "..."})
```

Request bodies accept either a plain `dict` or the matching Pydantic model from `fortnite_api.models`
(for example `RefreshDeviceRequest`); models are serialized with their API field names.

---

### Parsing

Parse Fortnite `.replay` files to extract match data. Accepts a path, `bytes`, or a file-like object.

```python
# Single replay — pick the detail you need
stats = client.parsing.parse_stats("match.replay")          # fast, stats only
broadcast = client.parsing.parse_broadcast("match.replay")  # everything in one call
lobby = client.parsing.parse_lobby(open("match.replay", "rb"))

# Multiple replays in one request
results = client.parsing.parse_multiple(["a.replay", "b.replay"])
```

Granular single-file methods: `parse_replay`, `parse_stats`, `parse_map`, `parse_loot`,
`parse_timeline`, `parse_zones`, `parse_lobby`, `parse_broadcast`.

---

### Replays (by Match ID)

Download and parse tournament replays straight from a match ID.

```python
raw = client.replays.download(match_id)            # -> bytes (.replay binary)
meta = client.replays.get_metadata(match_id)
parsed = client.replays.parse_stats(match_id)
tracks = client.replays.parse_tracks(match_id)
# replays.parse_broadcast() is deprecated by the API and emits a DeprecationWarning
```

---

### Account

Comprehensive account lookup with cross-platform support.

#### Lookup by Account ID
```python
account = client.account.get_by_id("4735ce9132924caf8a5b17789b40f79c")
# -> { "id", "displayName", "externalAuths" }
```

#### Lookup by Display Name
```python
account = client.account.get_by_display_name("Ninja")
```

#### Cross-Platform Lookup
Search for accounts by platform usernames (PSN, Xbox, Steam, Nintendo, Twitch, GitHub):

```python
account = client.account.get_by_external_display_name(
    "psn", "PSN_Username", case_insensitive=True
)
xbox = client.account.get_by_external_display_name("xbl", "Xbox_Gamertag")
```

**Supported platforms:** `psn`, `xbl`, `steam`, `nintendo`, `twitch`, `github`.

#### Bulk Operations
```python
# Bulk account lookup (max 100)
accounts = client.account.get_bulk(["accountId1", "accountId2", "accountId3"])

# Resolve account IDs to display names
names = client.account.get_display_names(["accountId1", "accountId2"])

# Bulk external lookups
accounts = client.account.bulk_external_display_names(
    [{"externalAuthType": "psn", "displayName": "PSNUser1"}]
)
accounts = client.account.bulk_external_ids(
    [{"externalAuthType": "psn", "externalId": "psn-id-123"}]
)
```

#### External Authentications
```python
auths = client.account.get_external_auths("accountId")
psn_auth = client.account.get_external_auth("accountId", "psn")
```

---

### News

Get Fortnite news and announcements for all game modes.

```python
br_news = client.news.get_br()                   # -> NewsFeed
stw_news = client.news.get_stw()
creative_news = client.news.get_creative()
festival_news = client.news.get_festival()
all_news = client.news.get_all(lang="en", platform="Windows")   # -> AllNews

for motd in br_news.motds or []:
    print(motd.title)

# In-game notices (-> list[NewsNotice])
notices = client.news.get_notices(lang="en")
```

---

### Cosmetics

Browse and search the complete Fortnite cosmetics catalog.

#### Get All Cosmetics
```python
# -> CosmeticDtoPaginatedResultDto (page, page_size, total, total_pages, data)
page = client.cosmetics.get_all(
    page=1, page_size=50, type="outfit", rarity="legendary", set="Dark Series"
)
print(page.total, "items")
for item in page.data or []:
    print(item.name, item.rarity)
```

#### Get / Search / New
```python
item = client.cosmetics.get_by_id("CID_123_Athena")
results = client.cosmetics.search("galaxy", type="outfit", page_size=20)
new_items = client.cosmetics.get_new(page=1, page_size=50)
```

---

### Crew

Fortnite Crew subscription pack information.

```python
current = client.crew.get_current()
history = client.crew.get_history()
```

---

### Map

Current and historical Fortnite map data.

```python
map_data = client.map.get(version="v41.00")   # -> MapDataDto (with POIs)
image_url = client.map.get_image()            # -> resolved image URL string
og_image = client.map.get_image(mode="og")   # `mode`: "br" (default), "og" or "rotating:<codename>"
history = client.map.get_history(season=1)    # -> list[MapHistoryEntryDto]
```

---

### Playlists

Fortnite playlists and game modes.

```python
all_playlists = client.playlists.get_all()
active = client.playlists.get_active()
playlist = client.playlists.get_by_id("Playlist_DefaultSolo")
```

---

### FN (Fortnite Game)

Fortnite-specific game data including inventory, features, and settings.

```python
# Battle Royale inventory (V-Bucks)
inventory = client.fn.get_br_inventory("accountId")

# Storefront keychain
keychain = client.fn.get_keychain()

# Purchase receipts
receipts = client.fn.get_receipts("accountId")

# Enabled game features
features = client.fn.get_enabled_features()

# Version check
version = client.fn.get_version("Windows", version="++Fortnite+Release-30.40-CL-...-Windows")
```

#### Privacy & Entitlement (require user token)
```python
privacy = client.fn.get_privacy("accountId", fortnite_token="userToken")
client.fn.update_privacy(
    "accountId", {"optOutOfPublicLeaderboards": True}, fortnite_token="userToken"
)

check = client.fn.get_entitlement(fortnite_token="userToken")
client.fn.request_entitlement("accountId", fortnite_token="userToken")
```

---

### Sprites

Sprite catalog, drop data and player collections.

```python
# Current catalog (-> SpritesResponseDto)
catalog = client.sprites.get(rarity="legendary")
for family in catalog.sprites or []:
    print(family.name)

every_season = client.sprites.get_all()         # -> AllSpritesResponseDto
versions = client.sprites.get_versions()        # -> list[SpriteVersionDto]
boons = client.sprites.get_boons()              # -> list[SpriteBoonDto]
family = client.sprites.get_by_id("SpriteId")   # -> SpriteFamilyDto

# The caller's own collection
mine = client.sprites.get_collection(account_id="accountId")
all_mine = client.sprites.get_all_collections(account_id="accountId")

# Share your collection publicly (requires your own x-fortnite-token)
result = client.sprites.publish_collection(
    body={"visibility": "public"}, fortnite_token="userToken"
)
client.sprites.unpublish_collection(fortnite_token="userToken")

# View someone else's published collection (no token required)
shared = client.sprites.get_shared_collection("Ninja")
```

---

### Custom Match

Custom key pushes and bot account management.

```python
job = client.custom_match.initiate(
    body={"custom_key": "MYKEY", "players_id": ["accountId1", "accountId2"]}
)
status = client.custom_match.get_status("accountId1")
bots = client.custom_match.get_bots()

# Register / remove one of your own Epic accounts in your bot pool
client.custom_match.register_account(body={"label": "bot-1", "device_auth_json": "{...}"})
client.custom_match.delete_account(42)   # numeric account ID
```

---

### Identity

Link a Discord user to an Epic account.

```python
client.identity.link(
    body={"discord_id": "123456789", "epic_account_id": "accountId", "display_name": "Ninja"}
)
linked = client.identity.get("123456789")
```

---

### Friends

```python
friends = client.friends.get_friends("accountId")
summary = client.friends.get_summary("accountId")
friend = client.friends.get_friend("accountId", "friendId")
mutual = client.friends.get_mutual_friends("accountId", "friendId")
incoming = client.friends.get_incoming("accountId")
outgoing = client.friends.get_outgoing("accountId")
suggested = client.friends.get_suggested("accountId")
blocked = client.friends.get_blocklist("accountId")
```

---

### AES Keys & Mappings

```python
keys = client.aes.get_keys()           # current main key + dynamic pak keys
history = client.aes.get_history()     # historical keys
mappings = client.aes.get_mappings()   # .usmap download URLs
```

---

### Health

```python
client.health()           # GET /health
client.health_version()   # GET /health/version (deployed API version)
```

---

## 🔐 Authentication

Every method accepts an optional `fortnite_token` (sent as the `x-fortnite-token` header). Set it once on the client or pass it per call:

```python
client = FortniteAPI(api_key="...", fortnite_token="userToken")
client.fn.get_privacy("accountId", fortnite_token="override")  # per-call override
```

### Endpoints Requiring a User Token
- `client.quests.get()`
- `client.tournaments.get_tracker()`
- `client.tournaments.get_tracker_eligibility()`
- `client.tournaments.get_player()`
- `client.tournaments.get_player_session()`
- `client.tournaments.get_player_matches()` (for accounts other than the service account)
- `client.power_rankings.get_player()`
- `client.events.get_player_history()`
- `client.sprites.publish_collection()` / `client.sprites.unpublish_collection()`
- `client.fn.get_privacy()` / `client.fn.update_privacy()`
- `client.fn.get_entitlement()` / `client.fn.request_entitlement()`
- `client.profile.get_level()`

**How to obtain a user token:** use the OAuth flow:

```python
flow = client.oauth.get_token()
# Direct the user to the URL returned in `flow`
auth = client.oauth.complete(body={"flowId": flow["flowId"]})
# Use auth's access token as the `fortnite_token` argument
```

---

## 🚀 Advanced Usage

### Custom Base URL & Timeout

```python
client = FortniteAPI(
    api_key="your-api-key",
    base_url="https://custom-api-url.com/api",
    timeout=60.0,
)
```

### Typed Models

Most methods return Pydantic models defined in `fortnite_api.models`. Fields use snake_case
attribute names, while the original API (camelCase) names remain available through
`model_dump(by_alias=True)`. Fields that are not in the spec are kept rather than dropped.

```python
from fortnite_api.models import WeaponListItemDto

weapons: list[WeaponListItemDto] = client.weapons.get()
print(weapons[0].display_name, weapons[0].ammo_type)

raw = weapons[0].model_dump(by_alias=True)   # -> dict with the API's camelCase keys
```

Endpoints whose response has no schema in the OpenAPI spec still return raw JSON (`dict` / `list`).

### Deprecation Warnings

Methods for endpoints that the API marks as deprecated emit a `DeprecationWarning` and name the
replacement. To turn them into errors while testing:

```python
import warnings
warnings.simplefilter("error", DeprecationWarning)
```

### Error Handling

Every error derives from `FortniteAPIError` (`status`, `message`, `data`), so a single `except`
still catches everything. Catch a subclass to react to a specific failure:

| Condition | Exception | Notes |
|---|---|---|
| 3xx response | `RedirectError` | `location` holds the `Location` header |
| 401 | `AuthError` | subclass of `ClientError` |
| 403 | `PlanRequiredError` | subclass of `ClientError` |
| 404 | `NotFoundError` | subclass of `ClientError` |
| 429 | `RateLimitError` | subclass of `ClientError`; `retry_after` in seconds (from `Retry-After`) or `None`; **not capped**, clamp it before sleeping |
| other 4xx | `ClientError` | |
| 5xx | `ServerError` | |
| 2xx with `{"success": false}` | `UnsuccessfulResponseError` | `status` is the real HTTP status |
| 2xx with a non-JSON body | `DecodeError` | `data` is the body text (max. 1000 chars) |
| 2xx not matching the model | `ValidationError` | `validation_error` / `__cause__` is the `pydantic.ValidationError` |
| connection failure | `APIConnectionError` | `status == 0` (`fortnite_api.NETWORK_ERROR_STATUS`), the httpx error is the `__cause__` |
| timeout | `APITimeoutError` | subclass of `APIConnectionError`, `status == 0` |

```python
from fortnite_api import FortniteAPIError, NotFoundError, RateLimitError

try:
    shop = client.shop.get_current()
except RateLimitError as error:
    print("Retry in", min(error.retry_after or 10, 60), "seconds")  # retry_after is the raw server value
except NotFoundError:
    print("Not found")
except FortniteAPIError as error:
    print("API Error:", error.message)
    print("Status Code:", error.status)
    print("Details:", error.data)   # response body, never request headers
```

Exceptions and `repr()` of clients and transports never contain the API key or the user token.
Connection errors only name the exception type (httpx/h11 messages can echo header values), and the
credential headers of the request attached to `__cause__` (`__cause__.request.headers`) are masked
as `***`. An API key or token that is not printable ASCII or has leading/trailing whitespace (e.g.
a trailing newline read from a file) raises `ValueError` before anything is sent; the message
never includes the value.

### Retries

Retries are disabled by default. Pass a `RetryConfig` to retry idempotent requests (the `GET`
endpoints and the read-only bulk lookups `account.bulk_external_display_names`, `account.bulk_external_ids`,
`stats.get_bulk`, `profile.bulk_track_progress` and `profile.get_leaderboard`) after a 429 or 5xx
response, a connection error or a timeout:

```python
from fortnite_api import FortniteAPI, RetryConfig

client = FortniteAPI(
    api_key="your-api-key",
    retry=RetryConfig(max_retries=3, backoff_base=0.5, backoff_max=8.0, jitter=True, max_retry_after=60.0),
)
```

The wait honours `Retry-After` (capped at `max_retry_after`); otherwise it is an exponential backoff
(`backoff_base * 2**attempt`, capped at `backoff_max`) with optional jitter. When all retries fail,
the last error is raised. Other `POST`, `DELETE` and multipart (`parsing.*`) requests are never
retried, and neither are two kinds of `GET`: the `replays.parse*` endpoints (every attempt
consumes parsing credits) and `oauth.get_token` (every call starts a new device-code flow).

Custom transports can reuse the same decision with
`RetryConfig.next_delay(attempt, retryable=..., status=..., headers=...)`, which returns the seconds
to wait or `None` (`status=None` means a connection error or timeout).

### Redirects

Redirects are **not** followed: a 3xx response raises `RedirectError`, because the `x-api-key` and
`x-fortnite-token` headers would otherwise be re-sent to the redirect target. If you need to follow
them, pass `follow_redirects=True` (optionally with `max_redirects=`, default 5); credentials are
then only re-sent when scheme, host and port stay the same. `map.get_image()` always returns the
redirect target without following it.

```python
from fortnite_api import FortniteAPI, RedirectError

try:
    client.shop.get_current()
except RedirectError as error:
    print("Redirected to", error.location)

following = FortniteAPI(api_key="your-api-key", follow_redirects=True, max_redirects=3)
```

### User-Agent

Requests are sent with `User-Agent: fortnite-api-sdk/<version> python-httpx/<version>`. Override it
with `FortniteAPI(api_key=..., user_agent="my-app/1.0")`.

### Custom Transports

`FortniteAPI(transport=...)` and `AsyncFortniteAPI(transport=...)` accept any object implementing
`fortnite_api.SyncTransportProtocol` / `fortnite_api.AsyncTransportProtocol` (`request`,
`request_binary`, `request_redirect` and `request_multipart`). Settings such as the API key are
then configured on the transport, so `api_key=` and the other options must be omitted, and
`close()` leaves the injected transport open.

The functions in `fortnite_api.interpret` build URLs, headers and bodies and turn a status code,
headers and body into the same results and exceptions as the built-in transport, e.g.
`interpret.interpret_json(status, headers, body, response_type)`. See
[`examples/custom_transport.py`](examples/custom_transport.py) for a complete async transport with
an endpoint allowlist and a request counter. The core of a transport looks like this:

```python
from typing import Any

import httpx

from fortnite_api import APIConnectionError, APITimeoutError, AsyncFortniteAPI, interpret


class MyTransport:
    def __init__(self, api_key: str, http: httpx.AsyncClient) -> None:
        self._api_key = api_key
        self._http = http

    async def request(self, method, path, version, *, params=None, json_body=None,
                      fortnite_token=None, response_type=None, retryable=False) -> Any:
        try:
            resp = await self._http.request(
                method,
                interpret.build_url(interpret.DEFAULT_BASE_URL, path, version),
                params=interpret.clean_params(params),
                json=interpret.serialize_body(json_body),
                headers=interpret.build_headers(self._api_key, fortnite_token),
                follow_redirects=False,  # never re-send the key to a redirect target
            )
        except httpx.TimeoutException as exc:
            raise APITimeoutError(f"Request timed out ({type(exc).__name__})") from exc
        except httpx.TransportError as exc:
            raise APIConnectionError(f"Connection failed ({type(exc).__name__})") from exc
        return interpret.interpret_json(resp.status_code, resp.headers, resp.content, response_type)

    # request_binary, request_redirect and request_multipart follow the same pattern
    # (see examples/custom_transport.py).


client = AsyncFortniteAPI(transport=MyTransport("your-api-key", httpx.AsyncClient()))
```

The protocol methods and their exact parameters are:

| Method | Signature |
|---|---|
| `request` | `(method, path, version, *, params=None, json_body=None, fortnite_token=None, response_type=None, retryable=False)` |
| `request_binary` | `(path, version, *, fortnite_token=None) -> bytes` |
| `request_redirect` | `(path, version, *, params=None, fortnite_token=None) -> str \| None` |
| `request_multipart` | `(path, files, *, response_type=None, unwrap=True)` |

A complete transport must implement all four methods. `retryable=True` marks requests that are
safe to retry (GETs except `replays.parse*` and `oauth.get_token`, plus the read-only bulk
lookups), so a transport with its own retry logic can honour it, e.g. with
`RetryConfig.next_delay()`. `interpret.build_headers()` always sets `User-Agent`: the value of
`user_agent=` if given, otherwise `fortnite-api-sdk/<version>` (without the `python-httpx` suffix
the built-in transport adds). It also validates the API key and token (`ValueError` without
echoing them).

Rules for a safe transport:

- **Never follow redirects automatically.** httpx (`follow_redirects=True`) and **aiohttp** (whose
  default is `allow_redirects=True`) both re-send custom headers such as `x-api-key` and
  `x-fortnite-token` to a redirect target on another host, which reintroduces the key leak that
  0.3.0 fixes. With aiohttp pass `allow_redirects=False` on every request, and with httpx
  `follow_redirects=False`. Hand 3xx responses to `interpret.interpret_json()` /
  `interpret_binary()`, which raise `RedirectError`; `request_redirect` must return the `Location`
  via `interpret.interpret_redirect()` without following it. If you follow redirects on purpose,
  send only `interpret.redirect_headers(headers, from_url, to_url)` to each hop (credentials are
  kept for the same scheme, host and port only; see also `interpret.is_same_origin()`) and cap
  the number of hops.
- **Raise the SDK's network errors.** Map connection failures to `APIConnectionError` and
  timeouts to `APITimeoutError` with `raise ... from exc` (aiohttp: `aiohttp.ClientError` and
  `asyncio.TimeoutError`), so callers catching `FortniteAPIError` keep working. Do not copy the
  original error text into the message: HTTP libraries may echo header values in it.
- **Match sync and async.** `FortniteAPI` needs a plain `def request()` and `AsyncFortniteAPI` an
  `async def request()`; a mismatch raises `TypeError` when the client is created
  (`isinstance(..., AsyncTransportProtocol)` cannot tell them apart).

---

## ⬆️ Migrating from 0.2.x

Version 0.3.0 hardens the transport and adds pluggable transports. Please review the following
changes when upgrading.

### Breaking changes

- **Redirects are no longer followed.** A 3xx response now raises `RedirectError`. Pass
  `follow_redirects=True` to follow them (credentials are only re-sent to the same origin).
- **Specific exception classes.** Errors are now raised as subclasses of `FortniteAPIError`
  (see [Error Handling](#error-handling)). Code that catches `FortniteAPIError` keeps working;
  code that checks `type(error) is FortniteAPIError` must be updated.
- **Network errors are wrapped.** Connection errors and timeouts raise `APIConnectionError` /
  `APITimeoutError` (`status == 0`) instead of `httpx` exceptions. The original exception is
  available as `__cause__`.
- **`{"success": false}` responses keep their real status.** They raise
  `UnsuccessfulResponseError` with the actual HTTP status (usually 200) instead of a synthetic 422.
- **Invalid response bodies** raise `DecodeError` (not JSON) or `ValidationError` (does not match
  the model) instead of `json.JSONDecodeError` / `pydantic.ValidationError`. An empty 2xx body now
  returns `None`.
- **Path parameters are URL-encoded** as a single path segment (`/`, `?`, `#`, `%`, spaces...).
  Values that were previously passed pre-encoded (e.g. `"a%2Fb"`) are now encoded again. Empty path
  parameters raise `ValueError`.
- **Client constructor.** All arguments except `api_key` are keyword-only (as before) and now
  default to `None`; `api_key` may be omitted only when `transport=` is given.
- **Internal transport attributes.** The private helpers `_BaseTransport._parse`, `_unwrap`,
  `_body`, `_file_tuple`, `_clean` and `_error` were replaced by the public
  `fortnite_api.interpret` module, and `SyncTransport.api_key` / `fortnite_token` are no longer
  public attributes.
- **User-Agent.** Requests now identify as `fortnite-api-sdk/<version>`.
- **Credential validation.** An `api_key` or `fortnite_token` that is not printable ASCII or has
  leading/trailing whitespace (e.g. a trailing newline read from a file) now raises `ValueError`
  instead of failing inside httpx with a message that contained the value.

### New in 0.3.0

- `RetryConfig` for opt-in retries of idempotent requests
- `transport=` with `SyncTransportProtocol` / `AsyncTransportProtocol`, the `fortnite_api.interpret`
  module and `examples/custom_transport.py`
- `client.transport` property and `user_agent=`, `follow_redirects=`, `max_redirects=` options
- `RetryConfig.next_delay()` and `interpret.parse_retry_after(..., max_seconds=)` for custom
  retry logic
- `SyncTransport` / `AsyncTransport` are exported and can be used as context managers

---

## ⬆️ Migrating from 0.1.x

Version 0.2.0 syncs the SDK with the latest API specification. Please review the following changes when upgrading.

### Breaking changes

- **Typed responses.** Many methods that returned a plain `dict` / `list` now return Pydantic models
  (for example `tournaments.get_leaderboard()`, `tournaments.get_current()`, `events.get_window_leaderboard()`,
  `news.get_br()`, `battlepass.get()`). Replace key access with attribute access, or call
  `model_dump(by_alias=True)` to get the previous dictionary shape:

  ```python
  # 0.1.x
  lb = client.tournaments.get_leaderboard(event_id=..., event_window_id=...)
  entries = lb["entries"]

  # 0.2.0
  lb = client.tournaments.get_leaderboard(event_id=..., event_window_id=...)
  entries = lb.entries
  # or: lb.model_dump(by_alias=True)["entries"]
  ```

- **Power Rankings moved to `client.power_rankings`.**

  | 0.1.x | 0.2.0 |
  |---|---|
  | `client.tournaments.get_power_rankings()` | `client.power_rankings.get_leaderboard()` |
  | `client.tournaments.get_power_rankings_player()` | `client.power_rankings.get_player()` |
  | `client.tournaments.search_power_rankings()` | `client.power_rankings.search()` |

- **Battle Pass.** `battlepass.get()` now calls the v2 endpoint (`GET /api/v2/battlepass`), takes an
  optional `season` instead of `lang`, and returns a `BattlePassCatalog`. The previous behaviour is
  available as `battlepass.get_legacy(lang=...)`, which is deprecated.

- **Removed:** `tournaments.get_tracker_debug()` (the endpoint no longer exists in the API).

- **Parameter types follow the spec.** `cosmetics.get_all(season=, chapter=)` now take an `int`
  instead of a `str`, and `profile.bulk_track_progress(body)` now takes a `list[str]` instead of `Any`.

### Deprecations

The following methods still work but emit a `DeprecationWarning`:

- `battlepass.get_legacy()` → use `battlepass.get()`
- `replays.parse_broadcast()` → use `replays.parse()` or the individual `replays.parse_*` methods

### New in 0.2.0

- New resources: `sprites`, `custom_match`, `identity`, `power_rankings`
  (path parameters follow the spec types, e.g. `custom_match.delete_account(id)` takes an `int`)
- New methods: `tournaments.get_player_matches`, `get_player_session`, `get_player_window_matches`,
  `get_scoring`, `get_window_scoring`; `battlepass.get_seasons`; `quests.get_definitions`,
  `get_definition`; `weapons.get_by_id`, `get_lootpool`; `news.get_festival`, `get_notices`;
  `oauth.revoke_device`; `aes.get_history`; `replays.parse_tracks`; `power_rankings.get_from_archive`;
  `client.health_version()`
- New optional query parameters: `weapons.get(major=, minor=, date=, secondary=)`,
  `map.get(mode=)` / `map.get_image(mode=)`, `platform=` on the `news` feeds,
  `quests.get(resolve=)`, `events.get_window_leaderboard(round=, instance_id_format=)`,
  `events.get_player_window_standing(rank_hint=, max_pages=)`,
  `tournaments.get_leaderboard(cumulative_id=)`
- Request bodies accept the Pydantic request model or a plain `dict`

---

## 📖 Documentation

- **Full API Documentation (Swagger)**: https://documentation.api-fortnite.com/documentation
- **Support**: https://api-fortnite.com

This SDK is generated from `openapi/swagger.json` — regenerate after a spec change with:

```bash
uv run python scripts/generate.py
```

---

## 🛠️ Development

```bash
uv sync --locked --all-extras --dev   # set up the environment
uv run ruff check . && uv run ruff format --check . && uv run mypy
uv run pytest                         # offline unit tests with coverage
FN_API_KEY=... uv run pytest -m live  # smoke tests against the real API
```

See [docs/TESTING.md](docs/TESTING.md) for every check CI runs, the live tests, regenerating the SDK
from a new OpenAPI spec, and the release flow.

---

## 🤖 Agent Skill

This repository ships an [Agent Skill](skills/fortnite-api/SKILL.md) that teaches AI coding agents (such as Claude Code)
how to use this SDK correctly. See [skills/README.md](skills/README.md) for installation instructions.

---

## 📝 License

MIT
