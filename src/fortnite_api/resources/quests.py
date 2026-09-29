from __future__ import annotations

from typing import Any

from ..models import QuestDefinitionResult, QuestDefinitionsPage
from ._base import Resource

class QuestsResource(Resource):
    def get(self, account_id: str, *, resolve: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get active quests and challenges for a player. Requires x-fortnite-token.

        ``GET /api/v2/quests/{accountId}``
        """
        return self._t.request("GET", f"/quests/{account_id}", "v2",
            params={"resolve": resolve}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_definitions(self, *, template_ids: str | None = None, bundle: str | None = None, search: str | None = None, visible: bool | None = None, limit: int | None = None, offset: int | None = None, fortnite_token: str | None = None) -> QuestDefinitionsPage:
        """Quest definitions: title, description, objectives, rewards and icon for each quest templateId.

        ``GET /api/v2/quests/definitions``
        """
        return self._t.request("GET", "/quests/definitions", "v2",
            params={"templateIds": template_ids, "bundle": bundle, "search": search, "visible": visible, "limit": limit, "offset": offset}, json_body=None, fortnite_token=fortnite_token,
            response_type=QuestDefinitionsPage)

    def get_definition(self, template_id: str, *, fortnite_token: str | None = None) -> QuestDefinitionResult:
        """One quest definition, with its bundle.

        ``GET /api/v2/quests/definitions/{templateId}``
        """
        return self._t.request("GET", f"/quests/definitions/{template_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=QuestDefinitionResult)


class AsyncQuestsResource(Resource):
    async def get(self, account_id: str, *, resolve: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get active quests and challenges for a player. Requires x-fortnite-token.

        ``GET /api/v2/quests/{accountId}``
        """
        return await self._t.request("GET", f"/quests/{account_id}", "v2",
            params={"resolve": resolve}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_definitions(self, *, template_ids: str | None = None, bundle: str | None = None, search: str | None = None, visible: bool | None = None, limit: int | None = None, offset: int | None = None, fortnite_token: str | None = None) -> QuestDefinitionsPage:
        """Quest definitions: title, description, objectives, rewards and icon for each quest templateId.

        ``GET /api/v2/quests/definitions``
        """
        return await self._t.request("GET", "/quests/definitions", "v2",
            params={"templateIds": template_ids, "bundle": bundle, "search": search, "visible": visible, "limit": limit, "offset": offset}, json_body=None, fortnite_token=fortnite_token,
            response_type=QuestDefinitionsPage)

    async def get_definition(self, template_id: str, *, fortnite_token: str | None = None) -> QuestDefinitionResult:
        """One quest definition, with its bundle.

        ``GET /api/v2/quests/definitions/{templateId}``
        """
        return await self._t.request("GET", f"/quests/definitions/{template_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=QuestDefinitionResult)
