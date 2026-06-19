from __future__ import annotations

from typing import Any

from ._base import Resource

class OAuthResource(Resource):
    def get_authorize_url(self, *, redirect_uri: str | None = None, fortnite_token: str | None = None) -> Any:
        """Returns the Epic Games authorization URL to redirect the user to."""
        return self._t.request("GET", "/oauth/authorize-url", "v1",
            params={"redirectUri": redirect_uri}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def complete(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Complete the device code OAuth flow by polling with the flowId returned from GET /oauth/get-token."""
        return self._t.request("POST", "/oauth/complete", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def exchange_code(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Exchange an authorization code for an Epic access token."""
        return self._t.request("POST", "/oauth/exchange-code", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def get_token(self, *, fortnite_token: str | None = None) -> Any:
        """Initiate the device code OAuth flow."""
        return self._t.request("GET", "/oauth/get-token", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def link(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Exchanges an Epic authorization code for a Fortnite access token and device auth credentials."""
        return self._t.request("POST", "/oauth/link", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def refresh_device(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Re-authenticate silently using stored device auth credentials (accountId + deviceId + secret)."""
        return self._t.request("POST", "/oauth/refresh-device", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    def refresh_token(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Refresh an Epic access token using a refresh token."""
        return self._t.request("POST", "/oauth/refresh-token", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)


class AsyncOAuthResource(Resource):
    async def get_authorize_url(self, *, redirect_uri: str | None = None, fortnite_token: str | None = None) -> Any:
        """Returns the Epic Games authorization URL to redirect the user to."""
        return await self._t.request("GET", "/oauth/authorize-url", "v1",
            params={"redirectUri": redirect_uri}, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def complete(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Complete the device code OAuth flow by polling with the flowId returned from GET /oauth/get-token."""
        return await self._t.request("POST", "/oauth/complete", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def exchange_code(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Exchange an authorization code for an Epic access token."""
        return await self._t.request("POST", "/oauth/exchange-code", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def get_token(self, *, fortnite_token: str | None = None) -> Any:
        """Initiate the device code OAuth flow."""
        return await self._t.request("GET", "/oauth/get-token", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def link(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Exchanges an Epic authorization code for a Fortnite access token and device auth credentials."""
        return await self._t.request("POST", "/oauth/link", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def refresh_device(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Re-authenticate silently using stored device auth credentials (accountId + deviceId + secret)."""
        return await self._t.request("POST", "/oauth/refresh-device", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)

    async def refresh_token(self, body: Any, *, fortnite_token: str | None = None) -> Any:
        """Refresh an Epic access token using a refresh token."""
        return await self._t.request("POST", "/oauth/refresh-token", "v1",
            params=None, json_body=body, fortnite_token=fortnite_token,
            model=None, is_list=False)
