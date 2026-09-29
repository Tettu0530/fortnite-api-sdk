# Accounts and auth: account, friends, oauth, identity, fn, quests, custom_match

Account lookups, social graph, OAuth flows that produce the `x-fortnite-token`, per-player game
data, quests, and custom-match key pushes. Nearly everything here returns raw JSON (`Any`) - use
key access and inspect the payload before relying on key names.

Signatures, return types, HTTP paths and descriptions below are extracted from the SDK source
(`fortnite_api/resources/*.py`); only the guidance section is hand-written. All methods exist with
the same signature on `AsyncFortniteAPI` (add `await`). "Token:" lines appear only where the API
description states something about `x-fortnite-token`. "Plans:" lines come from the `x-plans`
extension of the bundled OpenAPI spec (which api-fortnite.com plans may call the endpoint).

## Guidance

- **Name -> account ID.** Most player endpoints want the Epic account ID (32 hex chars).
  `account.get_by_display_name("Ninja")` for Epic names, `account.get_by_external_display_name(
  "psn" | "xbl" | "steam" | "nintendo" | "twitch" | "github", name)` for platform names,
  `account.get_display_names(ids)` / `account.get_bulk(ids)` for the reverse (README: bulk max 100).
- **Getting a user token (device-code flow):**
  1. `flow = client.oauth.get_token()` -> dict with a `flowId` and a URL the player opens.
  2. Poll `client.oauth.complete({"flowId": flow["flowId"]})`; it answers 202
     `AUTHORIZATION_PENDING` until the player finishes and 429 `RATE_LIMITED` if you poll too fast,
     so sleep a few seconds between polls and treat 202 as "keep waiting".
  3. The result carries the access token (pass it as `fortnite_token=`) and a `deviceAuth`
     (`accountId`, `deviceId`, `secret`). Store the device auth securely and re-authenticate with
     `oauth.refresh_device(...)` when a token call returns 401; revoke it with
     `oauth.revoke_device(...)` when the user disconnects.
  Inspect the returned dicts for exact key names before hard-coding them.
- **Authorization-code flow:** `oauth.get_authorize_url(redirect_uri=...)` -> redirect the user ->
  `oauth.link({"code": ..., "redirectUri": ...})`.
- **Bodies:** OAuth / identity / custom_match bodies accept the request model from
  `fortnite_api.models` or a dict with the API's key names (shown in each example).
- **Quests:** `quests.get(account_id, resolve=True, fortnite_token=...)` needs the player's token;
  `quests.get_definitions()` / `get_definition()` are public and typed.
- **Tokens are credentials.** Never log `fortnite_token`, refresh tokens or device-auth secrets.

## Contents

