"""Custom transports: the generated resources only rely on the public transport protocol."""

from __future__ import annotations

import contextlib
import functools
import inspect
import json
import warnings
from collections.abc import Mapping
from typing import Any

import httpx
import pytest

from examples.custom_transport import EndpointNotAllowedError, MyAsyncTransport, main
from fortnite_api import (
    APIConnectionError,
    APITimeoutError,
    AsyncFortniteAPI,
    AsyncTransport,
    AsyncTransportProtocol,
    FortniteAPI,
    NotFoundError,
    RedirectError,
    SyncTransport,
    SyncTransportProtocol,
    UnsuccessfulResponseError,
    interpret,
)
from fortnite_api.interpret import MultipartFiles
from fortnite_api.models import MapDataDto, WeaponListItemDto
from scripts.check_spec_coverage import call_args, public_methods


class InMemorySyncTransport:
    """A sync transport without any HTTP library: canned (status, headers, body) per path."""

    def __init__(self, routes: Mapping[str, tuple[int, dict[str, str], bytes]] | None = None) -> None:
        self.routes = dict(routes or {})
        self.sent: list[dict[str, Any]] = []

    def _answer(self, **sent: Any) -> tuple[int, dict[str, str], bytes]:
        self.sent.append(sent)
        return self.routes.get(sent["path"], (200, {}, b"{}"))

    def request(
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
        status, headers, body = self._answer(
            method=method,
            path=path,
            url=interpret.build_url("https://api.test/api", path, version),
            params=interpret.clean_params(params),
            body=interpret.serialize_body(json_body),
            retryable=retryable,
        )
        return interpret.interpret_json(status, headers, body, response_type)

    def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        status, headers, body = self._answer(method="GET", path=path, retryable=True)
        return interpret.interpret_binary(status, headers, body)

    def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        status, headers, body = self._answer(method="GET", path=path, retryable=True)
        return interpret.interpret_redirect(
            status, headers, body, interpret.build_url("https://api.test", path, version)
        )

    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        status, headers, body = self._answer(method="POST", path=path, files=files, retryable=False)
        return interpret.interpret_json(status, headers, body, response_type, unwrap=unwrap)


def _json(data: Any, status: int = 200, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
    return status, headers or {}, json.dumps(data).encode()


# --- protocol conformance ---------------------------------------------------------------------


def test_protocols_are_runtime_checkable() -> None:
    sync_builtin = SyncTransport("key")
    assert isinstance(sync_builtin, SyncTransportProtocol)
    assert isinstance(AsyncTransport("key"), AsyncTransportProtocol)
    assert isinstance(InMemorySyncTransport(), SyncTransportProtocol)
    assert isinstance(MyAsyncTransport("k", http=httpx.AsyncClient()), AsyncTransportProtocol)
    assert not isinstance(object(), SyncTransportProtocol)
    sync_builtin.close()


def test_protocol_signatures_match_builtin_transports() -> None:
    for proto, impl in ((SyncTransportProtocol, SyncTransport), (AsyncTransportProtocol, AsyncTransport)):
        for name in ("request", "request_binary", "request_redirect", "request_multipart"):
            assert inspect.signature(getattr(proto, name)) == inspect.signature(getattr(impl, name)), name


# --- sync custom transport end to end ---------------------------------------------------------


def test_sync_custom_transport_end_to_end() -> None:
    transport = InMemorySyncTransport(
        {
            "/weapons": _json({"status": 200, "data": [{"id": "WID_A", "displayName": "AR"}]}),
            "/map": _json({"chapter": 6, "imageUrl": "https://x/y.png"}),
            "/account/missing": _json({"error": "no such account"}, 404),
            "/replays/m%2F1": (200, {}, b"\x00BIN"),
            "/map/image": (302, {"Location": "https://img/x.png"}, b""),
            "/parsing": _json({"success": False, "error": "quota"}),
        }
    )
    client = FortniteAPI(transport=transport)
    weapons = client.weapons.get(major=1)
    assert isinstance(weapons[0], WeaponListItemDto)
    assert weapons[0].display_name == "AR"
    assert isinstance(client.map.get(), MapDataDto)
    with pytest.raises(NotFoundError, match="no such account"):
        client.account.get_by_id("missing")
    assert client.replays.download("m/1") == b"\x00BIN"
    assert client.map.get_image() == "https://img/x.png"
    with pytest.raises(UnsuccessfulResponseError) as info:
        client.parsing.parse_replay(b"data", filename="a.replay")
    assert info.value.status == 200
    client.stats.get_bulk({"accountIds": ["a"], "stats": ["s"]})
    client.close()  # a no-op for injected transports
    assert transport.sent[0]["params"] == {"major": 1}
    assert transport.sent[0]["url"] == "https://api.test/api/v2/weapons"
    assert transport.sent[-2]["files"] == {"file": ("a.replay", b"data", "application/octet-stream")}
    assert transport.sent[-1] == {
        "method": "POST",
        "path": "/stats/bulk",
        "url": "https://api.test/api/v2/stats/bulk",
        "params": None,
        "body": {"accountIds": ["a"], "stats": ["s"]},
        "retryable": True,
    }
    assert repr(client).startswith("FortniteAPI(transport=<")


def test_generated_retryable_classification() -> None:
    """GETs (except the costly ones) and exactly the read-only bulk POST lookups are retryable."""
    transport = InMemorySyncTransport()
    client = FortniteAPI(transport=transport)
    for _name, method in public_methods(client):
        args, kwargs = call_args(inspect.signature(method))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            with contextlib.suppress(Exception):  # canned {} bodies may fail model validation
                method(*args, **kwargs)
    client.health()
    retryable_non_get = {(s["method"], s["path"]) for s in transport.sent if s["retryable"] and s["method"] != "GET"}
    assert retryable_non_get == {
        ("POST", "/account/external/displayNames/bulk"),
        ("POST", "/account/external/ids/bulk"),
        ("POST", "/profile/leaderboard/P_game_id"),
        ("POST", "/profile/trackprogress/bulk"),
        ("POST", "/stats/bulk"),
    }
    non_retryable_get = {s["path"] for s in transport.sent if not s["retryable"] and s["method"] == "GET"}
    # Parsing a replay consumes credits and get-token starts a new device-code flow.
    assert non_retryable_get == {
        "/oauth/get-token",
        "/replays/P_match_id/parse",
        "/replays/P_match_id/parse/broadcast",
        "/replays/P_match_id/parse/lobby",
        "/replays/P_match_id/parse/loot",
        "/replays/P_match_id/parse/map",
        "/replays/P_match_id/parse/stats",
        "/replays/P_match_id/parse/timeline",
        "/replays/P_match_id/parse/tracks",
        "/replays/P_match_id/parse/zones",
    }
    assert len(transport.sent) == 147  # 146 resource methods + health


# --- async custom transport (the example) end to end ------------------------------------------


def _mock_api(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if request.headers.get("x-api-key") != "k":
        return httpx.Response(401, json={"error": "bad key"})
    if path == "/api/v2/weapons":
        return httpx.Response(200, json=[{"id": "WID_A"}])
    if path == "/api/v1/replays/m1":
        return httpx.Response(200, content=b"BIN")
    if path == "/api/v1/map/image":
        return httpx.Response(302, headers={"location": "https://img/a.png"})
    if path == "/api/v1/parsing":
        return httpx.Response(200, json={"success": True, "data": {"parsed": True}})
    if request.url.raw_path == b"/api/v1/account/displayName/a%2Fb":
        return httpx.Response(404, json={"error": "not found"})
    return httpx.Response(200, json={"path": path, "query": dict(request.url.params)})


async def test_async_custom_transport_end_to_end() -> None:
    async with httpx.AsyncClient(transport=httpx.MockTransport(_mock_api)) as http:
        transport = MyAsyncTransport(
            "k", http=http, allowed_prefixes=("/weapons", "/replays", "/map", "/parsing", "/account")
        )
        client = AsyncFortniteAPI(transport=transport)
        weapons = await client.weapons.get()
        assert isinstance(weapons[0], WeaponListItemDto)
        assert await client.replays.download("m1") == b"BIN"
        assert await client.map.get_image(version="1") == "https://img/a.png"
        assert await client.parsing.parse_replay(b"x") == {"parsed": True}
        with pytest.raises(NotFoundError):
            await client.account.get_by_display_name("a/b")
        with pytest.raises(EndpointNotAllowedError):
            await client.shop.get_current()
        await client.close()
        assert not http.is_closed
    assert transport.calls["/weapons"] == 1
    assert "/shop" not in transport.calls
    assert repr(transport) == "MyAsyncTransport(base_url='https://prod.api-fortnite.com/api', api_key='***')"


async def test_example_main_runs(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("FN_API_KEY", "k")
    monkeypatch.setattr(
        httpx, "AsyncClient", functools.partial(httpx.AsyncClient, transport=httpx.MockTransport(_mock_api))
    )
    await main()
    out = capsys.readouterr().out
    assert "weapons: 1" in out
    assert "blocked: GET /account/some-account is not allowlisted" in out
    assert "calls: {'/weapons': 1}" in out


def test_clients_reject_transports_of_the_wrong_kind() -> None:
    http = httpx.AsyncClient()
    with pytest.raises(TypeError, match=r"FortniteAPI\(transport=\.\.\.\) needs a SyncTransportProtocol"):
        FortniteAPI(transport=MyAsyncTransport("k", http=http))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match=r"AsyncFortniteAPI\(transport=\.\.\.\) needs a AsyncTransportProtocol"):
        AsyncFortniteAPI(transport=InMemorySyncTransport())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="SyncTransportProtocol"):
        FortniteAPI(transport=object())  # type: ignore[arg-type]
    # isinstance() alone cannot tell them apart:
    assert isinstance(InMemorySyncTransport(), AsyncTransportProtocol)


async def test_example_transport_never_follows_redirects_with_the_key() -> None:
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        if request.url.host == "evil.test":
            return httpx.Response(200, json={"stolen": request.headers.get("x-api-key")})
        return httpx.Response(302, headers={"location": "https://evil.test/collect"})

    # The shared client is configured to follow redirects; the example must override it.
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), follow_redirects=True) as http:
        client = AsyncFortniteAPI(transport=MyAsyncTransport("SEKRIT", http=http))
        with pytest.raises(RedirectError) as info:
            await client.weapons.get()
        assert info.value.location == "https://evil.test/collect"
        with pytest.raises(RedirectError):
            await client.replays.download("m1")
        with pytest.raises(RedirectError):
            await client.parsing.parse_replay(b"x")
        assert await client.map.get_image() == "https://evil.test/collect"
    assert [r.url.host for r in sent] == ["prod.api-fortnite.com"] * 4


@pytest.mark.parametrize(
    ("exc", "cls"), [(httpx.ConnectError, APIConnectionError), (httpx.ReadTimeout, APITimeoutError)]
)
async def test_example_transport_wraps_network_errors(exc: type[httpx.TransportError], cls: type[Exception]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise exc(f"failed with {request.headers['x-api-key']}", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        client = AsyncFortniteAPI(transport=MyAsyncTransport("SEKRIT", http=http))
        with pytest.raises(cls) as info:
            await client.weapons.get()
    assert type(info.value) is cls
    assert isinstance(info.value.__cause__, exc)
    assert "SEKRIT" not in str(info.value)
