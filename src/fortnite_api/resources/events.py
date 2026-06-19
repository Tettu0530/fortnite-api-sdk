from __future__ import annotations

from typing import Any

from ._base import Resource

class EventsResource(Resource):
    def get_player_history(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's event participation history."""
        return self._t.request("GET", f"/events/players/{account_id}/history", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_window_leaderboard(self, event_id: str, event_window_id: str, *, page: int | None = None, leaderboard_def: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the paginated leaderboard for a specific event window."""
        return self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/leaderboard", "v2",
            params={"page": page, "leaderboardDef": leaderboard_def}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_window_leaderboard_player(self, event_id: str, event_window_id: str, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Find a player's rank and surrounding entries in an event window leaderboard."""
        return self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/leaderboard/player", "v2",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_player_window_standing(self, event_id: str, event_window_id: str, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's standing in a specific event window."""
        return self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/players/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncEventsResource(Resource):
    async def get_player_history(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's event participation history."""
        return await self._t.request("GET", f"/events/players/{account_id}/history", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_window_leaderboard(self, event_id: str, event_window_id: str, *, page: int | None = None, leaderboard_def: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the paginated leaderboard for a specific event window."""
        return await self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/leaderboard", "v2",
            params={"page": page, "leaderboardDef": leaderboard_def}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_window_leaderboard_player(self, event_id: str, event_window_id: str, *, account_id: str | None = None, fortnite_token: str | None = None) -> Any:
        """Find a player's rank and surrounding entries in an event window leaderboard."""
        return await self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/leaderboard/player", "v2",
            params={"accountId": account_id}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_player_window_standing(self, event_id: str, event_window_id: str, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's standing in a specific event window."""
        return await self._t.request("GET", f"/events/{event_id}/windows/{event_window_id}/players/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
