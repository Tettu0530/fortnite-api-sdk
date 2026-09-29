from __future__ import annotations

from typing import Any

from ..models import InitiateRequest, RegisterAccountRequest
from ._base import Resource

class CustomMatchResource(Resource):
    def initiate(self, body: InitiateRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Queue a custom key push for a list of players.

        ``POST /api/v1/custom-match/initiate``
        """
        return self._t.request("POST", "/custom-match/initiate", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    def get_status(self, player_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the current or historical status of a player's key-push job.

        ``GET /api/v1/custom-match/status/{playerId}``
        """
        return self._t.request("GET", f"/custom-match/status/{player_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_bots(self, *, fortnite_token: str | None = None) -> Any:
        """Show the caller's own bot pool with live per-worker readiness — use this to check capacity before
        launching a large multi-lobby scrim.

        ``GET /api/v1/custom-match/bots``
        """
        return self._t.request("GET", "/custom-match/bots", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def register_account(self, body: RegisterAccountRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Register one of the caller's OWN Epic accounts into their dedicated bot pool. The account's device-
        auth is encrypted at rest. Lands as `provisioning` until a worker is attached.

        ``POST /api/v1/custom-match/accounts``
        """
        return self._t.request("POST", "/custom-match/accounts", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    def delete_account(self, id: int, *, fortnite_token: str | None = None) -> Any:
        """Remove one of the caller's own registered accounts (ownership-enforced).

        ``DELETE /api/v1/custom-match/accounts/{id}``
        """
        return self._t.request("DELETE", f"/custom-match/accounts/{id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncCustomMatchResource(Resource):
    async def initiate(self, body: InitiateRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Queue a custom key push for a list of players.

        ``POST /api/v1/custom-match/initiate``
        """
        return await self._t.request("POST", "/custom-match/initiate", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    async def get_status(self, player_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the current or historical status of a player's key-push job.

        ``GET /api/v1/custom-match/status/{playerId}``
        """
        return await self._t.request("GET", f"/custom-match/status/{player_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_bots(self, *, fortnite_token: str | None = None) -> Any:
        """Show the caller's own bot pool with live per-worker readiness — use this to check capacity before
        launching a large multi-lobby scrim.

        ``GET /api/v1/custom-match/bots``
        """
        return await self._t.request("GET", "/custom-match/bots", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def register_account(self, body: RegisterAccountRequest | dict[str, Any], *, fortnite_token: str | None = None) -> Any:
        """Register one of the caller's OWN Epic accounts into their dedicated bot pool. The account's device-
        auth is encrypted at rest. Lands as `provisioning` until a worker is attached.

        ``POST /api/v1/custom-match/accounts``
        """
        return await self._t.request("POST", "/custom-match/accounts", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    async def delete_account(self, id: int, *, fortnite_token: str | None = None) -> Any:
        """Remove one of the caller's own registered accounts (ownership-enforced).

        ``DELETE /api/v1/custom-match/accounts/{id}``
        """
        return await self._t.request("DELETE", f"/custom-match/accounts/{id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
