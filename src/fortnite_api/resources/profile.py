from __future__ import annotations

from typing import Any

from ._base import Resource

class ProfileResource(Resource):
    def get_leaderboard(self, game_id: str, *, account_id: str | None = None, from_index: int | None = None, find_teams: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get a Habanero game leaderboard centered around an account (e.g. HazelnutSpread). The gameId maps to
        the internal Habanero game identifier.

        ``POST /api/v1/profile/leaderboard/{gameId}``
        """
        return self._t.request("POST", f"/profile/leaderboard/{game_id}", "v1",
            params={"accountId": account_id, "fromIndex": from_index, "findTeams": find_teams}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_level(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a player's XP, level, accountLevel, and battle pass tier. Parsed from QueryProfile
        (profileId=athena) — requires x-fortnite-token.

        ``GET /api/v1/profile/level``
        """
        return self._t.request("GET", "/profile/level", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_progress(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get raw Habanero track progress for a single account. Public — no token required.

        ``GET /api/v1/profile/progress``
        """
        return self._t.request("GET", "/profile/progress", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_ranked(self, *, display_name: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a player's enriched ranked progress — human-readable rank names, game mode labels, season dates,
        and isCurrent flag. Accepts either ?displayName= or ?accountId= (accountId skips the name lookup and
        is preferred).

        ``GET /api/v1/profile/ranked``
        """
        return self._t.request("GET", "/profile/ranked", "v1",
            params={"displayName": display_name, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def bulk_track_progress(self, body: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get ranked track progress for multiple account IDs in a single request (L3AGUE bulk endpoint). Body:
        array of Epic account IDs.

        ``POST /api/v1/profile/trackprogress/bulk``
        """
        return self._t.request("POST", "/profile/trackprogress/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    def get_tracks(self, *, ends_before: str | None = None, ends_after: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all available ranked game mode tracks — modes, division counts, and season dates. Useful for
        building mode selectors or understanding what tracks exist.

        ``GET /api/v1/profile/tracks``
        """
        return self._t.request("GET", "/profile/tracks", "v1",
            params={"endsBefore": ends_before, "endsAfter": ends_after}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncProfileResource(Resource):
    async def get_leaderboard(self, game_id: str, *, account_id: str | None = None, from_index: int | None = None, find_teams: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get a Habanero game leaderboard centered around an account (e.g. HazelnutSpread). The gameId maps to
        the internal Habanero game identifier.

        ``POST /api/v1/profile/leaderboard/{gameId}``
        """
        return await self._t.request("POST", f"/profile/leaderboard/{game_id}", "v1",
            params={"accountId": account_id, "fromIndex": from_index, "findTeams": find_teams}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_level(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a player's XP, level, accountLevel, and battle pass tier. Parsed from QueryProfile
        (profileId=athena) — requires x-fortnite-token.

        ``GET /api/v1/profile/level``
        """
        return await self._t.request("GET", "/profile/level", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_progress(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get raw Habanero track progress for a single account. Public — no token required.

        ``GET /api/v1/profile/progress``
        """
        return await self._t.request("GET", "/profile/progress", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_ranked(self, *, display_name: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a player's enriched ranked progress — human-readable rank names, game mode labels, season dates,
        and isCurrent flag. Accepts either ?displayName= or ?accountId= (accountId skips the name lookup and
        is preferred).

        ``GET /api/v1/profile/ranked``
        """
        return await self._t.request("GET", "/profile/ranked", "v1",
            params={"displayName": display_name, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def bulk_track_progress(self, body: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get ranked track progress for multiple account IDs in a single request (L3AGUE bulk endpoint). Body:
        array of Epic account IDs.

        ``POST /api/v1/profile/trackprogress/bulk``
        """
        return await self._t.request("POST", "/profile/trackprogress/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    async def get_tracks(self, *, ends_before: str | None = None, ends_after: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all available ranked game mode tracks — modes, division counts, and season dates. Useful for
        building mode selectors or understanding what tracks exist.

        ``GET /api/v1/profile/tracks``
        """
        return await self._t.request("GET", "/profile/tracks", "v1",
            params={"endsBefore": ends_before, "endsAfter": ends_after}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
