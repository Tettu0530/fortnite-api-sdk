"""Offline tests for the generated resources (typed models, params, bodies, deprecations)."""

from __future__ import annotations

import inspect
import json
import warnings
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest

from fortnite_api import AsyncFortniteAPI, FortniteAPI
from fortnite_api import resources as res_pkg
from fortnite_api.models import (
    CashPrizeScoringDto,
    LinkAccountRequest,
    MapDataDto,
    NewsNotice,
    PublishCollectionRequest,
    WeaponListItemDto,
)
from fortnite_api.resources._base import Resource
from tests.helpers import mock_async, mock_sync


class Recorder:
    """Records outgoing requests and answers with a canned JSON payload."""

    def __init__(self, payload: Any = None, status: int = 200) -> None:
        self.payload = {} if payload is None else payload
        self.status = status
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(self.status, json=self.payload)

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def query(self) -> dict[str, list[str]]:
        return parse_qs(self.last.url.query.decode())

    def body(self) -> Any:
        return json.loads(self.last.content) if self.last.content else None


@pytest.fixture
def sync_client():
    def make(payload: Any = None) -> tuple[FortniteAPI, Recorder]:
        rec = Recorder(payload)
        client = mock_sync(rec)
        clients.append(client)
        return client, rec

    clients: list[FortniteAPI] = []
    yield make
    for c in clients:
        c.close()


def make_async(payload: Any = None) -> tuple[AsyncFortniteAPI, Recorder]:
    rec = Recorder(payload)
    return mock_async(rec), rec


# --- typed model parsing -------------------------------------------------------------------


def test_single_model_parsing(sync_client):
    client, rec = sync_client({"version": "33.10", "chapter": 6, "imageUrl": "https://x/y.png", "extraField": 1})
    result = client.map.get(version="33.10")
    assert isinstance(result, MapDataDto)
    assert result.image_url == "https://x/y.png"
    assert result.chapter == 6
    # extra="allow" keeps unknown fields available
    assert result.model_extra == {"extraField": 1}
    assert rec.last.url.path == "/api/v1/map"


def test_list_of_models_parsing(sync_client):
    client, _ = sync_client([{"id": "WID_A", "displayName": "AR", "ammoType": "medium"}, {"id": "WID_B"}])
    result = client.weapons.get()
    assert [type(w) for w in result] == [WeaponListItemDto, WeaponListItemDto]
    assert result[0].display_name == "AR"
    assert result[0].ammo_type == "medium"


def test_list_of_models_unwraps_single_list_envelope(sync_client):
    client, _ = sync_client({"status": 200, "notices": [{"title": "Down", "platforms": ["pc"]}]})
    result = client.news.get_notices()
    assert len(result) == 1
    assert isinstance(result[0], NewsNotice)
    assert result[0].platforms == ["pc"]


def test_status_data_envelope_then_typed(sync_client):
    client, _ = sync_client({"status": 200, "data": [{"id": "WID_A"}]})
    result = client.weapons.get()
    assert isinstance(result[0], WeaponListItemDto)


def test_dict_of_model_lists_parsing(sync_client):
    client, rec = sync_client({"w1": [{"scoringType": "value", "ranks": []}], "w2": []})
    result = client.tournaments.get_cashprizes()
    assert set(result) == {"w1", "w2"}
    assert isinstance(result["w1"][0], CashPrizeScoringDto)
    assert result["w1"][0].scoring_type == "value"
    assert result["w2"] == []
    assert rec.last.method == "GET"


def test_untyped_endpoint_returns_raw_json(sync_client):
    client, _ = sync_client({"anything": [1, 2]})
    assert client.weapons.get_lootpool() == {"anything": [1, 2]}


# --- request bodies -----------------------------------------------------------------------


def test_body_as_model_uses_aliases_and_drops_none(sync_client):
    client, rec = sync_client({})
    client.oauth.link(LinkAccountRequest(code="c", redirect_uri="https://r", client_id=None))
    assert rec.last.method == "POST"
    assert rec.body() == {"code": "c", "redirectUri": "https://r"}


