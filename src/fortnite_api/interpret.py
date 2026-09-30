"""Transport-independent request building and response interpretation.

This module holds everything the built-in httpx transports do *around* the HTTP call, as plain
functions without any dependency on an HTTP library. A custom transport (for example one built
on aiohttp that adds allowlisting, quota counting or log redaction) can reuse it to get exactly
the same semantics as the built-in transports:

* request side: :func:`build_url`, :func:`build_headers` (which validates credentials with
  :func:`validate_credential`), :func:`clean_params`, :func:`serialize_body`, :func:`file_tuple`,
  :func:`path_segment`;
* response side: :func:`interpret_json`, :func:`interpret_binary` and :func:`interpret_redirect`
  (built from :func:`raise_for_response`, :func:`decode_json`, :func:`unwrap_envelope` and
  :func:`parse_response`), which raise the exceptions from :mod:`fortnite_api.errors`;
* redirects and retries: :func:`is_same_origin`, :func:`redirect_headers`,
  :func:`is_retryable_status` and :func:`parse_retry_after` (see also
  :meth:`fortnite_api.retry.RetryConfig.next_delay`).

Headers passed to the response helpers may be any mapping; lookups are case-insensitive.

Transports must not let their HTTP library follow redirects automatically (httpx:
``follow_redirects=False``; aiohttp: ``allow_redirects=False`` on every request): both libraries
re-send custom headers such as ``x-api-key`` to another origin. Pass 3xx responses to the
``interpret_*`` functions instead (they raise :class:`~fortnite_api.errors.RedirectError`), or, when
following redirects deliberately, send only :func:`redirect_headers` to the next hop. Network
failures should be raised as :class:`~fortnite_api.errors.APIConnectionError` /
:class:`~fortnite_api.errors.APITimeoutError` (``raise ... from exc``) without echoing the
original error message, which may contain header values.
"""

from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from functools import cache
from typing import Any, BinaryIO, NoReturn, TypeAlias, get_origin
from urllib.parse import quote, urlsplit

import pydantic
from pydantic import BaseModel, TypeAdapter

