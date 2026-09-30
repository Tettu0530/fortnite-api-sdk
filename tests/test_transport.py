"""Tests for the built-in httpx transports: requests, error mapping, redirects and settings."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import httpx
import pydantic
import pytest

import fortnite_api
from fortnite_api import (
    APIConnectionError,
    APITimeoutError,
    AsyncFortniteAPI,
    AsyncTransport,
    AuthError,
    ClientError,
    DecodeError,
    FortniteAPI,
    FortniteAPIError,
    NotFoundError,
    PlanRequiredError,
    RateLimitError,
    RedirectError,
    RetryConfig,
    ServerError,
    SyncTransport,
    UnsuccessfulResponseError,
    ValidationError,
)
from fortnite_api.models import BattlePassCatalog, CashPrizeScoringDto, InitiateRequest
from tests.helpers import Handler, mock_async, mock_sync, sync_transport

# --- requests ---------------------------------------------------------------------------------


def test_sync_typed_response_and_model_body() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content) if request.content else None
        if request.url.path.endswith("/battlepass"):
            return httpx.Response(200, json={"season": 3})
        return httpx.Response(200, json={"ok": True})

    client = mock_sync(handler)
    assert isinstance(client.battlepass.get(season=3), BattlePassCatalog)
    assert seen["url"].endswith("/api/v2/battlepass?season=3")
    client.custom_match.initiate(InitiateRequest(custom_key="abc", players_id=["p1"]))
    assert seen["body"] == {"custom_key": "abc", "players_id": ["p1"]}
    client.custom_match.initiate({"custom_key": "raw"})
    assert seen["body"] == {"custom_key": "raw"}
    client.close()


def test_default_and_custom_user_agent() -> None:
    agents: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        agents.append(request.headers["user-agent"])
        return httpx.Response(200, json={})

    client = mock_sync(handler)
    client.health()
    client.close()
    custom = mock_sync(handler, user_agent="BotShade/1.0")
    custom.health()
    custom.close()
    assert agents[0] == f"fortnite-api-sdk/{fortnite_api.__version__} python-httpx/{httpx.__version__}"
    assert agents[0].startswith("fortnite-api-sdk/0.3.0 ")
    assert agents[1] == "BotShade/1.0"


def test_headers_and_token_precedence() -> None:
    seen: list[httpx.Headers] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers)
        return httpx.Response(200, json={})

    client = mock_sync(handler, fortnite_token="default")
    client.weapons.get_lootpool()
    client.weapons.get_lootpool(fortnite_token="override")
    client.close()
    assert seen[0]["x-api-key"] == "key"
    assert seen[0]["x-fortnite-token"] == "default"
    assert seen[1]["x-fortnite-token"] == "override"


def test_path_parameters_are_encoded_as_one_segment() -> None:
    raw: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raw.append(request.url.raw_path)
        return httpx.Response(200, json={})

    client = mock_sync(handler)
    client.account.get_by_display_name("a/b?c#d")
    client.account.get_by_display_name("..")
    client.custom_match.delete_account(42)
    client.close()
    assert raw[0] == b"/api/v1/account/displayName/a%2Fb%3Fc%23d"
    assert raw[1] == b"/api/v1/account/displayName/%2E%2E"
    assert raw[2] == b"/api/v1/custom-match/accounts/42"


async def test_async_path_parameters_are_encoded() -> None:
    raw: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        raw.append(request.url.raw_path)
        return httpx.Response(200, json={})

    client = mock_async(handler)
    await client.account.get_by_display_name("x y/z")
    await client.close()
    assert raw == [b"/api/v1/account/displayName/x%20y%2Fz"]


def test_empty_path_parameter_is_rejected() -> None:
    client = mock_sync(lambda _r: httpx.Response(200, json={}))
    with pytest.raises(ValueError, match="must not be empty"):
        client.account.get_by_id("")
    client.close()


def test_deprecated_endpoint_warns() -> None:
    client = mock_sync(lambda _r: httpx.Response(200, json={}))
    with pytest.warns(DeprecationWarning, match="battlepass.get"):
        client.battlepass.get_legacy()
    client.close()


async def test_async_parity_typed_and_deprecated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cashprizes"):
            return httpx.Response(200, json={"w": [{"scoringType": "x"}]})
        return httpx.Response(200, json={})

    client = mock_async(handler)
    prizes = await client.tournaments.get_cashprizes()
    assert isinstance(prizes["w"][0], CashPrizeScoringDto)
    with pytest.warns(DeprecationWarning, match="parse_broadcast"):
        await client.replays.parse_broadcast("match")
    await client.close()


def test_removed_and_moved_methods() -> None:
    client = FortniteAPI("key")
    assert not hasattr(client.tournaments, "get_tracker_debug")
    assert not hasattr(client.tournaments, "get_power_rankings")
    assert hasattr(client.power_rankings, "get_from_archive")
    assert hasattr(client, "health_version")
    client.close()


# --- error mapping ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("response", "cls", "message"),
    [
        (httpx.Response(400, json={"title": "Bad Request", "status": 400}), ClientError, "Bad Request"),
        (httpx.Response(401, json={"error": "Invalid key"}), AuthError, "Invalid key"),
        (httpx.Response(403, json={"error": "Upgrade your plan"}), PlanRequiredError, "Upgrade your plan"),
        (httpx.Response(404, json={"detail": "Nope"}), NotFoundError, "Nope"),
        (httpx.Response(413, json={"message": "too big"}), ClientError, "too big"),
        (httpx.Response(429, json={"error": "slow down"}), RateLimitError, "slow down"),
        (httpx.Response(500, json=["unexpected"]), ServerError, "Request failed with status 500"),
        (httpx.Response(502, text="<html>gateway</html>"), ServerError, "Request failed"),
    ],
)
def test_error_classes(response: httpx.Response, cls: type[FortniteAPIError], message: str) -> None:
    client = mock_sync(lambda _request: response)
    with pytest.raises(cls) as info:
        client.shop.get_current()
    assert type(info.value) is cls
    assert info.value.status == response.status_code
    assert info.value.message == message
    assert str(info.value) == f"[{response.status_code}] {message}"
    assert repr(info.value) == f"{cls.__name__}(status={response.status_code}, message={message!r})"
    client.close()


def test_rate_limit_retry_after_header() -> None:
    client = mock_sync(lambda _r: httpx.Response(429, headers={"Retry-After": "12"}, json={"error": "quota"}))
    with pytest.raises(RateLimitError) as info:
        client.shop.get_current()
    assert info.value.retry_after == 12.0
    client.close()


def test_success_false_envelope_keeps_real_status() -> None:
    envelope = {"success": False, "error": "quota exceeded"}
    client = mock_sync(lambda _request: httpx.Response(200, json=envelope))
    with pytest.raises(UnsuccessfulResponseError, match="quota exceeded") as info:
        client.health()
    assert info.value.status == 200
    assert info.value.data == envelope
    client.close()


def test_success_false_with_error_status_uses_status_class() -> None:
    client = mock_sync(lambda _r: httpx.Response(429, json={"success": False, "error": "limit"}))
    with pytest.raises(RateLimitError) as info:
        client.health()
    assert info.value.data == {"success": False, "error": "limit"}
    client.close()


def test_non_json_success_body_raises_decode_error() -> None:
    client = mock_sync(lambda _r: httpx.Response(200, text="<html>maintenance</html>"))
    with pytest.raises(DecodeError) as info:
        client.shop.get_current()
    assert info.value.status == 200
    assert info.value.data == "<html>maintenance</html>"
    assert isinstance(info.value.__cause__, json.JSONDecodeError)
    client.close()


def test_empty_success_body_is_none() -> None:
    client = mock_sync(lambda _r: httpx.Response(204))
    assert client.sprites.unpublish_collection() is None
    client.close()


def test_invalid_model_raises_validation_error() -> None:
    client = mock_sync(lambda _r: httpx.Response(200, json={"chapter": "not-a-number"}))
    with pytest.raises(ValidationError) as info:
        client.map.get()
    err = info.value
    assert isinstance(err.validation_error, pydantic.ValidationError)
    assert err.__cause__ is err.validation_error
    assert err.status == 200
    assert err.data == {"chapter": "not-a-number"}
    assert "MapDataDto" in err.message
    client.close()


def test_connection_error_is_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = mock_sync(handler)
    with pytest.raises(APIConnectionError) as info:
        client.shop.get_current()
    assert type(info.value) is APIConnectionError
    assert info.value.status == 0
    assert isinstance(info.value.__cause__, httpx.ConnectError)
    assert info.value.message == "Connection failed (ConnectError)"  # never the httpx text
    assert "connection refused" in str(info.value.__cause__)
    client.close()


async def test_async_timeout_is_wrapped() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    client = mock_async(handler)
    with pytest.raises(APITimeoutError) as info:
        await client.shop.get_current()
    assert isinstance(info.value, APIConnectionError)
    assert info.value.status == 0
    assert isinstance(info.value.__cause__, httpx.ReadTimeout)
    await client.close()


def test_exceptions_exported_from_package_and_errors_module() -> None:
    from fortnite_api import errors  # noqa: PLC0415

    for name in errors.__all__:
        assert getattr(fortnite_api, name) is getattr(errors, name)
        assert name in fortnite_api.__all__
    assert fortnite_api.NETWORK_ERROR_STATUS == 0
    assert fortnite_api.protocol.SyncTransportProtocol is fortnite_api.SyncTransportProtocol
    assert "protocol" in fortnite_api.__all__
    assert issubclass(fortnite_api.AuthError, fortnite_api.ClientError)
    assert issubclass(fortnite_api.ClientError, fortnite_api.FortniteAPIError)


# --- redirects --------------------------------------------------------------------------------


def test_redirect_is_not_followed_by_default() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(302, headers={"location": "https://evil.example/steal"})

    client = mock_sync(handler)
    with pytest.raises(RedirectError) as info:
        client.shop.get_current()
    assert info.value.status == 302
    assert info.value.location == "https://evil.example/steal"
    assert len(requests) == 1
    client.close()


def _redirecting(target: str, status: int = 302) -> tuple[Handler, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(status, headers={"location": target})
        return httpx.Response(200, json={"ok": True})

    return handler, requests


def test_follow_same_origin_keeps_credentials() -> None:
    handler, requests = _redirecting("/api/v1/moved?x=1")
    client = mock_sync(handler, follow_redirects=True, fortnite_token="tok")
    assert client.account.get_bulk(["a"]) == {"ok": True}
    client.close()
    assert str(requests[1].url) == "https://prod.api-fortnite.com/api/v1/moved?x=1"
    assert requests[1].headers["x-api-key"] == "key"
    assert requests[1].headers["x-fortnite-token"] == "tok"


@pytest.mark.parametrize(
    "target",
    [
        "https://evil.example/steal",
        "http://prod.api-fortnite.com/api/v1/shop",  # scheme downgrade
        "https://prod.api-fortnite.com:8443/api/v1/shop",  # other port
    ],
)
def test_follow_cross_origin_strips_credentials(target: str) -> None:
    handler, requests = _redirecting(target)
    client = mock_sync(handler, follow_redirects=True, fortnite_token="tok")
    client.shop.get_current()
    client.close()
    assert str(requests[1].url).startswith(target)
    assert "x-api-key" not in requests[1].headers
    assert "x-fortnite-token" not in requests[1].headers
    assert requests[1].headers["user-agent"].startswith("fortnite-api-sdk/")


async def test_async_follow_cross_origin_strips_credentials() -> None:
    handler, requests = _redirecting("https://cdn.example/x.json")
    client = mock_async(handler, follow_redirects=True)
    assert await client.weapons.get_lootpool() == {"ok": True}
    await client.close()
    assert "x-api-key" not in requests[1].headers


@pytest.mark.parametrize(
    ("status", "method", "has_body"), [(303, "GET", False), (302, "GET", False), (307, "POST", True)]
)
def test_follow_method_and_body_rules(status: int, method: str, has_body: bool) -> None:
    handler, requests = _redirecting("/api/v1/elsewhere", status)
    client = mock_sync(handler, follow_redirects=True)
    client.custom_match.initiate({"custom_key": "k"})
    client.close()
    assert requests[1].method == method
    assert (json.loads(requests[1].content) if has_body else requests[1].content) == (
        {"custom_key": "k"} if has_body else b""
    )
    assert ("content-type" in requests[1].headers) is has_body


def test_follow_get_keeps_method_on_303() -> None:
    handler, requests = _redirecting("/api/v1/elsewhere", 301)
    client = mock_sync(handler, follow_redirects=True)
    client.shop.get_current()
    client.close()
    assert requests[1].method == "GET"


def test_follow_redirect_hop_limit() -> None:
    count = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal count
        count += 1
        return httpx.Response(302, headers={"location": f"/api/v1/hop{count}"})

    client = mock_sync(handler, follow_redirects=True, max_redirects=2)
    with pytest.raises(RedirectError, match="maximum of 2 redirects") as info:
        client.shop.get_current()
    assert count == 3
    assert info.value.location == "/api/v1/hop3"
    client.close()


async def test_async_follow_redirect_hop_limit() -> None:
    client = mock_async(
        lambda _r: httpx.Response(307, headers={"location": "/loop"}), follow_redirects=True, max_redirects=0
    )
    with pytest.raises(RedirectError):
        await client.shop.get_current()
    await client.close()


def test_map_image_never_follows_even_when_enabled() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(302, headers={"location": "https://img.example/a.png"})

    client = mock_sync(handler, follow_redirects=True)
    assert client.map.get_image() == "https://img.example/a.png"
    assert len(requests) == 1
    client.close()


# --- binary / redirect endpoint / multipart ----------------------------------------------------


def test_binary_download_and_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/missing"):
            return httpx.Response(404, json={"error": "no replay"})
        assert "Content-Type" not in request.headers
        return httpx.Response(200, content=b"\x00REPLAY")

    client = mock_sync(handler)
    assert client.replays.download("m1") == b"\x00REPLAY"
    with pytest.raises(NotFoundError, match="no replay"):
        client.replays.download("missing")
    client.close()


def test_redirect_endpoint_success_and_error() -> None:
    responses = iter([httpx.Response(200, json={}), httpx.Response(500, json={"error": "boom"})])
    client = mock_sync(lambda _request: next(responses))
    assert client.map.get_image(version="1.0") == "https://prod.api-fortnite.com/api/v1/map/image?version=1.0"
    with pytest.raises(ServerError, match="boom"):
        client.map.get_image()
    client.close()


def test_multipart_inputs(tmp_path: Path) -> None:
    seen: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.read())
        assert request.headers["content-type"].startswith("multipart/form-data")
        return httpx.Response(200, json={"success": True, "data": {"ok": True}})

    replay = tmp_path / "match.replay"
    replay.write_bytes(b"FROM-PATH")
    handle = io.BytesIO(b"FROM-HANDLE")
    handle.name = "handle.replay"

    client = mock_sync(handler)
    assert client.parsing.parse_replay(str(replay)) == {"ok": True}
    assert client.parsing.parse_stats(bytearray(b"RAW"), filename="custom.replay") == {"ok": True}
    assert client.parsing.parse_map(handle) == {"ok": True}
    assert client.parsing.parse_multiple([b"A", b"B"], filenames=["a.replay", "b.replay"]) == {"ok": True}
    client.close()

    assert b'filename="match.replay"' in seen[0]
    assert b"FROM-PATH" in seen[0]
    assert b'filename="custom.replay"' in seen[1]
    assert b'filename="handle.replay"' in seen[2]
    assert seen[3].count(b'name="files"') == 2


def test_multipart_error() -> None:
    client = mock_sync(lambda _request: httpx.Response(413, json={"error": "too large"}))
    with pytest.raises(ClientError, match="too large"):
        client.parsing.parse_replay(b"x")
    client.close()


def test_transport_multipart_without_unwrap() -> None:
    client = mock_sync(lambda _request: httpx.Response(200, json={"success": True, "data": 1}))
    transport = sync_transport(client)
    raw = transport.request_multipart("/parsing", {"file": ("a", b"x", "application/octet-stream")}, unwrap=False)
    assert raw == {"success": True, "data": 1}
    client.close()


async def test_async_error_binary_redirect_multipart() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/map/image"):
            return httpx.Response(302, headers={"location": "https://img/a.png"})
        if path.startswith("/api/v1/replays/"):
            return httpx.Response(200, content=b"BIN")
        if path.startswith("/api/v1/parsing"):
            return httpx.Response(200, json={"parsed": True})
        return httpx.Response(403, json={"error": "forbidden"})

    client = mock_async(handler)
    assert await client.map.get_image() == "https://img/a.png"
    assert await client.replays.download("m") == b"BIN"
    assert await client.parsing.parse_replay(b"x") == {"parsed": True}
    with pytest.raises(PlanRequiredError, match="forbidden"):
        await client.shop.get_current()
    await client.close()


# --- construction / lifecycle -----------------------------------------------------------------


def test_api_key_required() -> None:
    with pytest.raises(ValueError, match="api_key is required"):
        FortniteAPI()
    with pytest.raises(ValueError, match="api_key is required"):
        AsyncFortniteAPI("")
    with pytest.raises(ValueError, match="api_key is required"):
        SyncTransport("")


def test_transport_excludes_built_in_options() -> None:
    transport = SyncTransport("key")
    with pytest.raises(ValueError, match="configure api_key on the transport"):
        FortniteAPI("key", transport=transport)
    with pytest.raises(ValueError, match="configure retry, timeout on the transport"):
        FortniteAPI(transport=transport, timeout=1.0, retry=RetryConfig())
    transport.close()


def test_built_in_options_are_applied() -> None:
    retry = RetryConfig(max_retries=1)
    client = FortniteAPI(
        "key",
        base_url="https://example.test/custom/",
        timeout=3.0,
        retry=retry,
        follow_redirects=True,
        max_redirects=1,
        user_agent="ua",
    )
    transport = sync_transport(client)
    assert transport.base_url == "https://example.test/custom"
    assert transport.timeout == 3.0
    assert transport.retry is retry
    assert transport.follow_redirects is True
    assert transport.max_redirects == 1
    assert transport.user_agent == "ua"
    assert transport._url("/shop", "v1") == "https://example.test/custom/v1/shop"
    assert transport._url("/health", None) == "https://example.test/custom/health"
    client.close()


def test_client_does_not_close_injected_transport() -> None:
    transport = SyncTransport("key")
    with FortniteAPI(transport=transport) as client:
        assert client.transport is transport
    assert not transport._client.is_closed
    with transport as entered:
        assert entered is transport
    assert transport._client.is_closed


async def test_async_client_does_not_close_injected_transport() -> None:
    transport = AsyncTransport("key")
    async with AsyncFortniteAPI(transport=transport) as client:
        assert client.transport is transport
    assert not transport._client.is_closed
    async with transport as entered:
        assert entered is transport
    assert transport._client.is_closed


async def test_async_context_manager_and_health() -> None:
    client = mock_async(lambda _request: httpx.Response(200, json={"status": "ok"}))
    async with client as entered:
        assert entered is client
        assert await client.health() == {"status": "ok"}


def test_sync_context_manager() -> None:
    client = mock_sync(lambda _request: httpx.Response(200, json={"status": "ok"}))
    with client as entered:
        assert entered is client
        assert client.health() == {"status": "ok"}


def test_client_and_transport_repr() -> None:
    client = FortniteAPI("key", fortnite_token="tok")
    text = repr(client)
    assert text.startswith("FortniteAPI(transport=SyncTransport(base_url='https://prod.api-fortnite.com/api'")
    assert "api_key='***'" in text
    assert "fortnite_token='***'" in text
    client.close()
    assert "fortnite_token=None" in repr(SyncTransport("key"))
