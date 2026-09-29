# Replays and parsing: replays, parsing

Two ways to get parsed match data:

- `client.replays.*` - tournament replays fetched server-side **by match ID** (the `session_id`
  values from leaderboard `session_history` / `EventMatchDto`, or from
  `tournaments.get_player_matches()` / `get_player_session()`).
- `client.parsing.*` - you **upload a local `.replay` file** (multipart). These methods take
  `file: FileInput` = a filesystem path (`str`), `bytes` / `bytearray`, or an open binary file
  object, plus an optional `filename=`. The `parse_multiple*` variants take a list of those plus
  optional `filenames=`. `parsing.*` methods have no `fortnite_token` parameter.

Signatures, return types, HTTP paths and descriptions below are extracted from the SDK source
(`fortnite_api/resources/*.py`); only the guidance section is hand-written. All methods exist with
the same signature on `AsyncFortniteAPI` (add `await`). "Plans:" lines come from the `x-plans`
extension of the bundled OpenAPI spec (which api-fortnite.com plans may call the endpoint).

## Guidance

- **Everything returns raw JSON** (`Any`), except `replays.download()` which returns the `.replay`
  file as `bytes`. Explore the payload once and use the documented field names (field reference:
  https://api-fortnite.com/docs/replay-parser).
- **Cost.** Parsing is charged against a per-plan quota: 5 credits for most `replays.parse*`
  endpoints, 1 credit for `replays.parse_stats`. `parsing.*` uploads use the same quota, but
  their per-call cost is not documented. Pick the narrowest method (stats -> lobby -> full `parse`)
  and cache results locally rather than re-parsing the same match.
- **Which method:** stats only -> `parse_stats`; players / kills / placement -> `parse_lobby`;
  storm -> `parse_zones`; bus / drops / POI context -> `parse_map`; loot -> `parse_loot`;
  killfeed and events -> `parse_timeline`; player **positions** -> `replays.parse_tracks` (the only
  endpoint with movement data); everything at once -> `replays.parse` (or `parsing.parse_broadcast`
  for a local file).
- **Times and coordinates.** Subtract `referenceTime` from absolute times for match-relative
  seconds (not `matchStartTime`). Map units: `x = ueX/18.2 - 550`, `y = -ueY/18.2`.
- **Deprecated:** `replays.parse_broadcast()` emits `DeprecationWarning`; use `replays.parse()`.
- **Large files / timeouts.** Parsing big replays can take longer than the default 30 s timeout -
  create the client with `timeout=120.0` (or more) for parsing work.

## Contents

- [`client.replays`](#clientreplays)
- [`client.parsing`](#clientparsing)

## `client.replays`

### `client.replays.download(match_id: str, *, fortnite_token: str | None = None) -> bytes`

- HTTP: `GET /api/v1/replays/{matchId}`
- Returns raw bytes (binary download).
- Plans: `free`, `pro`, `custom`
- Download a tournament .replay file by match ID. Returns the raw .replay binary (application/octet- stream). Match IDs come from Epic's tournament events API.

```python
result = client.replays.download("<match_id>")
open("out.bin", "wb").write(result)
```

### `client.replays.get_metadata(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/metadata`
- Plans: `pro`, `custom`
- Get the raw chunk manifest (metadata) for a tournament replay. Returns Events, DataChunks, Checkpoints arrays with timing info.

```python
result = client.replays.get_metadata("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse`
- Plans: `pro`, `custom`
- Download and fully parse a tournament replay by match ID — the whole file. Returns everything the sub-endpoints return, combined: per-player stats and weapon tables (lobby), storm zones, map objects (bus/drops/llamas/reboot vans), ground loot, and the timeline with the full killfeed. The rows are identical to the sub-endpoints', but the envelope differs: everything is under "game", and the loot array is "game.loot" (it is "loot.pickups" on /parse/loot). Subtract "referenceTime" from any absolute time. worldBounds and the map projection of the storm (map.zones) are only on /parse/map. Field reference: https://api-fortnite.com/docs/replay-parser Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_broadcast(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/broadcast`
- Plans: `pro`, `custom`
- **Deprecated** (emits `DeprecationWarning`): This endpoint is marked as deprecated by the API. Use replays.parse() or the individual parse_* methods instead.
- DEPRECATED — use GET /{matchId}/parse instead, which returns the same combined payload for 5 credits. This route now serves the exact same result as /parse (same cache, 5 credits) and will be removed in v2.

```python
result = client.replays.parse_broadcast("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_lobby(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/lobby`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — full player lobby. Returns all players with kills, placement, damage, reboots, headshots, teamKills, death info, and cosmetics. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_lobby("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_loot(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/loot`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — ground loot. Server replays give whole-map loot coverage (vs ~150m radius for client replays). Returns all item spawns: position, item ID, picked-up status and time. Coordinates are map units derived from Unreal world cm: x = ueX/18.2 - 550, y = -ueY/18.2, z = ueZ/18.2 (invert to get Unreal coords). All times (spawnTime, pickedUpTime) are on the replay world clock, which starts during the warmup lobby — subtract referenceTime for match-relative times. Do NOT subtract matchStartTime: it is a skydive-gap heuristic that can land minutes into the match and push most pickups negative; it is kept only for existing consumers. Warmup-island loot appears far outside the main map bounds. spawnTime for pre-placed floor loot is when the actor first replicated, not when a player could see it. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_loot("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_map(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/map`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — map context. Returns bus path, storm circles, supply drops, llamas, reboot vans. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_map("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_stats(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/stats`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — stats only. Faster than full parse. Returns name, replayId, version, playlist, teamSize, teamCount, isTournament, tournamentRound, stats. Subject to per-plan parsing quota limits (1 credit).

```python
result = client.replays.parse_stats("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_timeline(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/timeline`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — match timeline. Returns chronological event feed: kills, knocks, death, damage dealt/taken, heals, pickups. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_timeline("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_tracks(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/tracks`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — per-player tracks for interactive map playback. For every player: downsampled movement samples [t, x, y, z, stateFlags], health/shield curve, held-weapon changes, item pickups, material deltas, damage dealt and life events (knock/death/revive/reboot) — plus storm circle phases and the kill feed. This is the ONLY endpoint that returns player positions: /parse and the deprecated /parse/broadcast never carried them. Sample times are already relative to referenceTime; x/y are map units (same convention as /parse/loot), z = ueZ/18.2. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_tracks("<match_id>")
# raw JSON (dict / list) - use key access
```

### `client.replays.parse_zones(match_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/replays/{matchId}/parse/zones`
- Plans: `pro`, `custom`
- Download and parse a tournament replay — storm zones. Returns all safe zone phases with timing, positions, and damage per tick. Subject to per-plan parsing quota limits (5 credits).

```python
result = client.replays.parse_zones("<match_id>")
# raw JSON (dict / list) - use key access
```

## `client.parsing`

### `client.parsing.parse_replay(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and extract match statistics. Subject to per-plan parsing quota limits.

```python
result = client.parsing.parse_replay("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_stats(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/stats`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `free`, `pro`, `custom`
- Parse a single Fortnite .replay file and return only basic match statistics. Significantly faster than full parsing — skips movement, zones, and kill feed. Returns: name, replayId, version, stats (elims, damage, accuracy, placement, assists, damageTaken, damageStructures, matsFarm, matsUsed, totalPlayers).

```python
result = client.parsing.parse_stats("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_map(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/map`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return full map context. Returns: bus flight path + drop window, all storm circles with timing, supply drops, llamas, reboot vans.

```python
result = client.parsing.parse_map("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_loot(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/loot`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return ground loot data. Returns all items that were on the ground near the player: position, item ID, picked-up status and time. Times are on the replay world clock — subtract referenceTime, NOT matchStartTime (a heuristic kept only for existing consumers). Field reference: https://api-fortnite.com/docs/replay-parser

```python
result = client.parsing.parse_loot("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_timeline(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/timeline`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return a time-ordered match timeline. Returns all events with t in seconds since referenceTime (match start): kills, knocks, own death, damage dealt, damage taken, healed, pickups. Requires full parse mode — slower than /parsing/stats but richer than /parsing.

```python
result = client.parsing.parse_timeline("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_zones(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/zones`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return storm zone data. Returns all safe zone phases with circle positions, timing, damage per tick, and phase count.

```python
result = client.parsing.parse_zones("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_lobby(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/lobby`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return the full player lobby. Returns all players with placement, kills, death info, cosmetics, and team data.

```python
result = client.parsing.parse_lobby("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_broadcast(file: FileInput, *, filename: str | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/broadcast`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: `pro`, `custom`
- Parse a single Fortnite .replay file and return the complete broadcast payload. Combines all data: header, stats, full player lobby, storm zones, map objects, ground loot, and timeline events. Requires full parse mode — equivalent to calling all endpoints in one request.

```python
result = client.parsing.parse_broadcast("match.replay")
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_multiple(files: list[FileInput], *, filenames: list[str] | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/multiple`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: not stated (this operation is not in the bundled OpenAPI spec)

```python
result = client.parsing.parse_multiple(["a.replay", "b.replay"])
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_multiple_stats(files: list[FileInput], *, filenames: list[str] | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/multiple/stats`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: not stated (this operation is not in the bundled OpenAPI spec)

```python
result = client.parsing.parse_multiple_stats(["a.replay", "b.replay"])
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_multiple_map(files: list[FileInput], *, filenames: list[str] | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/multiple/map`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: not stated (this operation is not in the bundled OpenAPI spec)

```python
result = client.parsing.parse_multiple_map(["a.replay", "b.replay"])
# raw JSON (dict / list) - use key access
```

### `client.parsing.parse_multiple_loot(files: list[FileInput], *, filenames: list[str] | None = None) -> Any`

- HTTP: `POST /api/v1/parsing/multiple/loot`
- Uploads the file as multipart form data (path, bytes, or binary file object).
- No `fortnite_token` parameter.
- Plans: not stated (this operation is not in the bundled OpenAPI spec)

```python
result = client.parsing.parse_multiple_loot(["a.replay", "b.replay"])
# raw JSON (dict / list) - use key access
```

