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
- ✅ Pydantic models for well-defined responses (shop, cosmetics, weapons, map, season); raw `dict` for the rest
- ✅ Automatic error handling with a single `FortniteAPIError` (status + message + body)
- ✅ Support for all Fortnite API endpoints (22 resources, 113 methods)
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

# Get current Battle Pass
battle_pass = client.battlepass.get()
```

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
leaderboard = client.tournaments.get_leaderboard(
    event_id="epicgames_S37_BlitzCupsAllPlatforms_BR",
    event_window_id="S37_BlitzCupsAllPlatforms_Event1_BR",
    page=0,
)
```

#### Power Rankings
```python
top = client.tournaments.get_power_rankings(page=0)
player = client.tournaments.get_power_rankings_player("Ninja")
results = client.tournaments.search_power_rankings(q="nin", limit=10)
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
prizes = client.tournaments.get_cashprizes()
window = client.tournaments.get_cashprize("S37_BlitzCupsAllPlatforms_Event1_BR")
```

---

### Quests

Access player quest progress, XP, and account level information.

```python
# Requires the user's personal Fortnite OAuth token
quests = client.quests.get("accountId", fortnite_token="userToken")
```

**Authentication Required**: user's Fortnite OAuth token.

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
```

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
broadcast = client.replays.parse_broadcast(match_id)
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
br_news = client.news.get_br()
stw_news = client.news.get_stw()
creative_news = client.news.get_creative()
all_news = client.news.get_all()
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

### Error Handling

```python
from fortnite_api import FortniteAPIError

try:
    shop = client.shop.get_current()
except FortniteAPIError as error:
    print("API Error:", error.message)
    print("Status Code:", error.status)
    print("Details:", error.data)   # raw error body
```

---

## 📖 Documentation

- **Full API Documentation (Swagger)**: https://documentation.api-fortnite.com/documentation
- **Support**: https://api-fortnite.com

This SDK is generated from `openapi/swagger.json` — regenerate after a spec change with:

```bash
uv run python scripts/generate.py
```

---

## 📝 License

MIT
