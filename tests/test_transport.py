from __future__ import annotations

import json

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
    with pytest.raises(ValueError):
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


def _mock(handler):
    return httpx.MockTransport(handler)


def test_sync_typed_response_and_model_body():
    seen = {}

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
    with pytest.warns(DeprecationWarning):
        await client.replays.parse_broadcast("match")
    await client.close()


def test_removed_and_moved_methods():
    client = FortniteAPI("key")
    assert not hasattr(client.tournaments, "get_tracker_debug")
    assert not hasattr(client.tournaments, "get_power_rankings")
    assert hasattr(client.power_rankings, "get_from_archive")
    assert hasattr(client, "health_version")
    client.close()
