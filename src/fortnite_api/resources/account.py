from __future__ import annotations

from typing import Any

from ._base import Resource

class AccountResource(Resource):
    def get_by_id(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get account information by Epic account ID."""
        return self._t.request("GET", f"/account/{account_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_bulk(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get multiple accounts by Epic account IDs in a single request."""
        return self._t.request("GET", "/account/bulk", "v1",
            params={"accountId": account_ids}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_by_display_name(self, display_name: str, *, fortnite_token: str | None = None) -> Any:
        """Get account information by Epic display name."""
        return self._t.request("GET", f"/account/displayName/{display_name}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_display_names(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Resolve one or more Epic account IDs to their display names."""
        return self._t.request("GET", "/account/displaynames", "v1",
            params={"ids": ",".join(account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def bulk_external_display_names(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Bulk lookup accounts by external display names."""
        return self._t.request("POST", "/account/external/displayNames/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def bulk_external_ids(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Bulk lookup accounts by external platform IDs."""
        return self._t.request("POST", "/account/external/ids/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_by_external_display_name(self, external_auth_type: str, display_name: str, *, case_insensitive: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get account by display name from an external auth provider (e.g. psn, xbl, nintendo)."""
        return self._t.request("GET", f"/account/external/{external_auth_type}/displayName/{display_name}", "v1",
            params={"caseInsensitive": case_insensitive}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_epic_id_sdk(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Epic ID SDK v2 account lookup — returns extended account info via the Developer Portal API."""
        return self._t.request("GET", "/account/sdk", "v1",
            params={"accountId": ",".join(account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_external_auths(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get all external auth connections for an account."""
        return self._t.request("GET", f"/account/{account_id}/externalAuths", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_external_auth(self, account_id: str, auth_type: str, *, fortnite_token: str | None = None) -> Any:
        """Get a specific external auth connection for an account."""
        return self._t.request("GET", f"/account/{account_id}/externalAuths/{auth_type}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncAccountResource(Resource):
    async def get_by_id(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get account information by Epic account ID."""
        return await self._t.request("GET", f"/account/{account_id}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_bulk(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Get multiple accounts by Epic account IDs in a single request."""
        return await self._t.request("GET", "/account/bulk", "v1",
            params={"accountId": account_ids}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_by_display_name(self, display_name: str, *, fortnite_token: str | None = None) -> Any:
        """Get account information by Epic display name."""
        return await self._t.request("GET", f"/account/displayName/{display_name}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_display_names(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Resolve one or more Epic account IDs to their display names."""
        return await self._t.request("GET", "/account/displaynames", "v1",
            params={"ids": ",".join(account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def bulk_external_display_names(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Bulk lookup accounts by external display names."""
        return await self._t.request("POST", "/account/external/displayNames/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def bulk_external_ids(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Bulk lookup accounts by external platform IDs."""
        return await self._t.request("POST", "/account/external/ids/bulk", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_by_external_display_name(self, external_auth_type: str, display_name: str, *, case_insensitive: bool | None = None, fortnite_token: str | None = None) -> Any:
        """Get account by display name from an external auth provider (e.g. psn, xbl, nintendo)."""
        return await self._t.request("GET", f"/account/external/{external_auth_type}/displayName/{display_name}", "v1",
            params={"caseInsensitive": case_insensitive}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_epic_id_sdk(self, account_ids: list[str], *, fortnite_token: str | None = None) -> Any:
        """Epic ID SDK v2 account lookup — returns extended account info via the Developer Portal API."""
        return await self._t.request("GET", "/account/sdk", "v1",
            params={"accountId": ",".join(account_ids)}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_external_auths(self, account_id: str, *, fortnite_token: str | None = None) -> Any:
        """Get all external auth connections for an account."""
        return await self._t.request("GET", f"/account/{account_id}/externalAuths", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_external_auth(self, account_id: str, auth_type: str, *, fortnite_token: str | None = None) -> Any:
        """Get a specific external auth connection for an account."""
        return await self._t.request("GET", f"/account/{account_id}/externalAuths/{auth_type}", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)
