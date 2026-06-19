from __future__ import annotations

from typing import Any

from ._base import Resource

class TournamentsResource(Resource):
    def get_cashprize(self, event_window_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the payout table for a specific event window."""
        return self._t.request("GET", f"/events/cashprize/{event_window_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_cashprizes(self, *, fortnite_token: str | None = None) -> Any:
        """Get all payout tables extracted from Epic's events download."""
        return self._t.request("GET", "/events/cashprizes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_current(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active and upcoming tournaments, enriched with CMS metadata."""
        return self._t.request("GET", "/events/global", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_global_history(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all tournaments including past ones, enriched with CMS metadata."""
        return self._t.request("GET", "/events/global/history", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_leaderboard(self, *, event_id: str | None = None, event_window_id: str | None = None, page: int | None = None, leaderboard_def: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a paginated tournament leaderboard for the given event window."""
        return self._t.request("GET", "/events/global/leaderboard", "v1",
            params={"eventId": event_id, "eventWindowId": event_window_id, "page": page, "leaderboardDef": leaderboard_def, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_player(self, *, region: str | None = None, platform: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the authenticated player's tournament data — token progression and event participation."""
        return self._t.request("GET", "/events/player", "v1",
            params={"region": region, "platform": platform, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_power_rankings(self, *, page: int | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the Fortnite Power Rankings leaderboard — the official competitive skill rating."""
        return self._t.request("GET", "/events/powerrankings", "v1",
            params={"page": page, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_power_rankings_player(self, identifier: str, *, fortnite_token: str | None = None) -> Any:
        """Look up a player's Power Rankings entry by display name or account ID."""
        return self._t.request("GET", f"/events/powerrankings/player/{identifier}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def search_power_rankings(self, *, q: str | None = None, limit: int | None = None, fortnite_token: str | None = None) -> Any:
        """Search Power Rankings players by display name (partial, case-insensitive)."""
        return self._t.request("GET", "/events/powerrankings/search", "v1",
            params={"q": q, "limit": limit}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_sessions(self, *, event_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get sessions for a specific event."""
        return self._t.request("GET", "/events/sessions", "v1",
            params={"eventId": event_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_stat_leaders(self, event_id: str, event_window_id: str, stat_key: str, *, top: int | None = None, fortnite_token: str | None = None) -> Any:
        """Get the top performers for a specific tracked stat across the entire leaderboard."""
        return self._t.request("GET", f"/events/stats/{event_id}/{event_window_id}/{stat_key}", "v1",
            params={"top": top}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_team_stats(self, event_id: str, event_window_id: str, stat_key: str, team_identifier: str, *, twitter: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get all tracked stats for a specific team identified by Epic account ID or display name."""
        return self._t.request("GET", f"/events/stats/{event_id}/{event_window_id}/{stat_key}/{team_identifier}", "v1",
            params={"twitter": twitter}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_tokens(self, team_account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get the raw token set for one or more players directly from Epic's tokens endpoint."""
        return self._t.request("GET", "/events/tokens", "v1",
            params={"teamAccountIds": ",".join(team_account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_tracker(self, *, account_id: str | None = None, valid_only: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get tournament tracker data for a player — token progression and past event participation."""
        return self._t.request("GET", "/events/tracker", "v1",
            params={"accountId": account_id, "validOnly": valid_only}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_tracker_debug(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Admin debug: returns the raw Epic /download response for a player."""
        return self._t.request("GET", "/events/tracker/debug", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_tracker_eligibility(self, *, account_id: str | None = None, days: int | None = None, required_tournaments: int | None = None, fortnite_token: str | None = None) -> Any:
        """Check whether a player is eligible for tournaments based on their participation history."""
        return self._t.request("GET", "/events/tracker/eligibility", "v1",
            params={"accountId": account_id, "days": days, "requiredTournaments": required_tournaments}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def check_eligibility(self, identifier: str, event_id: str, *, event_window_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Check a player's eligibility for a specific event — verifies all token requirements"""
        return self._t.request("GET", f"/events/tracker/eligibility/{identifier}/{event_id}", "v1",
            params={"eventWindowId": event_window_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncTournamentsResource(Resource):
    async def get_cashprize(self, event_window_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the payout table for a specific event window."""
        return await self._t.request("GET", f"/events/cashprize/{event_window_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_cashprizes(self, *, fortnite_token: str | None = None) -> Any:
        """Get all payout tables extracted from Epic's events download."""
        return await self._t.request("GET", "/events/cashprizes", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_current(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get currently active and upcoming tournaments, enriched with CMS metadata."""
        return await self._t.request("GET", "/events/global", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_global_history(self, *, lang: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get all tournaments including past ones, enriched with CMS metadata."""
        return await self._t.request("GET", "/events/global/history", "v1",
            params={"lang": lang}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_leaderboard(self, *, event_id: str | None = None, event_window_id: str | None = None, page: int | None = None, leaderboard_def: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get a paginated tournament leaderboard for the given event window."""
        return await self._t.request("GET", "/events/global/leaderboard", "v1",
            params={"eventId": event_id, "eventWindowId": event_window_id, "page": page, "leaderboardDef": leaderboard_def, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_player(self, *, region: str | None = None, platform: str | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the authenticated player's tournament data — token progression and event participation."""
        return await self._t.request("GET", "/events/player", "v1",
            params={"region": region, "platform": platform, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_power_rankings(self, *, page: int | None = None, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the Fortnite Power Rankings leaderboard — the official competitive skill rating."""
        return await self._t.request("GET", "/events/powerrankings", "v1",
            params={"page": page, "accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_power_rankings_player(self, identifier: str, *, fortnite_token: str | None = None) -> Any:
        """Look up a player's Power Rankings entry by display name or account ID."""
        return await self._t.request("GET", f"/events/powerrankings/player/{identifier}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def search_power_rankings(self, *, q: str | None = None, limit: int | None = None, fortnite_token: str | None = None) -> Any:
        """Search Power Rankings players by display name (partial, case-insensitive)."""
        return await self._t.request("GET", "/events/powerrankings/search", "v1",
            params={"q": q, "limit": limit}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_sessions(self, *, event_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get sessions for a specific event."""
        return await self._t.request("GET", "/events/sessions", "v1",
            params={"eventId": event_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_stat_leaders(self, event_id: str, event_window_id: str, stat_key: str, *, top: int | None = None, fortnite_token: str | None = None) -> Any:
        """Get the top performers for a specific tracked stat across the entire leaderboard."""
        return await self._t.request("GET", f"/events/stats/{event_id}/{event_window_id}/{stat_key}", "v1",
            params={"top": top}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_team_stats(self, event_id: str, event_window_id: str, stat_key: str, team_identifier: str, *, twitter: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get all tracked stats for a specific team identified by Epic account ID or display name."""
        return await self._t.request("GET", f"/events/stats/{event_id}/{event_window_id}/{stat_key}/{team_identifier}", "v1",
            params={"twitter": twitter}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_tokens(self, team_account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get the raw token set for one or more players directly from Epic's tokens endpoint."""
        return await self._t.request("GET", "/events/tokens", "v1",
            params={"teamAccountIds": ",".join(team_account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_tracker(self, *, account_id: str | None = None, valid_only: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get tournament tracker data for a player — token progression and past event participation."""
        return await self._t.request("GET", "/events/tracker", "v1",
            params={"accountId": account_id, "validOnly": valid_only}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_tracker_debug(self, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Admin debug: returns the raw Epic /download response for a player."""
        return await self._t.request("GET", "/events/tracker/debug", "v1",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_tracker_eligibility(self, *, account_id: str | None = None, days: int | None = None, required_tournaments: int | None = None, fortnite_token: str | None = None) -> Any:
        """Check whether a player is eligible for tournaments based on their participation history."""
        return await self._t.request("GET", "/events/tracker/eligibility", "v1",
            params={"accountId": account_id, "days": days, "requiredTournaments": required_tournaments}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def check_eligibility(self, identifier: str, event_id: str, *, event_window_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Check a player's eligibility for a specific event — verifies all token requirements"""
        return await self._t.request("GET", f"/events/tracker/eligibility/{identifier}/{event_id}", "v1",
            params={"eventWindowId": event_window_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
