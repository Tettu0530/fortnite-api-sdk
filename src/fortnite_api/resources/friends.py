from __future__ import annotations

from typing import Any

from ._base import Resource

class FriendsResource(Resource):
    def get_blocklist(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's blocklist."""
        return self._t.request("GET", f"/friends/{account_id}/blocklist", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_friends(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's full friends list."""
        return self._t.request("GET", f"/friends/{account_id}/friends", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_friend(self, account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get details for a specific friend of a player."""
        return self._t.request("GET", f"/friends/{account_id}/friends/{friend_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_mutual_friends(self, account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get mutual friends between two players."""
        return self._t.request("GET", f"/friends/{account_id}/friends/{friend_id}/mutual", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_incoming(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get incoming friend requests for a player."""
        return self._t.request("GET", f"/friends/{account_id}/incoming", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_outgoing(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get outgoing friend requests sent by a player."""
        return self._t.request("GET", f"/friends/{account_id}/outgoing", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_suggested(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get suggested friends for a player."""
        return self._t.request("GET", f"/friends/{account_id}/suggested", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_summary(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a summary of a player's friends, incoming/outgoing requests, and blocklist counts."""
        return self._t.request("GET", f"/friends/{account_id}/summary", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncFriendsResource(Resource):
    async def get_blocklist(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's blocklist."""
        return await self._t.request("GET", f"/friends/{account_id}/blocklist", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_friends(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a player's full friends list."""
        return await self._t.request("GET", f"/friends/{account_id}/friends", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_friend(self, account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get details for a specific friend of a player."""
        return await self._t.request("GET", f"/friends/{account_id}/friends/{friend_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_mutual_friends(self, account_id: str, friend_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get mutual friends between two players."""
        return await self._t.request("GET", f"/friends/{account_id}/friends/{friend_id}/mutual", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_incoming(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get incoming friend requests for a player."""
        return await self._t.request("GET", f"/friends/{account_id}/incoming", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_outgoing(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get outgoing friend requests sent by a player."""
        return await self._t.request("GET", f"/friends/{account_id}/outgoing", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_suggested(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get suggested friends for a player."""
        return await self._t.request("GET", f"/friends/{account_id}/suggested", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_summary(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get a summary of a player's friends, incoming/outgoing requests, and blocklist counts."""
        return await self._t.request("GET", f"/friends/{account_id}/summary", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
