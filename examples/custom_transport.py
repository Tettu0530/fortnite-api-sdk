"""A minimal custom async transport.

``AsyncFortniteAPI(transport=...)`` accepts any object implementing
``fortnite_api.AsyncTransportProtocol``. This example sends requests with its own
``httpx.AsyncClient`` (swap in aiohttp or anything else) and reuses ``fortnite_api.interpret``
so URLs, headers, bodies, errors, envelopes and typed models behave exactly like the built-in
transport. It also shows where a wrapper can add policy: an endpoint allowlist and a request
counter (e.g. for quota accounting).

Two rules keep a transport as safe as the built-in one:

* Never let the HTTP library follow redirects: every request below passes
  ``follow_redirects=False``. httpx and aiohttp both re-send ``x-api-key`` / ``x-fortnite-token``
  to a redirect target on another host. With aiohttp, pass ``allow_redirects=False`` on every
  request (its default is ``True``). If you do want to follow redirects, send only
  ``interpret.redirect_headers(headers, from_url, to_url)`` to the next hop.
* Raise ``APIConnectionError`` / ``APITimeoutError`` (``raise ... from exc``) for network failures,
  so ``except FortniteAPIError`` catches them. Do not copy the original error text into the
  message: it can contain header values. (aiohttp: ``aiohttp.ClientError`` and
  ``asyncio.TimeoutError``.)

Run with ``FN_API_KEY=... uv run python examples/custom_transport.py``.
"""

from __future__ import annotations

import asyncio
import os
from collections import Counter
from collections.abc import Mapping
from typing import Any, NoReturn

import httpx

from fortnite_api import (
    APIConnectionError,
    APITimeoutError,
    AsyncFortniteAPI,
    AsyncTransportProtocol,
    FortniteAPIError,
    interpret,
)
from fortnite_api.interpret import MultipartFiles


class EndpointNotAllowedError(FortniteAPIError):
    """Raised before any network I/O when a path is not on the allowlist."""


def raise_network_error(exc: httpx.TransportError) -> NoReturn:
    """Map an httpx failure to the SDK's exceptions without echoing its message."""
    if isinstance(exc, httpx.TimeoutException):
        raise APITimeoutError(f"Request timed out ({type(exc).__name__})") from exc
    raise APIConnectionError(f"Connection failed ({type(exc).__name__})") from exc


class MyAsyncTransport:
    """Implements ``AsyncTransportProtocol`` on top of a caller-owned ``httpx.AsyncClient``."""

    def __init__(
        self,
        api_key: str,
        *,
        http: httpx.AsyncClient,
        base_url: str = interpret.DEFAULT_BASE_URL,
        allowed_prefixes: tuple[str, ...] = (),
    ) -> None:
        self._api_key = api_key
        self._http = http
        self.base_url = base_url
        self.allowed_prefixes = allowed_prefixes
        self.calls: Counter[str] = Counter()

    def __repr__(self) -> str:  # never print the key
        return f"MyAsyncTransport(base_url={self.base_url!r}, api_key='***')"

    def _check(self, method: str, path: str) -> None:
        if self.allowed_prefixes and not path.startswith(self.allowed_prefixes):
            raise EndpointNotAllowedError(f"{method} {path} is not allowlisted", 0)
        self.calls[path] += 1

    async def _send(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            # follow_redirects=False on every call, whatever the shared client was configured with.
            return await self._http.request(method, url, follow_redirects=False, **kwargs)
        except httpx.TransportError as exc:
            raise_network_error(exc)

    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any = None,
        fortnite_token: str | None = None,
        response_type: Any = None,
        retryable: bool = False,
    ) -> Any:
        self._check(method, path)
        resp = await self._send(
            method,
            interpret.build_url(self.base_url, path, version),
            params=interpret.clean_params(params),
            json=interpret.serialize_body(json_body),
            headers=interpret.build_headers(self._api_key, fortnite_token),
        )
        return interpret.interpret_json(resp.status_code, resp.headers, resp.content, response_type)

    async def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        self._check("GET", path)
        resp = await self._send(
            "GET",
            interpret.build_url(self.base_url, path, version),
            headers=interpret.build_headers(self._api_key, fortnite_token, json=False),
        )
        return interpret.interpret_binary(resp.status_code, resp.headers, resp.content)

    async def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        self._check("GET", path)
        resp = await self._send(
            "GET",
            interpret.build_url(self.base_url, path, version),
            params=interpret.clean_params(params),
            headers=interpret.build_headers(self._api_key, fortnite_token, json=False),
        )
        return interpret.interpret_redirect(resp.status_code, resp.headers, resp.content, str(resp.url))

    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        self._check("POST", path)
        resp = await self._send(
            "POST",
            interpret.build_url(self.base_url, path, "v1"),
            headers=interpret.build_headers(self._api_key, json=False),
            files=files,
        )
        return interpret.interpret_json(resp.status_code, resp.headers, resp.content, response_type, unwrap=unwrap)


async def main() -> None:
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as http:
        transport = MyAsyncTransport(
            os.environ.get("FN_API_KEY", "your-api-key"),
            http=http,
            allowed_prefixes=("/weapons", "/shop"),
        )
        assert isinstance(transport, AsyncTransportProtocol)
        client = AsyncFortniteAPI(transport=transport)
        weapons = await client.weapons.get()
        print("weapons:", len(weapons))
        try:
            await client.account.get_by_id("some-account")
        except EndpointNotAllowedError as err:
            print("blocked:", err.message)
        print("calls:", dict(transport.calls))


if __name__ == "__main__":
    asyncio.run(main())