- [`client.account`](#clientaccount)
- [`client.friends`](#clientfriends)
- [`client.oauth`](#clientoauth)
- [`client.identity`](#clientidentity)
- [`client.fn`](#clientfn)
- [`client.quests`](#clientquests)
- [`client.custom_match`](#clientcustom_match)

## `client.account`

### `client.account.get_by_id(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/{accountId}`
- Plans: `free`, `pro`, `custom`
- Get account information by Epic account ID.

```python
result = client.account.get_by_id("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.account.get_bulk(account_ids: list[str], *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/bulk`
- Plans: `free`, `pro`, `custom`
- Get multiple accounts by Epic account IDs in a single request.

```python
result = client.account.get_bulk(["accountId1", "accountId2"])
# raw JSON (dict / list) - use key access
```

### `client.account.get_by_display_name(display_name: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/displayName/{displayName}`
- Plans: `free`, `pro`, `custom`
- Get account information by Epic display name.

```python
result = client.account.get_by_display_name("<display_name>")
# raw JSON (dict / list) - use key access
```

### `client.account.get_display_names(account_ids: list[str], *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/displaynames`
- Plans: `free`, `pro`, `custom`
- Resolve one or more Epic account IDs to their display names.

```python
result = client.account.get_display_names(["accountId1", "accountId2"])
# raw JSON (dict / list) - use key access
```

### `client.account.bulk_external_display_names(body: Any, *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/account/external/displayNames/bulk`
- Plans: `free`, `pro`, `custom`
- Bulk lookup accounts by external display names.

```python
result = client.account.bulk_external_display_names([{"externalAuthType": "psn", "displayName": "PSNUser1"}])
# raw JSON (dict / list) - use key access
```

### `client.account.bulk_external_ids(body: Any, *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/account/external/ids/bulk`
- Plans: `free`, `pro`, `custom`
- Bulk lookup accounts by external platform IDs.

```python
result = client.account.bulk_external_ids([{"externalAuthType": "psn", "externalId": "psn-id-123"}])
# raw JSON (dict / list) - use key access
```

### `client.account.get_by_external_display_name(external_auth_type: str, display_name: str, *, case_insensitive: bool | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/external/{externalAuthType}/displayName/{displayName}`
- Plans: `free`, `pro`, `custom`
- Get account by display name from an external auth provider (e.g. psn, xbl, nintendo).

```python
result = client.account.get_by_external_display_name("<external_auth_type>", "<display_name>")
# raw JSON (dict / list) - use key access
```

### `client.account.get_epic_id_sdk(account_ids: list[str], *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/sdk`
- Plans: `free`, `pro`, `custom`
- Epic ID SDK v2 account lookup — returns extended account info via the Developer Portal API. Accepts one or more comma-separated Epic account IDs.

```python
result = client.account.get_epic_id_sdk(["accountId1", "accountId2"])
# raw JSON (dict / list) - use key access
```

### `client.account.get_external_auths(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/{accountId}/externalAuths`
- Plans: `free`, `pro`, `custom`
- Get all external auth connections for an account.

```python
result = client.account.get_external_auths("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.account.get_external_auth(account_id: str, auth_type: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/account/{accountId}/externalAuths/{authType}`
- Plans: `free`, `pro`, `custom`
- Get a specific external auth connection for an account.

```python
result = client.account.get_external_auth("<account_id>", "<auth_type>")
# raw JSON (dict / list) - use key access
```

## `client.friends`

### `client.friends.get_blocklist(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/blocklist`
- Plans: `pro`, `custom`
- Get a player's blocklist.

```python
result = client.friends.get_blocklist("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_friends(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/friends`
- Plans: `pro`, `custom`
- Get a player's full friends list.

```python
result = client.friends.get_friends("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_friend(account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/friends/{friendId}`
- Plans: `pro`, `custom`
- Get details for a specific friend of a player.

```python
result = client.friends.get_friend("<account_id>", "<friend_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_mutual_friends(account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/friends/{friendId}/mutual`
- Plans: `pro`, `custom`
- Get mutual friends between two players.

```python
result = client.friends.get_mutual_friends("<account_id>", "<friend_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_incoming(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/incoming`
- Plans: `pro`, `custom`
- Get incoming friend requests for a player.

```python
result = client.friends.get_incoming("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_outgoing(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/outgoing`
- Plans: `pro`, `custom`
- Get outgoing friend requests sent by a player.

```python
result = client.friends.get_outgoing("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_suggested(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/suggested`
- Plans: `pro`, `custom`
- Get suggested friends for a player.

```python
result = client.friends.get_suggested("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.friends.get_summary(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/friends/{accountId}/summary`
- Plans: `pro`, `custom`
- Get a summary of a player's friends, incoming/outgoing requests, and blocklist counts.

```python
result = client.friends.get_summary("<account_id>")
# raw JSON (dict / list) - use key access
```

## `client.oauth`

### `client.oauth.get_authorize_url(*, redirect_uri: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/oauth/authorize-url`
- Plans: `pro`, `custom`
- Returns the Epic Games authorization URL to redirect the user to. The user will see Epic's standard login page — no scary device confirmation page. After login, Epic redirects to your redirect_uri with ?code=... Then call POST /oauth/link with that code to get the Fortnite access token + device auth.

```python
result = client.oauth.get_authorize_url()
# raw JSON (dict / list) - use key access
```

### `client.oauth.complete(body: CompleteOAuthRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/complete`
- Plans: `pro`, `custom`
- Complete the device code OAuth flow by polling with the flowId returned from GET /oauth/get-token. Returns 202 with AUTHORIZATION_PENDING while the user has not yet authenticated. Returns 429 with RATE_LIMITED if polling too fast.

```python
result = client.oauth.complete({"flowId": "..."})
# raw JSON (dict / list) - use key access
```

### `client.oauth.exchange_code(body: ExchangeCodeRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/exchange-code`
- Plans: `pro`, `custom`
- Exchange an authorization code for an Epic access token.

```python
result = client.oauth.exchange_code({"code": "...", "redirectUri": "...", "clientId": "...", "clientSecret": "..."})
# raw JSON (dict / list) - use key access
```

### `client.oauth.get_token(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/oauth/get-token`
- Plans: `pro`, `custom`
- Initiate the device code OAuth flow. Returns a flowId and a user-facing URL where the user must authenticate. Poll POST /oauth/complete with the flowId to retrieve the token once the user has authorized.

```python
result = client.oauth.get_token()
# raw JSON (dict / list) - use key access
```

### `client.oauth.link(body: LinkAccountRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/link`
- Plans: `pro`, `custom`
- Exchanges an Epic authorization code for a Fortnite access token and device auth credentials. Use the code returned by Epic after the user authorizes via the URL from GET /oauth/authorize-url. The returned deviceAuth (accountId + deviceId + secret) can be stored and used with POST /oauth/refresh- device to silently re-authenticate in the future — no browser required.

```python
result = client.oauth.link({"code": "...", "redirectUri": "...", "clientId": "...", "clientSecret": "..."})
# raw JSON (dict / list) - use key access
```

### `client.oauth.refresh_device(body: RefreshDeviceRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/refresh-device`
- Plans: `pro`, `custom`
- Re-authenticate silently using stored device auth credentials (accountId + deviceId + secret).

```python
result = client.oauth.refresh_device({"accountId": "...", "deviceId": "...", "secret": "..."})
# raw JSON (dict / list) - use key access
```

### `client.oauth.refresh_token(body: RefreshTokenRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/refresh-token`
- Plans: `pro`, `custom`
- Refresh an Epic access token using a refresh token.

```python
result = client.oauth.refresh_token({"refreshToken": "..."})
# raw JSON (dict / list) - use key access
```

### `client.oauth.revoke_device(body: RefreshDeviceRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/oauth/revoke-device`
- Plans: `pro`, `custom`
- Revoke a device auth at Epic so it can never be used to log in again. Send the same accountId + deviceId + secret that POST /oauth/complete returned; the credential is used once to prove ownership, then deleted on Epic's side. We keep no copy of device auths at any point, so this is the complete cleanup. 400 when the device auth is already revoked or does not match (Epic rejects the login).

```python
result = client.oauth.revoke_device({"accountId": "...", "deviceId": "...", "secret": "..."})
# raw JSON (dict / list) - use key access
```

## `client.identity`

### `client.identity.link(body: LinkRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/identity/link`
- Plans: `custom`
- Store a Discord→Epic link. The caller runs the /oauth flow first (so it holds a real, API-minted epic_account_id) and reports the Discord user who authorised.

```python
result = client.identity.link({"discord_id": "...", "epic_account_id": "...", "display_name": "..."})
# raw JSON (dict / list) - use key access
```

### `client.identity.get(discord_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/identity/{discordId}`
- Plans: `custom`
- Resolve a Discord user to their linked Epic account.

```python
result = client.identity.get("<discord_id>")
# raw JSON (dict / list) - use key access
```

## `client.fn`

### `client.fn.get_br_inventory(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/br-inventory/{accountId}`
- Plans: `pro`, `custom`
- Get the Battle Royale inventory for a player.

```python
result = client.fn.get_br_inventory("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.fn.get_enabled_features(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/enabled-features`
- Plans: `pro`, `custom`
- Get the list of enabled game features.

```python
result = client.fn.get_enabled_features()
# raw JSON (dict / list) - use key access
```

### `client.fn.get_entitlement(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/entitlement`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get entitlements for the authenticated player. Requires x-fortnite-token.

```python
result = client.fn.get_entitlement()
# raw JSON (dict / list) - use key access
```

### `client.fn.request_entitlement(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v2/fn/entitlement/{accountId}`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Request an entitlement grant for a player. Requires x-fortnite-token.

```python
result = client.fn.request_entitlement("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.fn.get_keychain(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/keychain`
- Plans: `pro`, `custom`
- Get the current keychain (used for Save the World trading).

```python
result = client.fn.get_keychain()
# raw JSON (dict / list) - use key access
```

### `client.fn.get_privacy(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/privacy/{accountId}`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get privacy settings for a player. Requires x-fortnite-token.

```python
result = client.fn.get_privacy("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.fn.update_privacy(account_id: str, body: Any, *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v2/fn/privacy/{accountId}`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Update privacy settings for a player. Requires x-fortnite-token.

```python
result = client.fn.update_privacy("<account_id>", {"optOutOfPublicLeaderboards": True})
# raw JSON (dict / list) - use key access
```

### `client.fn.get_receipts(account_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/receipts/{accountId}`
- Plans: `pro`, `custom`
- Get purchase receipts for a player.

```python
result = client.fn.get_receipts("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.fn.get_version(platform: str, *, version: str | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/fn/version/{platform}`
- Plans: `pro`, `custom`
- Get the current Fortnite version for a platform.

```python
result = client.fn.get_version("<platform>")
# raw JSON (dict / list) - use key access
```

## `client.quests`

### `client.quests.get(account_id: str, *, resolve: bool | None = None, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v2/quests/{accountId}`
- Plans: `pro`, `custom`
- Token: **required** (`x-fortnite-token`)
- Get active quests and challenges for a player. Requires x-fortnite-token.

```python
result = client.quests.get("<account_id>")
# raw JSON (dict / list) - use key access
```

### `client.quests.get_definitions(*, template_ids: str | None = None, bundle: str | None = None, search: str | None = None, visible: bool | None = None, limit: int | None = None, offset: int | None = None, fortnite_token: str | None = None) -> QuestDefinitionsPage`

- HTTP: `GET /api/v2/quests/definitions`
- Plans: `pro`, `custom`
- Quest definitions: title, description, objectives, rewards and icon for each quest templateId.
- `QuestDefinitionsPage` fields: `game_version` (gameVersion): `str | None`, `generated`: `str | None`, `total`: `int | None`, `offset`: `int | None`, `limit`: `int | None`, `quests`: `list[QuestDefinition] | None`, `not_found` (notFound): `list[str] | None`

```python
result = client.quests.get_definitions()
print(result.game_version)
```

### `client.quests.get_definition(template_id: str, *, fortnite_token: str | None = None) -> QuestDefinitionResult`

- HTTP: `GET /api/v2/quests/definitions/{templateId}`
- Plans: `pro`, `custom`
- One quest definition, with its bundle.
- `QuestDefinitionResult` fields: `game_version` (gameVersion): `str | None`, `quest`: `QuestDefinition | None`, `bundle`: `QuestBundleDefinition | None`

```python
result = client.quests.get_definition("<template_id>")
print(result.game_version)
```

## `client.custom_match`

### `client.custom_match.initiate(body: InitiateRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/custom-match/initiate`
- Plans: `custom`
- Queue a custom key push for a list of players.

```python
result = client.custom_match.initiate({"custom_key": "...", "players_id": ["..."]})
# raw JSON (dict / list) - use key access
```

### `client.custom_match.get_status(player_id: str, *, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/custom-match/status/{playerId}`
- Plans: `custom`
- Get the current or historical status of a player's key-push job.

```python
result = client.custom_match.get_status("<player_id>")
# raw JSON (dict / list) - use key access
```

### `client.custom_match.get_bots(*, fortnite_token: str | None = None) -> Any`

- HTTP: `GET /api/v1/custom-match/bots`
- Plans: `custom`
- Show the caller's own bot pool with live per-worker readiness — use this to check capacity before launching a large multi-lobby scrim.

```python
result = client.custom_match.get_bots()
# raw JSON (dict / list) - use key access
```

### `client.custom_match.register_account(body: RegisterAccountRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any`

- HTTP: `POST /api/v1/custom-match/accounts`
- Plans: `custom`
- Register one of the caller's OWN Epic accounts into their dedicated bot pool. The account's device- auth is encrypted at rest. Lands as `provisioning` until a worker is attached.

```python
result = client.custom_match.register_account({"label": "...", "device_auth_json": "...", "roles": ["..."]})
# raw JSON (dict / list) - use key access
```

### `client.custom_match.delete_account(id: int, *, fortnite_token: str | None = None) -> Any`

- HTTP: `DELETE /api/v1/custom-match/accounts/{id}`
- Plans: `custom`
- Remove one of the caller's own registered accounts (ownership-enforced).

```python
result = client.custom_match.delete_account(1)
# raw JSON (dict / list) - use key access
```

