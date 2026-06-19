from __future__ import annotations

from typing import Any

from ._base import Resource

class QuestsResource(Resource):
    def get(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get active quests and challenges for a player."""
        return self._t.request("GET", f"/quests/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncQuestsResource(Resource):
    async def get(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get active quests and challenges for a player."""
        return await self._t.request("GET", f"/quests/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
