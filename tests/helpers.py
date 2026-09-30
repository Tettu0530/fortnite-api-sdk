"""Test helpers: clients whose built-in transport talks to an ``httpx.MockTransport``."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from fortnite_api import AsyncFortniteAPI, AsyncTransport, FortniteAPI, SyncTransport

Handler = Callable[[httpx.Request], httpx.Response]

SECRET_KEY = "sk-live-SECRET-api-key-0123456789"
SECRET_TOKEN = "eg1~SECRET-user-token-abcdef"


def sync_transport(client: FortniteAPI) -> SyncTransport:
    transport = client.transport
    assert isinstance(transport, SyncTransport)
    return transport


def async_transport(client: AsyncFortniteAPI) -> AsyncTransport:
    transport = client.transport
    assert isinstance(transport, AsyncTransport)
    return transport


def mock_sync(handler: Handler, api_key: str = "key", **options: Any) -> FortniteAPI:
    """A sync client using the built-in transport, answering every request with ``handler``."""
    client = FortniteAPI(api_key, **options)
    transport = sync_transport(client)
    transport._client.close()
    transport._client = httpx.Client(transport=httpx.MockTransport(handler))
    return client


def mock_async(handler: Handler, api_key: str = "key", **options: Any) -> AsyncFortniteAPI:
    """An async client using the built-in transport, answering every request with ``handler``."""
    client = AsyncFortniteAPI(api_key, **options)
    transport = async_transport(client)
    # Never used for I/O yet, so dropping it without closing leaks nothing.
    transport._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return client
