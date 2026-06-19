from __future__ import annotations

import pytest

from fortnite_api._transport import _BaseTransport
from fortnite_api.errors import FortniteAPIError
from fortnite_api.models import WeaponListItemDto


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
    result = t._parse(payload, WeaponListItemDto, is_list=True)
    assert len(result) == 1
    assert isinstance(result[0], WeaponListItemDto)


def test_api_key_required():
    with pytest.raises(ValueError):
        _BaseTransport("")
