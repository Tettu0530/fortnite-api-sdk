from __future__ import annotations

from typing import Any

from ._base import Resource

class FNResource(Resource):
    def get_br_inventory(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the Battle Royale inventory for a player.

        ``GET /api/v2/fn/br-inventory/{accountId}``
        """
        return self._t.request("GET", f"/fn/br-inventory/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_enabled_features(self, *, fortnite_token: str | None = None) -> Any:
        """Get the list of enabled game features.

        ``GET /api/v2/fn/enabled-features``
        """
        return self._t.request("GET", "/fn/enabled-features", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_entitlement(self, *, fortnite_token: str | None = None) -> Any:
        """Get entitlements for the authenticated player. Requires x-fortnite-token.

        ``GET /api/v2/fn/entitlement``
        """
        return self._t.request("GET", "/fn/entitlement", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def request_entitlement(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Request an entitlement grant for a player. Requires x-fortnite-token.

        ``POST /api/v2/fn/entitlement/{accountId}``
        """
        return self._t.request("POST", f"/fn/entitlement/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_keychain(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current keychain (used for Save the World trading).

        ``GET /api/v2/fn/keychain``
        """
        return self._t.request("GET", "/fn/keychain", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_privacy(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get privacy settings for a player. Requires x-fortnite-token.

        ``GET /api/v2/fn/privacy/{accountId}``
        """
        return self._t.request("GET", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def update_privacy(self, account_id: str, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Update privacy settings for a player. Requires x-fortnite-token.

        ``POST /api/v2/fn/privacy/{accountId}``
        """
        return self._t.request("POST", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    def get_receipts(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get purchase receipts for a player.

        ``GET /api/v2/fn/receipts/{accountId}``
        """
        return self._t.request("GET", f"/fn/receipts/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    def get_version(self, platform: str, *, version: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite version for a platform.

        ``GET /api/v2/fn/version/{platform}``
        """
        return self._t.request("GET", f"/fn/version/{platform}", "v2",
            params={"version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)


class AsyncFNResource(Resource):
    async def get_br_inventory(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the Battle Royale inventory for a player.

        ``GET /api/v2/fn/br-inventory/{accountId}``
        """
        return await self._t.request("GET", f"/fn/br-inventory/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_enabled_features(self, *, fortnite_token: str | None = None) -> Any:
        """Get the list of enabled game features.

        ``GET /api/v2/fn/enabled-features``
        """
        return await self._t.request("GET", "/fn/enabled-features", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_entitlement(self, *, fortnite_token: str | None = None) -> Any:
        """Get entitlements for the authenticated player. Requires x-fortnite-token.

        ``GET /api/v2/fn/entitlement``
        """
        return await self._t.request("GET", "/fn/entitlement", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def request_entitlement(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Request an entitlement grant for a player. Requires x-fortnite-token.

        ``POST /api/v2/fn/entitlement/{accountId}``
        """
        return await self._t.request("POST", f"/fn/entitlement/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_keychain(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current keychain (used for Save the World trading).

        ``GET /api/v2/fn/keychain``
        """
        return await self._t.request("GET", "/fn/keychain", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_privacy(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get privacy settings for a player. Requires x-fortnite-token.

        ``GET /api/v2/fn/privacy/{accountId}``
        """
        return await self._t.request("GET", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def update_privacy(self, account_id: str, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Update privacy settings for a player. Requires x-fortnite-token.

        ``POST /api/v2/fn/privacy/{accountId}``
        """
        return await self._t.request("POST", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            response_type=None)

    async def get_receipts(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get purchase receipts for a player.

        ``GET /api/v2/fn/receipts/{accountId}``
        """
        return await self._t.request("GET", f"/fn/receipts/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            response_type=None)

    async def get_version(self, platform: str, *, version: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite version for a platform.

        ``GET /api/v2/fn/version/{platform}``
        """
        return await self._t.request("GET", f"/fn/version/{platform}", "v2",
            params={"version": version}, json_body=None, fortnite_token=fortnite_token,
            response_type=None)
