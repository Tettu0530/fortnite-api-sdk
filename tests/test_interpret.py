"""Tests for the transport-independent helpers in fortnite_api.interpret."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pydantic
import pytest

import fortnite_api
from fortnite_api import interpret
from fortnite_api.errors import (
    AuthError,
    ClientError,
    DecodeError,
    FortniteAPIError,
    NotFoundError,
    PlanRequiredError,
    RateLimitError,
    RedirectError,
    ServerError,
    UnsuccessfulResponseError,
    ValidationError,
)
from fortnite_api.models import CashPrizeScoringDto, PublishCollectionRequest, WeaponListItemDto

# --- request side -----------------------------------------------------------------------------


def test_build_url_versioned_and_root() -> None:
    base = "https://prod.api-fortnite.com/api"
    assert interpret.build_url(base, "/shop", "v1") == "https://prod.api-fortnite.com/api/v1/shop"
    assert (
        interpret.build_url(base + "/", "/cosmetics/all", "v2") == "https://prod.api-fortnite.com/api/v2/cosmetics/all"
    )
    assert interpret.build_url(base, "/health", None) == "https://prod.api-fortnite.com/health"
    assert interpret.build_url("https://example.test/custom/", "/health", None) == "https://example.test/custom/health"


def test_build_headers() -> None:
    headers = interpret.build_headers("key", "tok")
    assert headers == {
        "x-api-key": "key",
        "User-Agent": f"fortnite-api-sdk/{fortnite_api.__version__}",
        "Content-Type": "application/json",
        "x-fortnite-token": "tok",
    }
    plain = interpret.build_headers("key", None, json=False, user_agent="ua")
    assert plain == {"x-api-key": "key", "User-Agent": "ua"}


@pytest.mark.parametrize(
    "value",
    ["zq9\n", "zq9\r\n", " zq9", "zq9 ", "z\x00q9", "z\tq9", "z\u00e9q9", "z\x7fq9"],
)
def test_build_headers_rejects_invalid_credentials(value: str) -> None:
    with pytest.raises(ValueError, match="api_key contains characters") as info:
        interpret.build_headers(value)
    assert value not in str(info.value)
    with pytest.raises(ValueError, match="fortnite_token contains characters") as info:
        interpret.build_headers("key", value)
    assert value not in str(info.value)


def test_validate_credential_accepts_unset_and_printable_values() -> None:
    interpret.validate_credential("api_key", None)
    interpret.validate_credential("api_key", "")
    interpret.validate_credential("api_key", "eg1~a.b-c_d/e+f=")


def test_default_user_agent() -> None:
    assert interpret.default_user_agent() == "fortnite-api-sdk/0.3.0"


def test_clean_params_drops_none() -> None:
    assert interpret.clean_params({"a": 1, "b": None}) == {"a": 1}
    assert interpret.clean_params({"a": None}) is None
    assert interpret.clean_params(None) is None


def test_serialize_body() -> None:
    body = PublishCollectionRequest(auto_refresh=True)
    assert interpret.serialize_body(body) == {"autoRefresh": True}
    assert interpret.serialize_body({"raw": None}) == {"raw": None}
    assert interpret.serialize_body(("a", body)) == ["a", {"autoRefresh": True}]
    assert interpret.serialize_body(None) is None


def test_file_tuple_inputs(tmp_path: Path) -> None:
    replay = tmp_path / "m.replay"
    replay.write_bytes(b"P")
    handle = io.BytesIO(b"H")
    assert interpret.file_tuple(str(replay)) == ("m.replay", b"P", "application/octet-stream")
    assert interpret.file_tuple(bytearray(b"B"), "x.replay") == ("x.replay", b"B", "application/octet-stream")
    assert interpret.file_tuple(handle) == ("replay.replay", b"H", "application/octet-stream")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a/b?c#d", "a%2Fb%3Fc%23d"),
        ("100%", "100%25"),
        ("name with space", "name%20with%20space"),
        ("ünïcode", "%C3%BCn%C3%AFcode"),
        (".", "%2E"),
        ("..", "%2E%2E"),
        ("a..b", "a..b"),
        (42, "42"),
        (True, "True"),
    ],
)
def test_path_segment(value: object, expected: str) -> None:
    assert interpret.path_segment(value) == expected


def test_path_segment_rejects_empty() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        interpret.path_segment("")


# --- redirects / retries ----------------------------------------------------------------------


def test_same_origin() -> None:
    assert interpret.is_same_origin("https://a.test/x", "https://A.test:443/y?z")
    assert interpret.is_same_origin("http://a.test/x", "http://a.test:80/")
    assert not interpret.is_same_origin("https://a.test/", "http://a.test/")
    assert not interpret.is_same_origin("https://a.test/", "https://b.test/")
    assert not interpret.is_same_origin("https://a.test/", "https://a.test:8443/")


def test_redirect_headers() -> None:
    headers = {"X-Api-Key": "k", "x-fortnite-token": "t", "Authorization": "a", "User-Agent": "ua"}
    assert interpret.redirect_headers(headers, "https://a.test/1", "https://a.test/2") == headers
    assert interpret.redirect_headers(headers, "https://a.test/1", "https://b.test/2") == {"User-Agent": "ua"}


@pytest.mark.parametrize(
    ("status", "expected"),
    [(429, True), (500, True), (503, True), (599, True), (400, False), (404, False), (600, False), (200, False)],
)
def test_is_retryable_status(status: int, expected: bool) -> None:
    assert interpret.is_retryable_status(status) is expected


NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("5", 5.0),
        (" 1.5 ", 1.5),
        ("0", 0.0),
        ("-1", None),
        ("nan", None),
        ("inf", None),
        ("soon", None),
        ("", None),
        ("Thu, 01 Jan 2026 12:00:30 GMT", 30.0),
        ("Thu, 01 Jan 2026 11:00:00 GMT", 0.0),
        ("Thu, 01 Jan 2026 12:01:00 -0000", 60.0),
    ],
)
def test_parse_retry_after(value: str | None, expected: float | None) -> None:
    assert interpret.parse_retry_after(value, now=NOW) == expected


def test_parse_retry_after_max_seconds() -> None:
    assert interpret.parse_retry_after("99999999999") == 99999999999.0
    assert interpret.parse_retry_after("99999999999", max_seconds=60.0) == 60.0
    assert interpret.parse_retry_after("5", max_seconds=60.0) == 5.0
    assert interpret.parse_retry_after("soon", max_seconds=60.0) is None


def test_parse_retry_after_uses_current_time() -> None:
    assert interpret.parse_retry_after("Wed, 21 Oct 2015 07:28:00 GMT") == 0.0


# --- response side ----------------------------------------------------------------------------


def test_get_header_is_case_insensitive() -> None:
    assert interpret.get_header({"Retry-After": "3"}, "retry-after") == "3"
    assert interpret.get_header({"retry-after": "3"}, "retry-after") == "3"
    assert interpret.get_header({"other": "x"}, "retry-after") is None
    assert interpret.get_header(None, "retry-after") is None


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        (301, RedirectError),
        (400, ClientError),
        (401, AuthError),
        (403, PlanRequiredError),
        (404, NotFoundError),
        (409, ClientError),
        (422, ClientError),
        (429, RateLimitError),
        (500, ServerError),
        (504, ServerError),
        (199, FortniteAPIError),
        (600, FortniteAPIError),
    ],
)
def test_error_for_response_status_table(status: int, cls: type[FortniteAPIError]) -> None:
    err = interpret.error_for_response(status, {}, b'{"error": "x"}')
    assert type(err) is cls
    assert err.status == status
    assert err.data == {"error": "x"}


def test_error_for_response_details() -> None:
    redirect = interpret.error_for_response(302, {"Location": "https://x.test/"}, "")
    assert isinstance(redirect, RedirectError)
    assert redirect.location == "https://x.test/"
    assert redirect.message == "Unexpected redirect (302) to https://x.test/"
    limited = interpret.error_for_response(429, {"retry-after": "7"}, "{}")
    assert isinstance(limited, RateLimitError)
    assert limited.retry_after == 7.0
    assert limited.message == "Request failed with status 429"
    missing = interpret.error_for_response(429, None, None)
    assert isinstance(missing, RateLimitError)
    assert missing.retry_after is None
    assert missing.data == {"error": "Request failed"}
    nested = interpret.error_for_response(400, None, json.dumps({"error": {"code": 1}}))
    assert nested.message == "{'code': 1}"


def test_raise_for_response() -> None:
    interpret.raise_for_response(200, None, b"")
    interpret.raise_for_response(299, None, b"")
    with pytest.raises(NotFoundError):
        interpret.raise_for_response(404, None, b"")


def test_decode_json() -> None:
    assert interpret.decode_json(200, b'{"a": 1}') == {"a": 1}
    assert interpret.decode_json(200, "[1]") == [1]
    assert interpret.decode_json(200, bytearray(b"2")) == 2
    assert interpret.decode_json(204, b"") is None
    assert interpret.decode_json(200, None) is None
    with pytest.raises(DecodeError) as info:
        interpret.decode_json(201, b"x" * 5000)
    assert info.value.status == 201
    assert info.value.data == "x" * 1000
    assert isinstance(info.value.__cause__, json.JSONDecodeError)


def test_unwrap_envelopes() -> None:
    assert interpret.unwrap_envelope({"status": 200, "data": [1, 2]}) == [1, 2]
    assert interpret.unwrap_envelope({"status": "ok", "date": "x"}) == {"status": "ok", "date": "x"}
    assert interpret.unwrap_envelope({"storefronts": []}) == {"storefronts": []}
    assert interpret.unwrap_envelope({"success": True, "data": {"x": 1}}) == {"x": 1}
    assert interpret.unwrap_envelope({"success": True, "results": [1]}) == [1]
    assert interpret.unwrap_envelope({"success": True, "other": 1}) == {"success": True, "other": 1}
    with pytest.raises(UnsuccessfulResponseError) as info:
        interpret.unwrap_envelope({"success": False, "error": "nope"}, 201)
    assert info.value.status == 201
    assert info.value.message == "nope"
    with pytest.raises(UnsuccessfulResponseError, match="Request failed"):
        interpret.unwrap_envelope({"success": False})


def test_parse_response() -> None:
    payload = {"status": 200, "current": "40.10", "patches": [{"patch": "40.10"}]}
    result = interpret.parse_response(payload, list[WeaponListItemDto])
    assert isinstance(result[0], WeaponListItemDto)
    assert interpret.parse_response({"a": 1}, None) == {"a": 1}
    prizes = interpret.parse_response(
        {"w1": [{"scoringType": "value"}], "w2": []}, dict[str, list[CashPrizeScoringDto]]
    )
    assert prizes["w1"][0].scoring_type == "value"


def test_parse_response_validation_error() -> None:
    with pytest.raises(ValidationError) as info:
        interpret.parse_response([{"id": 5}], list[WeaponListItemDto], 200)
    assert "list[" in info.value.message
    assert isinstance(info.value.__cause__, pydantic.ValidationError)
    assert info.value.validation_error is info.value.__cause__
    with pytest.raises(ValidationError, match="Response does not match int: 1 validation error"):
        interpret.parse_response("x", int)


def test_interpret_json() -> None:
    body = b'{"success": true, "data": 3}'
    assert interpret.interpret_json(200, {}, body) == 3
    assert interpret.interpret_json(200, {}, body, unwrap=False) == {"success": True, "data": 3}
    assert interpret.interpret_json(200, {}, "[1]", list[int]) == [1]
    with pytest.raises(ServerError):
        interpret.interpret_json(500, {}, body)


def test_interpret_binary_and_redirect() -> None:
    assert interpret.interpret_binary(200, {}, bytearray(b"B")) == b"B"
    with pytest.raises(AuthError):
        interpret.interpret_binary(401, {}, b"")
    assert interpret.interpret_redirect(302, {"location": "https://img/x"}, b"", "https://api/x") == "https://img/x"
    assert interpret.interpret_redirect(307, {}, b"", "https://api/x") is None
    assert interpret.interpret_redirect(200, {}, b"", "https://api/x") == "https://api/x"
    with pytest.raises(ServerError):
        interpret.interpret_redirect(502, {}, b"", "https://api/x")


def test_all_exports_exist() -> None:
    exported: list[Any] = [getattr(interpret, name) for name in interpret.__all__]
    assert all(item is not None for item in exported)
