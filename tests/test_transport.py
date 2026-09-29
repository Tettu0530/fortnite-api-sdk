from __future__ import annotations

import io
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

from fortnite_api import AsyncFortniteAPI, FortniteAPI
from fortnite_api._transport import _BaseTransport
from fortnite_api.errors import FortniteAPIError
from fortnite_api.models import (
    BattlePassCatalog,
    CashPrizeScoringDto,
    InitiateRequest,
    PublishCollectionRequest,
    WeaponListItemDto,
)


def make() -> _BaseTransport:
    return _BaseTransport("key", "https://prod.api-fortnite.com/api")


def test_url_versioned_and_root():
    t = make()
    assert t._url("/shop", "v1") == "https://prod.api-fortnite.com/api/v1/shop"
    assert t._url("/cosmetics/all", "v2") == "https://prod.api-fortnite.com/api/v2/cosmetics/all"
    assert t._url("/health", None) == "https://prod.api-fortnite.com/health"


def test_headers_and_token_precedence():
    t = _BaseTransport("key", fortnite_token="default")
    assert t._headers(None)["x-api-key"] == "key"
    assert t._headers(None)["x-fortnite-token"] == "default"
    assert t._headers("override")["x-fortnite-token"] == "override"
    assert "x-fortnite-token" not in _BaseTransport("key")._headers(None)


def test_clean_drops_none():
    assert make()._clean({"a": 1, "b": None}) == {"a": 1}
    assert make()._clean({"a": None}) is None
    assert make()._clean(None) is None


def test_unwrap_status_data_envelope():
    t = make()
    assert t._unwrap({"status": 200, "data": [1, 2]}) == [1, 2]
    assert t._unwrap({"status": "ok", "date": "x"}) == {"status": "ok", "date": "x"}
    assert t._unwrap({"storefronts": []}) == {"storefronts": []}


def test_unwrap_success_envelope():
    t = make()
    assert t._unwrap({"success": True, "data": {"x": 1}}) == {"x": 1}
    with pytest.raises(FortniteAPIError):
        t._unwrap({"success": False, "error": "nope"})


def test_parse_extracts_single_list_for_list_results():
    t = make()
    payload = {"status": 200, "current": "40.10", "patches": [{"patch": "40.10"}]}
    result = t._parse(payload, list[WeaponListItemDto])
    assert len(result) == 1
    assert isinstance(result[0], WeaponListItemDto)


def test_api_key_required():
    with pytest.raises(ValueError, match="api_key is required"):
        _BaseTransport("")


def test_parse_none_returns_raw():
    assert make()._parse({"a": 1}, None) == {"a": 1}


def test_parse_dict_of_model_lists():
    payload = {"w1": [{"scoringType": "value", "ranks": []}], "w2": []}
    result = make()._parse(payload, dict[str, list[CashPrizeScoringDto]])
    assert isinstance(result["w1"][0], CashPrizeScoringDto)
    assert result["w1"][0].scoring_type == "value"
    assert result["w2"] == []


def test_body_serializes_models_by_alias_without_none():
    body = PublishCollectionRequest(auto_refresh=True)
    assert _BaseTransport._body(body) == {"autoRefresh": True}
    assert _BaseTransport._body({"raw": None}) == {"raw": None}
    assert _BaseTransport._body(["a", "b"]) == ["a", "b"]
    assert _BaseTransport._body(None) is None


def _mock(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
    return httpx.MockTransport(handler)


def test_sync_typed_response_and_model_body():
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content) if request.content else None
        if request.url.path.endswith("/battlepass"):
            return httpx.Response(200, json={"season": 3})
        return httpx.Response(200, json={"ok": True})

    client = FortniteAPI("key")
    client._t._client = httpx.Client(transport=_mock(handler))
    assert isinstance(client.battlepass.get(season=3), BattlePassCatalog)
    assert seen["url"].endswith("/api/v2/battlepass?season=3")
    client.custom_match.initiate(InitiateRequest(custom_key="abc", players_id=["p1"]))
    assert seen["body"] == {"custom_key": "abc", "players_id": ["p1"]}
    client.custom_match.initiate({"custom_key": "raw"})
    assert seen["body"] == {"custom_key": "raw"}
    client.close()


def test_deprecated_endpoint_warns():
    client = FortniteAPI("key")
    client._t._client = httpx.Client(transport=_mock(lambda r: httpx.Response(200, json={})))
    with pytest.warns(DeprecationWarning, match="battlepass.get"):
        client.battlepass.get_legacy()
    client.close()


async def test_async_parity_typed_and_deprecated():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/cashprizes"):
            return httpx.Response(200, json={"w": [{"scoringType": "x"}]})
        return httpx.Response(200, json={})

    client = AsyncFortniteAPI("key")
    client._t._client = httpx.AsyncClient(transport=_mock(handler))
    prizes = await client.tournaments.get_cashprizes()
    assert isinstance(prizes["w"][0], CashPrizeScoringDto)
    with pytest.warns(DeprecationWarning, match="parse_broadcast"):
        await client.replays.parse_broadcast("match")
    await client.close()


