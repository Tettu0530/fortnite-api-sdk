# Competitive resources: tournaments, events, power_rankings, stats, profile

Tournaments, event-window leaderboards, scoring and payouts, Power Rankings, player stats and
ranked progress.

Signatures, return types, HTTP paths and descriptions below are extracted from the SDK source
(`fortnite_api/resources/*.py`); only the guidance section is hand-written. All methods exist with
the same signature on `AsyncFortniteAPI` (add `await`). "Token:" lines appear only where the API
description states something about `x-fortnite-token`. "Plans:" lines come from the `x-plans`
extension of the bundled OpenAPI spec (which api-fortnite.com plans may call the endpoint).

## Guidance

- **Finding event IDs.** `tournaments.get_current()` (active + upcoming) and
  `tournaments.get_global_history()` return `list[GlobalEventDto]`. Each has
  `regions: dict[str, list[EpicEventDto]]`; an `EpicEventDto` has `event_id`, `begin_time`,
  `end_time`, `platforms`, and `event_windows: list[EpicEventWindowDto]` with `event_window_id`,
  `begin_time`, `end_time`, `round`. Those two IDs feed every leaderboard call.
- **Two leaderboard methods.** `tournaments.get_leaderboard(*, event_id=, event_window_id=, page=)`
  (keyword-only, `/api/v1/events/global/leaderboard`) and
  `events.get_window_leaderboard(event_id, event_window_id, *, page=, round=)` (positional,
  `/api/v2/events/{eventId}/windows/{eventWindowId}/leaderboard`). Both return `EventLeaderboardDto` with
  `page`, `total_pages`, `entries: list[EventLeaderboardEntryDto]` (`rank`, `points_earned`,
  `score`, `team_account_ids`, `session_history`). Entries hold account IDs, not names - resolve
  names with `client.account.get_display_names(ids)`.
- **One player in a window, no token:** `events.get_window_leaderboard_player()` (rank and the
  entries around it) or `events.get_player_window_standing()` /
  `tournaments.get_player_window_matches()` (scans pages; pass `rank_hint=` to be fast).
- **Eligibility:** `tournaments.get_tracker_eligibility()` may return `eligible: null` while the
  history backfill is incomplete - treat `null` as "unknown", not "not eligible".
- **Power Rankings:** 100 entries per page, 100 pages (top 10,000). `search()` and
  `get_from_archive()` need no token; `get_player()` needs the looked-up player's token.
- **Stats / profile** return raw JSON. `stats.get(account_id)` takes an Epic **account ID** -
  resolve display names first with `account.get_by_display_name()`. `profile.get_ranked()` accepts
  either `display_name=` or `account_id=`.

## Contents