def test_body_as_dict_passed_through(sync_client):
    client, rec = sync_client({})
    client.oauth.link({"code": "c", "redirectUri": "https://r", "clientId": None})
    assert rec.body() == {"code": "c", "redirectUri": "https://r", "clientId": None}


def test_optional_body_and_model_populated_by_alias(sync_client):
    client, rec = sync_client({})
    client.sprites.publish_collection()
    assert rec.last.method == "POST"
    assert rec.last.content == b""
    client.sprites.publish_collection(body=PublishCollectionRequest(autoRefresh=False, visibility="public"))
    assert rec.body() == {"visibility": "public", "autoRefresh": False}


def test_list_body(sync_client):
    client, rec = sync_client({})
    client.profile.bulk_track_progress(["a", "b"])
    assert rec.body() == ["a", "b"]


# --- query params ---------------------------------------------------------------------------


def test_weapons_major_minor_params(sync_client):
    client, rec = sync_client([])
    client.weapons.get(major=33, minor=10, ammo_type="light", secondary=True)
    q = rec.query()
    assert q["major"] == ["33"]
    assert q["minor"] == ["10"]
    assert q["ammoType"] == ["light"]
    assert q["secondary"] == ["true"]
    assert "patch" not in q  # None values are dropped


def test_map_mode_param(sync_client):
    client, rec = sync_client({})
    client.map.get(mode="reload")
    assert rec.query() == {"mode": ["reload"]}


def test_map_image_mode_param_redirect():
    rec = Recorder()

    def handler(request: httpx.Request) -> httpx.Response:
        rec.requests.append(request)
        return httpx.Response(302, headers={"location": "https://img/x.png"})

    client = mock_sync(handler)
    assert client.map.get_image(mode="br", version="33.10") == "https://img/x.png"
    assert rec.query() == {"mode": ["br"], "version": ["33.10"]}
    client.close()


@pytest.mark.parametrize("method", ["get_all", "get_br", "get_stw", "get_creative", "get_festival"])
def test_news_platform_param(sync_client, method):
    client, rec = sync_client({})
    getattr(client.news, method)(platform="windows", lang="en")
    assert rec.query() == {"platform": ["windows"], "lang": ["en"]}


def test_csv_query_param(sync_client):
    client, rec = sync_client({})
    client.account.get_display_names(["id1", "id2"])
    assert rec.query() == {"ids": ["id1,id2"]}
    client.tournaments.get_tokens(["a", "b", "c"])
    assert rec.query() == {"teamAccountIds": ["a,b,c"]}
    assert rec.last.url.path == "/api/v1/events/tokens"


def test_list_query_param_repeated(sync_client):
    client, rec = sync_client({})
    client.account.get_bulk(["id1", "id2"])
    assert rec.query() == {"accountId": ["id1", "id2"]}


def test_camelcase_query_mapping(sync_client):
    client, rec = sync_client({})
    client.tournaments.get_leaderboard(event_id="e", cumulative_id="c")
    assert rec.query() == {"eventId": ["e"], "cumulativeId": ["c"]}


def test_fortnite_token_header(sync_client):
    client, rec = sync_client({})
    client.weapons.get_lootpool(fortnite_token="tok")
    assert rec.last.headers["x-fortnite-token"] == "tok"
    assert rec.last.headers["x-api-key"] == "key"


# --- deprecations ---------------------------------------------------------------------------


def test_deprecated_battlepass_legacy_warns_at_caller(sync_client):
    client, rec = sync_client({})
    with pytest.warns(DeprecationWarning, match="battlepass") as record:
        client.battlepass.get_legacy()
    assert record[0].filename == __file__  # stacklevel=2 points at the caller
    assert rec.last.url.path == "/api/v1/shop/battlepass"


def test_deprecated_replays_parse_broadcast_warns(sync_client):
    client, rec = sync_client({})
    with pytest.warns(DeprecationWarning, match="parse_broadcast"):
        client.replays.parse_broadcast("m1")
    assert rec.last.url.path == "/api/v1/replays/m1/parse/broadcast"


def test_non_deprecated_does_not_warn(sync_client):
    client, _ = sync_client({})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        client.battlepass.get(season=35)
        client.replays.parse("m1")