def test_removed_and_moved_methods():
    client = FortniteAPI("key")
    assert not hasattr(client.tournaments, "get_tracker_debug")
    assert not hasattr(client.tournaments, "get_power_rankings")
    assert hasattr(client.power_rankings, "get_from_archive")
    assert hasattr(client, "health_version")
    client.close()


# --- error handling and non-JSON transports ---------------------------------------------------


def _sync(handler: Callable[[httpx.Request], httpx.Response]) -> FortniteAPI:
    client = FortniteAPI("key")
    client._t._client.close()
    client._t._client = httpx.Client(transport=_mock(handler))
    return client


async def _async(handler: Callable[[httpx.Request], httpx.Response]) -> AsyncFortniteAPI:
    client = AsyncFortniteAPI("key")
    await client._t._client.aclose()
    client._t._client = httpx.AsyncClient(transport=_mock(handler))
    return client


@pytest.mark.parametrize(
    ("response", "message"),
    [
        (httpx.Response(401, json={"error": "Invalid key"}), "Invalid key"),
        (httpx.Response(400, json={"title": "Bad Request", "status": 400}), "Bad Request"),
        (httpx.Response(404, json={"detail": "Nope"}), "Nope"),
        (httpx.Response(500, json=["unexpected"]), "Request failed with status 500"),
        (httpx.Response(502, text="<html>gateway</html>"), "Request failed"),
    ],
)
def test_error_messages(response: httpx.Response, message: str) -> None:
    client = _sync(lambda _request: response)
    with pytest.raises(FortniteAPIError) as info:
        client.shop.get_current()
    assert info.value.status == response.status_code
    assert info.value.message == message
    assert str(info.value) == f"[{response.status_code}] {message}"
    client.close()


def test_success_false_envelope_raises() -> None:
    client = _sync(lambda _request: httpx.Response(200, json={"success": False, "error": "quota exceeded"}))
    with pytest.raises(FortniteAPIError, match="quota exceeded") as info:
        client.health()
    assert info.value.status == 422
    client.close()


def test_success_results_envelope_unwrapped() -> None:
    assert make()._unwrap({"success": True, "results": [1]}) == [1]
    assert make()._unwrap({"success": True, "other": 1}) == {"success": True, "other": 1}


def test_base_url_without_api_suffix() -> None:
    t = _BaseTransport("key", "https://example.test/custom/")
    assert t._url("/shop", "v1") == "https://example.test/custom/v1/shop"
    assert t._url("/health", None) == "https://example.test/custom/health"


def test_binary_download_and_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/missing"):
            return httpx.Response(404, json={"error": "no replay"})
        assert "Content-Type" not in request.headers
        return httpx.Response(200, content=b"\x00REPLAY")

    client = _sync(handler)
    assert client.replays.download("m1") == b"\x00REPLAY"
    with pytest.raises(FortniteAPIError, match="no replay"):
        client.replays.download("missing")
    client.close()


def test_redirect_success_and_error() -> None:
    responses = iter(
        [
            httpx.Response(200, json={}),
            httpx.Response(500, json={"error": "boom"}),
        ]
    )
    client = _sync(lambda _request: next(responses))
    assert client.map.get_image(version="1.0") == "https://prod.api-fortnite.com/api/v1/map/image?version=1.0"
    with pytest.raises(FortniteAPIError, match="boom"):
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

    client = _sync(handler)
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
    client = _sync(lambda _request: httpx.Response(413, json={"error": "too large"}))
    with pytest.raises(FortniteAPIError, match="too large"):
        client.parsing.parse_replay(b"x")
    client.close()


def test_transport_multipart_without_unwrap() -> None:
    client = _sync(lambda _request: httpx.Response(200, json={"success": True, "data": 1}))
    raw = client._t.request_multipart("/parsing", {"file": ("a", b"x", "application/octet-stream")}, unwrap=False)
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

    client = await _async(handler)
    assert await client.map.get_image() == "https://img/a.png"
    assert await client.replays.download("m") == b"BIN"
    assert await client.parsing.parse_replay(b"x") == {"parsed": True}
    with pytest.raises(FortniteAPIError, match="forbidden"):
        await client.shop.get_current()
    await client.close()


async def test_async_context_manager_and_health() -> None:
    client = await _async(lambda _request: httpx.Response(200, json={"status": "ok"}))
    async with client as entered:
        assert entered is client
        assert await client.health() == {"status": "ok"}


def test_sync_context_manager() -> None:
    client = _sync(lambda _request: httpx.Response(200, json={"status": "ok"}))
    with client as entered:
        assert entered is client
        assert client.health() == {"status": "ok"}
