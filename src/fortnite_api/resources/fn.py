from __future__ import annotations

from typing import Any

from ._base import Resource

class FNResource(Resource):
    def get_br_inventory(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the Battle Royale inventory for a player."""
        return self._t.request("GET", f"/fn/br-inventory/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_enabled_features(self, *, fortnite_token: str | None = None) -> Any:
        """Get the list of enabled game features."""
        return self._t.request("GET", "/fn/enabled-features", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_entitlement(self, *, fortnite_token: str | None = None) -> Any:
        """Get entitlements for the authenticated player. Requires x-fortnite-token."""
        return self._t.request("GET", "/fn/entitlement", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def request_entitlement(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Request an entitlement grant for a player. Requires x-fortnite-token."""
        return self._t.request("POST", f"/fn/entitlement/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_keychain(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current keychain (used for Save the World trading)."""
        return self._t.request("GET", "/fn/keychain", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_privacy(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get privacy settings for a player. Requires x-fortnite-token."""
        return self._t.request("GET", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def update_privacy(self, account_id: str, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Update privacy settings for a player. Requires x-fortnite-token."""
        return self._t.request("POST", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_receipts(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get purchase receipts for a player."""
        return self._t.request("GET", f"/fn/receipts/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_version(self, platform: str, *, version: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite version for a platform."""
        return self._t.request("GET", f"/fn/version/{platform}", "v2",
            params={"version": version}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncFNResource(Resource):
    async def get_br_inventory(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get the Battle Royale inventory for a player."""
        return await self._t.request("GET", f"/fn/br-inventory/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_enabled_features(self, *, fortnite_token: str | None = None) -> Any:
        """Get the list of enabled game features."""
        return await self._t.request("GET", "/fn/enabled-features", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_entitlement(self, *, fortnite_token: str | None = None) -> Any:
        """Get entitlements for the authenticated player. Requires x-fortnite-token."""
        return await self._t.request("GET", "/fn/entitlement", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def request_entitlement(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Request an entitlement grant for a player. Requires x-fortnite-token."""
        return await self._t.request("POST", f"/fn/entitlement/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_keychain(self, *, fortnite_token: str | None = None) -> Any:
        """Get the current keychain (used for Save the World trading)."""
        return await self._t.request("GET", "/fn/keychain", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_privacy(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get privacy settings for a player. Requires x-fortnite-token."""
        return await self._t.request("GET", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def update_privacy(self, account_id: str, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Update privacy settings for a player. Requires x-fortnite-token."""
        return await self._t.request("POST", f"/fn/privacy/{account_id}", "v2",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_receipts(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get purchase receipts for a player."""
        return await self._t.request("GET", f"/fn/receipts/{account_id}", "v2",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_version(self, platform: str, *, version: str | None = None, fortnite_token: str | None = None) -> Any:
        """Get the current Fortnite version for a platform."""
        return await self._t.request("GET", f"/fn/version/{platform}", "v2",
            params={"version": version}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