from .errors import (
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

__all__ = [
    "AUTH_HEADERS",
    "DEFAULT_BASE_URL",
    "FileInput",
    "FileTuple",
    "MultipartFiles",
    "ResponseBody",
    "build_headers",
    "build_url",
    "clean_params",
    "decode_json",
    "default_user_agent",
    "error_for_response",
    "file_tuple",
    "get_header",
    "interpret_binary",
    "interpret_json",
    "interpret_redirect",
    "is_retryable_status",
    "is_same_origin",
    "parse_response",
    "parse_retry_after",
    "path_segment",
    "raise_for_response",
    "redirect_headers",
    "serialize_body",
    "unwrap_envelope",
    "validate_credential",
]

DEFAULT_BASE_URL = "https://prod.api-fortnite.com/api"

AUTH_HEADERS = frozenset({"x-api-key", "x-fortnite-token", "authorization", "cookie", "proxy-authorization"})
"""Request headers carrying credentials; stripped from cross-origin redirects."""

FileInput: TypeAlias = bytes | bytearray | BinaryIO | str
"""A replay file: raw bytes, an open binary file object, or a filesystem path."""

FileTuple: TypeAlias = tuple[str, bytes, str]
"""``(filename, content, content_type)`` of one multipart file field."""

MultipartFiles: TypeAlias = Mapping[str, FileTuple] | Sequence[tuple[str, FileTuple]]
"""Multipart files: ``{"file": tuple}`` or ``[("files", tuple), ...]`` for repeated fields."""

ResponseBody: TypeAlias = bytes | bytearray | str
"""A raw response body: bytes, or already decoded text."""

_MAX_DECODE_ERROR_BODY = 1000


# --------------------------------------------------------------------------- request side


def default_user_agent() -> str:
    """``fortnite-api-sdk/<version>``, the default ``User-Agent`` product token."""
    from . import __version__  # noqa: PLC0415 - the package is fully imported by the time this runs

    return f"fortnite-api-sdk/{__version__}"


def path_segment(value: object) -> str:
    """Percent-encode ``value`` as exactly one URL path segment.

    ``str(value)`` is quoted with no safe characters, so ``/``, ``?``, ``#`` and ``%`` cannot
    change the request target. Segments made only of dots (``.`` / ``..``) are encoded too, since
    they would otherwise be collapsed by URL normalisation. Empty values are rejected.
    """
    text = str(value)
    if not text:
        raise ValueError("path parameters must not be empty")
    if text.strip(".") == "":
        return "%2E" * len(text)
    return quote(text, safe="")


def build_url(base_url: str, path: str, version: str | None) -> str:
    """The absolute URL of ``path``.

    Versioned paths go under ``base_url`` (``{base_url}/{version}{path}``); unversioned ones
    (``/health``) go under the root, i.e. ``base_url`` without a trailing ``/api``.
    """
    base = base_url.rstrip("/")
    if version is None:
        return f"{base.removesuffix('/api')}{path}"
    return f"{base}/{version}{path}"


def validate_credential(name: str, value: str | None) -> None:
    """Reject credential values that cannot be sent as an HTTP header value.

    ``value`` must be printable ASCII without leading or trailing whitespace (a trailing newline
    from a file or ``.env`` value is the typical mistake). Otherwise HTTP libraries raise errors
    whose message echoes the secret. The :class:`ValueError` raised here only names ``name``,
    never the value. ``None`` and ``""`` are accepted (meaning "not set").
    """
    if not value:
        return
    if value != value.strip() or not all(" " <= ch <= "~" for ch in value):
        raise ValueError(
            f"{name} contains characters that are not allowed in an HTTP header "
            "(it must be printable ASCII without leading or trailing whitespace)"
        )


def build_headers(
    api_key: str,
    fortnite_token: str | None = None,
    *,
    json: bool = True,
    user_agent: str | None = None,
) -> dict[str, str]:
    """Request headers: ``x-api-key``, ``User-Agent``, optional ``x-fortnite-token`` and JSON content type.

    ``User-Agent`` is always set: ``user_agent`` if given, otherwise :func:`default_user_agent`.
    Both credentials are checked with :func:`validate_credential` (``ValueError`` without echoing
    the value).
    """
    validate_credential("api_key", api_key)
    validate_credential("fortnite_token", fortnite_token)
    headers = {"x-api-key": api_key, "User-Agent": user_agent or default_user_agent()}
    if json:
        headers["Content-Type"] = "application/json"
    if fortnite_token:
        headers["x-fortnite-token"] = fortnite_token
    return headers


def clean_params(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` query values; returns ``None`` when nothing is left."""
    if not params:
        return None
    cleaned = {k: v for k, v in params.items() if v is not None}
    return cleaned or None


def serialize_body(body: Any) -> Any:
    """Serialise a JSON request body: pydantic models are dumped by alias without ``None`` fields."""
    if isinstance(body, BaseModel):
        return body.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(body, (list, tuple)):
        return [serialize_body(item) for item in body]
    return body


def file_tuple(file: FileInput, filename: str | None = None) -> FileTuple:
    """Build a multipart file tuple from bytes, a binary file object or a filesystem path."""
    if isinstance(file, str):
        with open(file, "rb") as handle:
            content = handle.read()
        name = filename or os.path.basename(file)
    elif isinstance(file, (bytes, bytearray)):
        content = bytes(file)
        name = filename or "replay.replay"
    else:
        content = file.read()
        name = filename or str(getattr(file, "name", "replay.replay"))
    return (name, content, "application/octet-stream")


# --------------------------------------------------------------------------- redirects / retries


def _origin(url: str) -> tuple[str, str, int | None]:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    port = parts.port or {"http": 80, "https": 443}.get(scheme)
    return scheme, (parts.hostname or "").lower(), port


def is_same_origin(url_a: str, url_b: str) -> bool:
    """Whether both absolute URLs share scheme, host and (effective) port."""
    return _origin(url_a) == _origin(url_b)


def redirect_headers(headers: Mapping[str, str], from_url: str, to_url: str) -> dict[str, str]:
    """Headers to send to a redirect target: credentials (:data:`AUTH_HEADERS`) only stay same-origin."""
    if is_same_origin(from_url, to_url):
        return dict(headers)
    return {k: v for k, v in headers.items() if k.lower() not in AUTH_HEADERS}


def is_retryable_status(status: int) -> bool:
    """429 and 5xx responses are worth retrying."""
    return status == 429 or 500 <= status <= 599


def parse_retry_after(
    value: str | None, *, now: datetime | None = None, max_seconds: float | None = None
) -> float | None:
    """Seconds to wait from a ``Retry-After`` value (delta-seconds or HTTP date); ``None`` if invalid.

    The result is the server's value and is **not** capped unless ``max_seconds`` is given (a
    hostile or broken server can send ``Retry-After: 99999999999``); clamp it before sleeping.
    """
    seconds = _parse_retry_after(value, now)
    if seconds is not None and max_seconds is not None:
        return min(seconds, max_seconds)
    return seconds


def _parse_retry_after(value: str | None, now: datetime | None) -> float | None:
    if value is None:
        return None
    text = value.strip()
    try:
        seconds = float(text)
    except ValueError:
        pass
    else:
        return seconds if math.isfinite(seconds) and seconds >= 0 else None
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    return max(0.0, (when - current).total_seconds())


# --------------------------------------------------------------------------- response side


def get_header(headers: Mapping[str, str] | None, name: str) -> str | None:
    """Case-insensitive header lookup that works with plain dicts and multidicts alike."""
    if not headers:
        return None
    value = headers.get(name)
    if value is None:
        lowered = name.lower()
        value = next((v for k, v in headers.items() if k.lower() == lowered), None)
    return value


def _text(body: ResponseBody | None) -> str:
    if body is None:
        return ""
    if isinstance(body, str):
        return body
    return bytes(body).decode("utf-8", errors="replace")


def _message(data: Any) -> str | None:
    if isinstance(data, dict):
        for key in ("error", "title", "detail", "message"):
            value = data.get(key)
            if value:
                return str(value)
    return None


def error_for_response(status: int, headers: Mapping[str, str] | None, body: ResponseBody | None) -> FortniteAPIError:
    """The exception for a non-2xx response (see the table in :mod:`fortnite_api.errors`)."""
    try:
        data: Any = json.loads(_text(body))
    except ValueError:
        data = {"error": "Request failed"}
    message = _message(data) or f"Request failed with status {status}"
    if 300 <= status <= 399:
        location = get_header(headers, "location")
        return RedirectError(f"Unexpected redirect ({status}) to {location}", status, data, location=location)
    if status == 401:
        return AuthError(message, status, data)
    if status == 403:
        return PlanRequiredError(message, status, data)
    if status == 404:
        return NotFoundError(message, status, data)
    if status == 429:
        retry_after = parse_retry_after(get_header(headers, "retry-after"))
        return RateLimitError(message, status, data, retry_after=retry_after)
    if 400 <= status <= 499:
        return ClientError(message, status, data)
    if 500 <= status <= 599:
        return ServerError(message, status, data)
    return FortniteAPIError(message, status, data)


def raise_for_response(status: int, headers: Mapping[str, str] | None, body: ResponseBody | None) -> None:
    """Raise the matching :class:`~fortnite_api.errors.FortniteAPIError` unless ``status`` is 2xx."""
    if not 200 <= status <= 299:
        raise error_for_response(status, headers, body)


def decode_json(status: int, body: ResponseBody | None) -> Any:
    """Decode a JSON body (an empty body is ``None``); raises :class:`~fortnite_api.errors.DecodeError`."""
    text = _text(body)
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError as exc:
        raise DecodeError(f"Response body is not valid JSON: {exc}", status, text[:_MAX_DECODE_ERROR_BODY]) from exc


def unwrap_envelope(data: Any, status: int = 200) -> Any:
    """Strip the API's response envelopes.

    ``{"success": true, "data"|"results": x}`` and ``{"status": ..., "data": x}`` yield ``x``;
    ``{"success": false, ...}`` raises :class:`~fortnite_api.errors.UnsuccessfulResponseError`
    carrying the real HTTP ``status`` and the whole envelope. Anything else is returned as is.
    """
    if isinstance(data, dict):
        if "success" in data:
            if not data.get("success"):
                raise UnsuccessfulResponseError(_message(data) or "Request failed", status, data)
            if "data" in data:
                return data["data"]
            if "results" in data:
                return data["results"]
        elif "data" in data and "status" in data:
            return data["data"]
    return data


@cache
def _adapter(response_type: Any) -> TypeAdapter[Any]:
    return TypeAdapter(response_type)


def _type_name(response_type: Any) -> str:
    # ``list[X]`` passes isinstance(..., type) on Python 3.10, hence the get_origin check.
    if get_origin(response_type) is None and isinstance(response_type, type):
        return response_type.__name__
    return str(response_type)


def parse_response(data: Any, response_type: Any = None, status: int = 200) -> Any:
    """Validate ``data`` against ``response_type`` (a model, ``list[Model]``, ``dict[str, ...]``...).

    ``None`` returns the raw JSON untouched. For list types, a dict holding exactly one list value
    (e.g. ``{"status": 200, "patches": [...]}``) is unwrapped to that list. Validation failures raise
    :class:`~fortnite_api.errors.ValidationError` with the pydantic error as ``__cause__``.
    """
    if response_type is None:
        return data
    if get_origin(response_type) is list and isinstance(data, dict):
        lists = [v for v in data.values() if isinstance(v, list)]
        if len(lists) == 1:
            data = lists[0]
    try:
        return _adapter(response_type).validate_python(data)
    except pydantic.ValidationError as exc:
        _raise_validation(exc, data, response_type, status)


def _raise_validation(exc: pydantic.ValidationError, data: Any, response_type: Any, status: int) -> NoReturn:
    message = f"Response does not match {_type_name(response_type)}: {exc.error_count()} validation error(s)"
    raise ValidationError(message, status, data, validation_error=exc) from exc


def interpret_json(
    status: int,
    headers: Mapping[str, str] | None,
    body: ResponseBody | None,
    response_type: Any = None,
    *,
    unwrap: bool = True,
) -> Any:
    """Full pipeline for JSON endpoints: status check, decode, envelope unwrap and model validation.

    ``unwrap=False`` skips :func:`unwrap_envelope` (used by ``request_multipart(unwrap=False)``).
    """
    raise_for_response(status, headers, body)
    data = decode_json(status, body)
    if unwrap:
        data = unwrap_envelope(data, status)
    return parse_response(data, response_type, status)


def interpret_binary(status: int, headers: Mapping[str, str] | None, body: bytes | bytearray) -> bytes:
    """Return the raw body of a binary endpoint, raising for non-2xx statuses."""
    raise_for_response(status, headers, body)
    return bytes(body)


def interpret_redirect(
    status: int, headers: Mapping[str, str] | None, body: ResponseBody | None, url: str
) -> str | None:
    """For endpoints answering with a redirect: the ``Location`` of a 3xx, the request ``url`` for 2xx."""
    if 300 <= status <= 399:
        return get_header(headers, "location")
    raise_for_response(status, headers, body)
    return url