async def test_async_deprecated_warns():
    client, _ = make_async({})
    with pytest.warns(DeprecationWarning, match="battlepass"):
        await client.battlepass.get_legacy()
    await client.close()


# --- moved / removed ------------------------------------------------------------------------


def test_power_rankings_resource(sync_client):
    client, rec = sync_client({})
    pr = client.power_rankings
    for name in ("get_leaderboard", "get_player", "search", "get_from_archive"):
        assert callable(getattr(pr, name))
    pr.get_leaderboard(page=2)
    assert rec.last.url.path == "/api/v1/events/powerrankings"
    pr.get_player("ninja")
    assert rec.last.url.path == "/api/v1/events/powerrankings/player/ninja"
    pr.search(q="bug")
    assert rec.last.url.path == "/api/v1/events/powerrankings/search"
    pr.get_from_archive("acc")
    assert rec.last.url.path == "/api/v1/events/powerrankings/archive/acc"


@pytest.mark.parametrize("cls", [FortniteAPI, AsyncFortniteAPI])
def test_tournaments_no_power_ranking_or_debug(cls):
    tournaments = cls("key").tournaments
    names = [n for n in dir(tournaments) if not n.startswith("_")]
    assert not [n for n in names if "power" in n or "debug" in n]
    assert not hasattr(tournaments, "get_tracker_debug")


# --- health_version -------------------------------------------------------------------------


def test_health_version_without_api_prefix(sync_client):
    client, rec = sync_client({"version": "1.2.3"})
    assert client.health_version() == {"version": "1.2.3"}
    assert str(rec.last.url) == "https://prod.api-fortnite.com/health/version"


async def test_async_health_version_without_api_prefix():
    client, rec = make_async({"version": "1"})
    await client.health_version()
    assert str(rec.last.url) == "https://prod.api-fortnite.com/health/version"
    await client.close()


# --- sync/async parity ----------------------------------------------------------------------


def _resource_pairs() -> list[tuple[type, type]]:
    pairs = []
    for name in res_pkg.__all__ if hasattr(res_pkg, "__all__") else dir(res_pkg):
        obj = getattr(res_pkg, name)
        if inspect.isclass(obj) and issubclass(obj, Resource) and obj is not Resource and not name.startswith("Async"):
            pairs.append((obj, getattr(res_pkg, "Async" + name)))
    return pairs


def _public_methods(cls: type) -> dict[str, Any]:
    return {n: f for n, f in inspect.getmembers(cls, inspect.isfunction) if not n.startswith("_")}


def test_resource_pairs_cover_client():
    pairs = _resource_pairs()
    assert len(pairs) == 26
    client = FortniteAPI("key")
    attached = {type(v) for v in vars(client).values() if isinstance(v, Resource)}
    assert attached == {s for s, _ in pairs}
    client.close()


@pytest.mark.parametrize(("sync_cls", "async_cls"), _resource_pairs(), ids=lambda c: c.__name__)
def test_sync_async_parity(sync_cls, async_cls):
    sync_m = _public_methods(sync_cls)
    async_m = _public_methods(async_cls)
    assert sync_m.keys() == async_m.keys()
    for name, fn in sync_m.items():
        afn = async_m[name]
        assert not inspect.iscoroutinefunction(fn), name
        assert inspect.iscoroutinefunction(afn), name
        assert inspect.signature(fn) == inspect.signature(afn), name


def test_client_level_parity():
    for name in ("health", "health_version"):
        assert inspect.signature(getattr(FortniteAPI, name)) == inspect.signature(getattr(AsyncFortniteAPI, name))
        assert inspect.iscoroutinefunction(getattr(AsyncFortniteAPI, name))


async def test_async_typed_and_same_url(sync_client):
    payload = [{"id": "WID_A"}]
    sclient, srec = sync_client(payload)
    aclient, arec = make_async(payload)
    s = sclient.weapons.get(major=1, minor=2)
    a = await aclient.weapons.get(major=1, minor=2)
    assert s == a
    assert isinstance(a[0], WeaponListItemDto)
    assert str(srec.last.url) == str(arec.last.url)
    await aclient.close()