- [`client.tournaments`](#clienttournaments)
- [`client.events`](#clientevents)
- [`client.power_rankings`](#clientpower_rankings)
- [`client.stats`](#clientstats)
- [`client.profile`](#clientprofile)

## `client.tournaments`

### `client.tournaments.get_cashprize(event_window_id: str, *, fortnite_token: str | None = None) -> list[CashPrizeScoringDto]`

- HTTP: `GET /api/v1/events/cashprize/{eventWindowId}`
- Plans: `pro`, `custom`
- Get the payout table for a specific event window.
- `CashPrizeScoringDto` fields: `scoring_type` (scoringType): `str | None`, `ranks`: `list[CashPrizeRankDto] | None`

```python
result = client.tournaments.get_cashprize("<event_window_id>")
first = result[0].scoring_type if result else None
```

### `client.tournaments.get_cashprizes(*, fortnite_token: str | None = None) -> dict[str, list[CashPrizeScoringDto]]`

- HTTP: `GET /api/v1/events/cashprizes`
- Plans: `pro`, `custom`
- Get all payout tables extracted from Epic's events download. Player data is stripped — only reward/prize structures are returned. Response is cached for 4 hours.
- `CashPrizeScoringDto` fields: `scoring_type` (scoringType): `str | None`, `ranks`: `list[CashPrizeRankDto] | None`

```python
result = client.tournaments.get_cashprizes()
for key, value in result.items(): ...
```

### `client.tournaments.get_current(*, lang: str | None = None, fortnite_token: str | None = None) -> list[GlobalEventDto]`

- HTTP: `GET /api/v1/events/global`
- Plans: `pro`, `custom`
- Get currently active and upcoming tournaments, enriched with CMS metadata.
- `GlobalEventDto` fields: `id`: `str | None`, `display_data_id` (displayDataId): `str | None`, `name`: `str | None`, `short_title` (shortTitle): `str | None`, `title_line1` (titleLine1): `str | None`, `title_line2` (titleLine2): `str | None`, `description`: `str | None`, `details_description` (detailsDescription): `str | None`, `schedule_info` (scheduleInfo): `str | None`, `poster`: `str | None`, `loading_screen` (loadingScreen): `str | None`, `regions`: `dict[str, list[EpicEventDto]] | None`

```python
result = client.tournaments.get_current()
first = result[0].id if result else None
```

### `client.tournaments.get_global_history(*, lang: str | None = None, fortnite_token: str | None = None) -> list[GlobalEventDto]`

- HTTP: `GET /api/v1/events/global/history`
- Plans: `pro`, `custom`
- Get all tournaments including past ones, enriched with CMS metadata.
- `GlobalEventDto` fields: `id`: `str | None`, `display_data_id` (displayDataId): `str | None`, `name`: `str | None`, `short_title` (shortTitle): `str | None`, `title_line1` (titleLine1): `str | None`, `title_line2` (titleLine2): `str | None`, `description`: `str | None`, `details_description` (detailsDescription): `str | None`, `schedule_info` (scheduleInfo): `str | None`, `poster`: `str | None`, `loading_screen` (loadingScreen): `str | None`, `regions`: `dict[str, list[EpicEventDto]] | None`

```python
result = client.tournaments.get_global_history()
first = result[0].id if result else None
```

### `client.tournaments.get_leaderboard(*, event_id: str | None = None, event_window_id: str | None = None, page: int | None = None, leaderboard_def: str | None = None, account_id: str | None = None, cumulative_id: str | None = None, fortnite_token: str | None = None) -> EventLeaderboardDto`

- HTTP: `GET /api/v1/events/global/leaderboard`
- Plans: `pro`, `custom`
- Token: optional - include the player's `x-fortnite-token` for a personalized leaderboard view
- Get a paginated tournament leaderboard for the given event window.
- `EventLeaderboardDto` fields: `game_id` (gameId): `str | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `page`: `int | None`, `total_pages` (totalPages): `int | None`, `updated_time` (updatedTime): `str | None`, `entries`: `list[EventLeaderboardEntryDto] | None`

```python
result = client.tournaments.get_leaderboard()
print(result.game_id)
```

### `client.tournaments.get_player(*, region: str | None = None, platform: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/player`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get the authenticated player's tournament data — token progression and event participation. Requires x-fortnite-token and accountId.

```python
result = client.tournaments.get_player()
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_player_matches(account_id: str, *, after: str | None = None, before: str | None = None, region: str | None = None, platform: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/player/{accountId}/matches`
- Plans: `pro`, `custom`
- Token: **required** for any account other than the API's service account (403 otherwise)
- Get a player's RECENT tournament sessions (session IDs), grouped by event window. Sourced from Epic's player-scoped /download data, which Epic keeps for roughly the last 36 hours only (measured 2026-09-01) — this is not a full history. Tournament sessions only: private custom-key matches are not events and never appear here. Epic only serves this data to the player it belongs to, so x-fortnite-token is required for any account other than the service account (403 otherwise). For a 180-day participation history use GET /events/tracker; for a token-less lookup of one tournament use GET {eventId}/{eventWindowId}/player/{accountId}/matches; for the match a player is in right now use GET player/{accountId}/session.

```python
result = client.tournaments.get_player_matches("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_player_session(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/player/{accountId}/session`
- Plans: `custom`
- Token: **required** — the player's own `x-fortnite-token`
- Get the match a consenting player is in right now — any mode: Battle Royale, Reload, Ranked, or a custom-key scrim hosted by anyone. Requires the player's OWN x-fortnite-token: the token is verified against the accountId before anything is forwarded (403 otherwise). That token comes from Epic's device-authorization flow, which authenticates as the Fortnite client rather than as your application; Epic Account Services developer terms do not allow routing your users through it, so it suits tools a player runs for themselves, not third-party apps asking other players to log in. Because Fortnite kills every other session of an account when the game launches, store the deviceAuth that POST /oauth/complete returns and re-authenticate with POST /oauth/refresh-device on 401. When Epic publishes it, sessionId is the replay match ID — pass it to /replays/{matchId} once the match has ended; playlist lets you filter (e.g. scrims) before parsing, and playlistSource says whether that playlist is the match being played (currentIsland) or only the lobby selection (islandSelection). sessionId can be null while inMatch is true: the id lives in the party fields the client uses to advertise "my friends may join or watch me", and a match that cannot be joined or watched can publish them empty for its whole duration. sessionSource names the field the id came from, and diagnostics reports, per field, whether Epic sent it present, empty or absent — presence only, never a value. When every field is empty, note says so and polling harder does not change it. The custom match key is never returned (hasCustomKey only); teammates are listed by account id only. inParty is false when the player's client is offline. Cached 10 s per account — polling faster gains nothing — and Epic's own party state lags the real match by 1-2 min. Rate limit: 1200 requests/min per API key.

```python
result = client.tournaments.get_player_session("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_player_window_matches(event_id: str, event_window_id: str, account_id: str, *, rank_hint: int | None = None, max_pages: int | None = None, fortnite_token: str | None = None) -> PlayerWindowStandingDto`

- HTTP: `GET /api/v1/events/{eventId}/{eventWindowId}/player/{accountId}/matches`
- Plans: `pro`, `custom`
- Token: not required (per API description)
- Get a player's matches (session IDs + per-match stats) in one event window, without any player token: the leaderboard is scanned page by page until the player's team is found. Pass rankHint (their approximate final rank) to hit the right page first — without it up to maxPages pages are scanned in order.
- `PlayerWindowStandingDto` fields: `found`: `bool | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `account_id` (accountId): `str | None`, `rank`: `int | None`, `points_earned` (pointsEarned): `int | None`, `team_account_ids` (teamAccountIds): `list[str] | None`, `match_count` (matchCount): `int | None`, `matches`: `list[EventMatchDto] | None`

```python
result = client.tournaments.get_player_window_matches("<event_id>", "<event_window_id>", "<account_id>")
print(result.found)
```

### `client.tournaments.get_scoring(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/scoring`
- Plans: `pro`, `custom`
- Get the per-match scoring rules (placement/elimination reward tiers) for every event window, keyed by eventWindowId. Extracted from Epic's events data (scoringRuleSets + scoreLocationScoringRuleSets, with event-template fallback).

```python
result = client.tournaments.get_scoring()
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_window_scoring(event_window_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/scoring/{eventWindowId}`
- Plans: `pro`, `custom`
- Get the per-match scoring rules for a specific event window — the authoritative "how does this session score" (exists before the first game is played, and differs between a weekly cup's qualifier round and its final).

```python
result = client.tournaments.get_window_scoring("<event_window_id>")
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_sessions(*, event_id: str | None = None, fortnite_token: str | None = None) -> EventSessionDto`

- HTTP: `GET /api/v1/events/sessions`
- Plans: `pro`, `custom`
- Get sessions for a specific event.
- `EventSessionDto` fields: `group_id` (groupId): `str | None`, `name`: `str | None`, `short_title` (shortTitle): `str | None`, `title_line1` (titleLine1): `str | None`, `title_line2` (titleLine2): `str | None`, `description`: `str | None`, `details_description` (detailsDescription): `str | None`, `schedule_info` (scheduleInfo): `str | None`, `poster`: `str | None`, `loading_screen` (loadingScreen): `str | None`, `matched_event_id` (matchedEventId): `str | None`, `matched_region` (matchedRegion): `str | None`, `all_regions` (allRegions): `list[str] | None`, `matched_event` (matchedEvent): `EpicEventDto | None`

```python
result = client.tournaments.get_sessions()
print(result.group_id)
```

### `client.tournaments.get_stat_leaders(event_id: str, event_window_id: str, stat_key: str, *, top: int | None = None, fortnite_token: str | None = None) -> EventStatsLeaderboardDto`

- HTTP: `GET /api/v1/events/stats/{eventId}/{eventWindowId}/{statKey}`
- Plans: `pro`, `custom`
- Get the top performers for a specific tracked stat across the entire leaderboard. Fetches all pages in parallel batches so low-scoring but high-stat teams (e.g. top fraggers in a placement-only event) are always included regardless of their leaderboard position. Response includes an `availableStats` array listing every stat key tracked in this tournament.
- `EventStatsLeaderboardDto` fields: `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `stat_key` (statKey): `str | None`, `top`: `int | None`, `total_teams` (totalTeams): `int | None`, `total_pages` (totalPages): `int | None`, `updated_time` (updatedTime): `str | None`, `available_stats` (availableStats): `list[str] | None`, `rankings`: `list[EventStatRankingDto] | None`

```python
result = client.tournaments.get_stat_leaders("<event_id>", "<event_window_id>", "<stat_key>")
print(result.event_id)
```

### `client.tournaments.get_team_stats(event_id: str, event_window_id: str, stat_key: str, team_identifier: str, *, twitter: bool | None = None, fortnite_token: str | None = None) -> TeamEventStatsDto`

- HTTP: `GET /api/v1/events/stats/{eventId}/{eventWindowId}/{statKey}/{teamIdentifier}`
- Plans: `pro`, `custom`
- Get all tracked stats for a specific team identified by Epic account ID or display name. Returns every stat tracked in this tournament for that team (total + per-game), plus their rank in the requested statKey across all teams in the event. Accepts account ID (32 hex chars) or display name — clan tags are stripped for matching.
- `TeamEventStatsDto` fields: `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `team_identifier` (teamIdentifier): `str | None`, `stat_key` (statKey): `str | None`, `stat_rank` (statRank): `int | None`, `total_teams` (totalTeams): `int | None`, `updated_time` (updatedTime): `str | None`, `team`: `TeamEventStatsDetailDto | None`

```python
result = client.tournaments.get_team_stats("<event_id>", "<event_window_id>", "<stat_key>", "<team_identifier>")
print(result.event_id)
```

### `client.tournaments.get_tokens(team_account_ids: list[str], *, fortnite_token: str | None = None) -> PlayerTokensDto`

- HTTP: `GET /api/v1/events/tokens`
- Plans: `pro`, `custom`
- Get the raw token set for one or more players directly from Epic's tokens endpoint. Tokens represent eligibility flags earned by participating in tournaments. Pass multiple IDs as comma-separated values: ?teamAccountIds=id1%2Cid2%2C...
- `PlayerTokensDto` fields: `accounts`: `list[PlayerTokenAccountDto] | None`

```python
result = client.tournaments.get_tokens(["accountId1", "accountId2"])
print(result.accounts)
```

### `client.tournaments.get_tracker(*, account_id: str | None = None, valid_only: bool | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/tracker`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get tournament tracker data for a player — token progression and past event participation. Requires x-fortnite-token and accountId.

```python
result = client.tournaments.get_tracker()
# raw JSON (dict / list) - use key access
```

### `client.tournaments.get_tracker_eligibility(*, account_id: str | None = None, days: int | None = None, required_tournaments: int | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/tracker/eligibility`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Check whether a player is eligible for tournaments based on their participation history. Eligibility is determined by the number of tournaments played in the last N days. Requires x-fortnite-token and accountId. Epic's live payload only remembers about a day of participation, so history older than that is rebuilt from per-window leaderboards in the background. The response carries a `history` block saying how much of the look-back has actually been verified. Until `history.complete` is true, `tournaments_played` is a LOWER BOUND and `eligible` is `null` rather than `false` — reaching the threshold still proves eligibility, but falling short proves nothing yet. The first call for a player kicks off that backfill; it takes a few minutes.

```python
result = client.tournaments.get_tracker_eligibility()
# raw JSON (dict / list) - use key access
```

### `client.tournaments.check_eligibility(identifier: str, event_id: str, *, event_window_id: str | None = None, fortnite_token: str | None = None) -> EventTokenEligibilityDto`

- HTTP: `GET /api/v1/events/tracker/eligibility/{identifier}/{eventId}`
- Plans: `pro`, `custom`
- Token: optional — with the player's OWN token the PR rank and Account Level are read live; without it the verdict may be `"unconfirmed"`
- Check a player's eligibility for a specific event window — the token rules (requireAllTokens, requireAnyTokens, requireNoneTokensCaller, …) for any player, the window's additionalRequirements (e.g. FNCS Solos: Power Rankings top 200,000) and the minimum Account Level. With the PLAYER'S OWN x-fortnite-token the Power Rankings rank is read live at any depth and the Account Level exactly; without it the rank comes from the PR archive and the level is a lower bound, so `verdict` may be "unconfirmed". Accepts display name or account ID (with or without dashes).
- `EventTokenEligibilityDto` fields: `account_id` (accountId): `str | None`, `display_name` (displayName): `str | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `is_eligible` (isEligible): `bool | None`, `verdict`: `str | None`, `verified_requirements` (verifiedRequirements): `list[VerifiedRequirementDto] | None`, `additional_requirements` (additionalRequirements): `list[Any] | None`, `unverified_requirements` (unverifiedRequirements): `list[UnverifiedRequirementDto] | None`

```python
result = client.tournaments.check_eligibility("<identifier>", "<event_id>")
print(result.account_id)
```

## `client.events`

### `client.events.get_player_history(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/events/players/{accountId}/history`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get a player's event participation history. Requires x-fortnite-token — Epic's history endpoint does not accept service auth. Obtain a token via GET /api/v1/oauth/get-token → POST /api/v1/oauth/complete.

```python
result = client.events.get_player_history("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.events.get_window_leaderboard(event_id: str, event_window_id: str, *, page: int | None = None, leaderboard_def: str | None = None, round: int | None = None, instance_id_format: str | None = None, fortnite_token: str | None = None) -> EventLeaderboardDto`

- HTTP: `GET /api/v2/events/{eventId}/windows/{eventWindowId}/leaderboard`
- Plans: `pro`, `custom`
- Get the paginated leaderboard for a specific event window. Use leaderboardDef to resolve a cumulative or rank-tier leaderboard definition.
- `EventLeaderboardDto` fields: `game_id` (gameId): `str | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `page`: `int | None`, `total_pages` (totalPages): `int | None`, `updated_time` (updatedTime): `str | None`, `entries`: `list[EventLeaderboardEntryDto] | None`

```python
result = client.events.get_window_leaderboard("<event_id>", "<event_window_id>")
print(result.game_id)
```

### `client.events.get_window_leaderboard_player(event_id: str, event_window_id: str, *, account_id: str | None = None, fortnite_token: str | None = None) -> list[EventLeaderboardEntryDto]`

- HTTP: `GET /api/v2/events/{eventId}/windows/{eventWindowId}/leaderboard/player`
- Plans: `pro`, `custom`
- Token: not required (per API description)
- Find a player's rank and surrounding entries in an event window leaderboard. Works for any placement including beyond top 10k. No x-fortnite-token required.
- `EventLeaderboardEntryDto` fields: `game_id` (gameId): `str | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `team_id` (teamId): `str | None`, `team_account_ids` (teamAccountIds): `list[str] | None`, `rank`: `int | None`, `points_earned` (pointsEarned): `int | None`, `score`: `int | None`, `percentile`: `float | None`, `point_breakdown` (pointBreakdown): `dict[str, Any] | None`, `session_history` (sessionHistory): `list[EventMatchDto] | None`

```python
result = client.events.get_window_leaderboard_player("<event_id>", "<event_window_id>")
first = result[0].game_id if result else None
```

### `client.events.get_player_window_standing(event_id: str, event_window_id: str, account_id: str, *, rank_hint: int | None = None, max_pages: int | None = None, fortnite_token: str | None = None) -> PlayerWindowStandingDto`

- HTTP: `GET /api/v2/events/{eventId}/windows/{eventWindowId}/players/{accountId}`
- Plans: `pro`, `custom`
- Token: not required (per API description)
- Get a player's standing (rank, points, team and per-match tracked stats) in an event window. Service token only, no x-fortnite-token needed.
- `PlayerWindowStandingDto` fields: `found`: `bool | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `account_id` (accountId): `str | None`, `rank`: `int | None`, `points_earned` (pointsEarned): `int | None`, `team_account_ids` (teamAccountIds): `list[str] | None`, `match_count` (matchCount): `int | None`, `matches`: `list[EventMatchDto] | None`

```python
result = client.events.get_player_window_standing("<event_id>", "<event_window_id>", "<account_id>")
print(result.found)
```

## `client.power_rankings`

### `client.power_rankings.get_leaderboard(*, page: int | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> PowerRankingsPageDto`

- HTTP: `GET /api/v1/events/powerrankings`
- Plans: `pro`, `custom`
- Token: optional — pass `fortnite_token` + `account_id` to also get the caller's own `playerEntry`
- Get the Fortnite Power Rankings leaderboard — the official competitive skill rating. Returns 100 players per page (100 pages total = top 10,000 players). The service account used to query Epic is stripped from the response. Supply x-fortnite-token + accountId to also receive the caller's own PR entry as `playerEntry` in the response (null if they are unranked). Without a token the response is the plain global page — that part needs no auth. trackedStats keys: PR (score), countingEvents (max 20), peakPerf, deltaPR, peakPR. For a single player use `powerrankings/search` or `powerrankings/archive/{accountId}` (no token), or `powerrankings/player/{identifier}` (x-fortnite- token required).
- `PowerRankingsPageDto` fields: `game_id` (gameId): `str | None`, `event_id` (eventId): `str | None`, `event_window_id` (eventWindowId): `str | None`, `page`: `int | None`, `total_pages` (totalPages): `int | None`, `updated_time` (updatedTime): `str | None`, `entries`: `list[PowerRankingEntryDto] | None`

```python
result = client.power_rankings.get_leaderboard()
print(result.game_id)
```

### `client.power_rankings.get_player(identifier: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/events/powerrankings/player/{identifier}`
- Plans: `pro`, `custom`
- Token: **required** — the token of the player being looked up
- Look up a player's Power Rankings entry by display name or account ID. **Requires the x-fortnite- token of the player being looked up.**

```python
result = client.power_rankings.get_player("<identifier>")
# raw JSON (dict / list) - use key access
```

### `client.power_rankings.search(*, q: str | None = None, limit: int | None = None, fortnite_token: str | None = None) -> PowerRankingSearchDto`

- HTTP: `GET /api/v1/events/powerrankings/search`
- Plans: `pro`, `custom`
- Token: not required (per API description)
- Search Power Rankings players by display name (partial, case-insensitive). Results come from an in- memory index built from the full 10,000-player leaderboard. The index is rebuilt every 2 hours and cached in Redis — no user token required.
- `PowerRankingSearchDto` fields: `query`: `str | None`, `total`: `int | None`, `results`: `list[PowerRankingSearchResultDto] | None`

```python
result = client.power_rankings.search()
print(result.query)
```

### `client.power_rankings.get_from_archive(account_id: str, *, fortnite_token: str | None = None) -> PowerRankingArchiveDto`

- HTTP: `GET /api/v1/events/powerrankings/archive/{accountId}`
- Plans: `pro`, `custom`
- Token: not required
- Look up a player's most recent Power Rankings entry by account ID from the archive. Returns rank, score, bestRank, peakPr, deltaPr, countingEvents and the last-updated time. Unlike `powerrankings/player/{identifier}`, this does NOT require an x-fortnite-token and works for any account that has appeared in the top-10,000 leaderboard.
- `PowerRankingArchiveDto` fields: `account_id` (accountId): `str | None`, `display_name` (displayName): `str | None`, `rank`: `int | None`, `score`: `int | None`, `best_rank` (bestRank): `int | None`, `peak_pr` (peakPr): `int | None`, `delta_pr` (deltaPr): `int | None`, `counting_events` (countingEvents): `int | None`, `last_updated` (lastUpdated): `str | None`, `season_label` (seasonLabel): `str | None`

```python
result = client.power_rankings.get_from_archive("<account_id>")
print(result.account_id)
```

## `client.stats`

### `client.stats.get_bulk(body: Any, *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v2/stats/bulk`
- Plans: `pro`, `custom`
- Get stats for multiple players in one request.

```python
result = client.stats.get_bulk(["accountId1", "accountId2"])
# raw JSON (dict / list) - use key access
```

### `client.stats.get_leaderboard(stat: str, *, limit: int | None = None, offset: int | None = None, window: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/stats/leaderboard/{stat}`
- Plans: `pro`, `custom`
- Get the global leaderboard for a specific stat.

```python
result = client.stats.get_leaderboard("<stat>")
# raw JSON (dict / list) - use key access
```

### `client.stats.get(account_id: str, *, start_time: str | None = None, end_time: str | None = None, stats: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/stats/{accountId}`
- Plans: `free`, `pro`, `custom`
- Get stats for a single player by Epic account ID.

```python
result = client.stats.get("<account_id>")
# raw JSON (dict / list) - use key access
```

## `client.profile`

### `client.profile.get_leaderboard(game_id: str, *, account_id: str | None = None, from_index: int | None = None, find_teams: bool | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/profile/leaderboard/{gameId}`
- Plans: `pro`, `custom`
- Get a Habanero game leaderboard centered around an account (e.g. HazelnutSpread). The gameId maps to the internal Habanero game identifier.

```python
result = client.profile.get_leaderboard("<game_id>")
# raw JSON (dict / list) - use key access
```

### `client.profile.get_level(*, account_id: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/profile/level`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get a player's XP, level, accountLevel, and battle pass tier. Parsed from QueryProfile (profileId=athena) — requires x-fortnite-token.

```python
result = client.profile.get_level()
# raw JSON (dict / list) - use key access
```

### `client.profile.get_progress(*, account_id: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/profile/progress`
- Plans: `pro`, `custom`
- Token: not required
- Get raw Habanero track progress for a single account. Public — no token required.

```python
result = client.profile.get_progress()
# raw JSON (dict / list) - use key access
```

### `client.profile.get_ranked(*, display_name: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/profile/ranked`
- Plans: `pro`, `custom`
- Get a player's enriched ranked progress — human-readable rank names, game mode labels, season dates, and isCurrent flag. Accepts either ?displayName= or ?accountId= (accountId skips the name lookup and is preferred).

```python
result = client.profile.get_ranked()
# raw JSON (dict / list) - use key access
```

### `client.profile.bulk_track_progress(body: list[str], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/profile/trackprogress/bulk`
- Plans: `pro`, `custom`
- Get ranked track progress for multiple account IDs in a single request (L3AGUE bulk endpoint). Body: array of Epic account IDs.

```python
result = client.profile.bulk_track_progress(["accountId1", "accountId2"])
# raw JSON (dict / list) - use key access
```

### `client.profile.get_tracks(*, ends_before: str | None = None, ends_after: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/profile/tracks`
- Plans: `pro`, `custom`
- Get all available ranked game mode tracks — modes, division counts, and season dates. Useful for building mode selectors or understanding what tracks exist.

```python
result = client.profile.get_tracks()
# raw JSON (dict / list) - use key access
```

