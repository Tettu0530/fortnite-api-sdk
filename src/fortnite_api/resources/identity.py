from __future__ import annotations

from typing import Any

from ..models import LinkRequest
from ._base import Resource

class IdentityResource(Resource):
    def link(self, body: LinkRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Store a Discord→Epic link. The caller runs the /oauth flow first (so it holds a real, API-minted
        epic_account_id) and reports the Discord user who authorised.

        ``POST /api/v1/identity/link``
        """
        return self._t.request("POST", "/identity/link", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    def get(self, discord_id: str, *, fortnite_token: str | None = None) -> Any:
        """Resolve a Discord user to their linked Epic account.

        ``GET /api/v1/identity/{discordId}``
        """
        return self._t.request("GET", f"/identity/{discord_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncIdentityResource(Resource):
    async def link(self, body: LinkRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Store a Discord→Epic link. The caller runs the /oauth flow first (so it holds a real, API-minted
        epic_account_id) and reports the Discord user who authorised.

        ``POST /api/v1/identity/link``
        """
        return await self._t.request("POST", "/identity/link", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    async def get(self, discord_id: str, *, fortnite_token: str | None = None) -> Any:
        """Resolve a Discord user to their linked Epic account.

        ``GET /api/v1/identity/{discordId}``
        """
        return await self._t.request("GET", f"/identity/{discord_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
