"""Built-in httpx transports (implementations of :mod:`fortnite_api.protocol`)."""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, TypeVar, overload

import httpx

from .errors import APIConnectionError, APITimeoutError, RedirectError
from .interpret import (
    AUTH_HEADERS,
    DEFAULT_BASE_URL,
    MultipartFiles,
    build_headers,
    build_url,
    clean_params,
    default_user_agent,
    interpret_binary,
    interpret_json,
    interpret_redirect,
    redirect_headers,
    serialize_body,
    validate_credential,
)
from .retry import RetryConfig

__all__ = ["DEFAULT_BASE_URL", "DEFAULT_MAX_REDIRECTS", "AsyncTransport", "SyncTransport"]

T = TypeVar("T")

DEFAULT_MAX_REDIRECTS = 5
_REDACTED = "'***'"


def _redact_request(exc: httpx.TransportError) -> None:
    """Mask credential headers on the request attached to ``exc`` (it has already been sent)."""
    try:
        request = exc.request
    except RuntimeError:  # no request attached
        return
    for name in AUTH_HEADERS:
        if name in request.headers:
            request.headers[name] = "***"


def _wrap_transport_error(exc: httpx.TransportError) -> APIConnectionError:
    """Map an httpx transport failure to the SDK's exception (the caller chains ``exc`` as the cause).

    Only the exception type is used in the message: httpx/h11 messages can echo header values
    (e.g. ``Illegal header value b'<key>'``). The credential headers of ``exc.request`` are masked,
    so the chained ``__cause__`` does not carry the API key or the user token either.
    """
    _redact_request(exc)
    if isinstance(exc, httpx.TimeoutException):
        return APITimeoutError(f"Request timed out ({type(exc).__name__})")
    return APIConnectionError(f"Connection failed ({type(exc).__name__})")


class _BaseTransport:
    """State and decisions shared by the sync and async transports (no I/O)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
        *,
        retry: RetryConfig | None = None,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        user_agent: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        validate_credential("api_key", api_key)
        validate_credential("fortnite_token", fortnite_token)
        self._api_key = api_key
        self._fortnite_token = fortnite_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry = retry
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.user_agent = user_agent or f"{default_user_agent()} python-httpx/{httpx.__version__}"
        self._random: Callable[[], float] = random.random

    def __repr__(self) -> str:
        token = _REDACTED if self._fortnite_token else "None"
        return (
            f"{type(self).__name__}(base_url={self.base_url!r}, api_key={_REDACTED}, fortnite_token={token}, "
            f"timeout={self.timeout!r}, retry={self.retry!r}, follow_redirects={self.follow_redirects!r})"
        )

    def _url(self, path: str, version: str | None) -> str:
        return build_url(self.base_url, path, version)

    def _headers(self, fortnite_token: str | None, json: bool = True) -> dict[str, str]:
        return build_headers(
            self._api_key, fortnite_token or self._fortnite_token, json=json, user_agent=self.user_agent
        )

    def _retry_delay(
        self, attempt: int, retryable: bool, status: int | None, headers: Mapping[str, str] | None
    ) -> float | None:
        """Seconds to wait before retrying, or ``None`` when the request must not be retried.

        ``status`` is ``None`` for connection errors / timeouts.
        """
        if self.retry is None:
            return None
        return self.retry.next_delay(attempt, retryable=retryable, status=status, headers=headers, random=self._random)

    def _next_hop(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: dict[str, Any],
        *,
        resp: httpx.Response,
        hops: int,
    ) -> tuple[str, str, dict[str, str], dict[str, Any]]:
        """The request to send after the redirect ``resp`` (credentials only kept for same-origin)."""
        location = resp.headers["location"]
        if hops > self.max_redirects:
            raise RedirectError(
                f"Exceeded the maximum of {self.max_redirects} redirects", resp.status_code, None, location=location
            )
        next_url = str(httpx.URL(url).join(location))
        next_headers = redirect_headers(headers, url, next_url)
        status = resp.status_code
        if (status == 303 and method != "HEAD") or (status in (301, 302) and method == "POST"):
            method, body = "GET", {}
            next_headers = {k: v for k, v in next_headers.items() if k.lower() != "content-type"}
        return method, next_url, next_headers, body


class SyncTransport(_BaseTransport):
    """Blocking httpx transport (implements :class:`~fortnite_api.protocol.SyncTransportProtocol`).

    Redirects are not followed unless ``follow_redirects=True``; even then credentials are only
    re-sent to the same origin and at most ``max_redirects`` hops are taken. Retries are disabled
    unless a :class:`~fortnite_api.retry.RetryConfig` is given.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
        *,
        retry: RetryConfig | None = None,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        user_agent: str | None = None,
    ) -> None:
        super().__init__(
            api_key,
            base_url,
            timeout,
            fortnite_token,
            retry=retry,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            user_agent=user_agent,
        )
        self._client = httpx.Client(timeout=self.timeout, follow_redirects=False)
        self._sleep: Callable[[float], None] = time.sleep

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _send_once(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        *,
        params: dict[str, Any] | None,
        body: dict[str, Any],
        follow: bool,
    ) -> httpx.Response:
        hops = 0
        while True:
            request = self._client.build_request(method, url, params=params, headers=headers, **body)
            try:
                resp = self._client.send(request)
            except httpx.TransportError as exc:
                raise _wrap_transport_error(exc) from exc
            if not (follow and resp.is_redirect):
                return resp
            hops += 1
            method, url, headers, body = self._next_hop(method, str(request.url), headers, body, resp=resp, hops=hops)
            params = None  # the Location already carries the query string

    def _send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        *,
        params: Mapping[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        retryable: bool = False,
        follow: bool | None = None,
    ) -> httpx.Response:
        follow = self.follow_redirects if follow is None else follow
        attempt = 0
        while True:
            try:
                resp = self._send_once(
                    method, url, headers, params=clean_params(params), body=body or {}, follow=follow
                )
            except APIConnectionError:
                delay = self._retry_delay(attempt, retryable, None, None)
                if delay is None:
                    raise
            else:
                delay = self._retry_delay(attempt, retryable, resp.status_code, resp.headers)
                if delay is None:
                    return resp
            self._sleep(delay)
            attempt += 1

    @overload
    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: None = ...,
        retryable: bool = ...,
    ) -> Any: ...

    @overload
    def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: type[T],
        retryable: bool = ...,
    ) -> T: ...

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
        resp = self._send(
            method,
            self._url(path, version),
            self._headers(fortnite_token),
            params=params,
            body={"json": serialize_body(json_body)},
            retryable=retryable,
        )
        return interpret_json(resp.status_code, resp.headers, resp.content, response_type)

    def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = self._send("GET", self._url(path, version), self._headers(fortnite_token, json=False), retryable=True)
        return interpret_binary(resp.status_code, resp.headers, resp.content)

    def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        resp = self._send(
            "GET",
            self._url(path, version),
            self._headers(fortnite_token, json=False),
            params=params,
            retryable=True,
            follow=False,
        )
        return interpret_redirect(resp.status_code, resp.headers, resp.content, str(resp.url))

    @overload
    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: None = ..., unwrap: bool = ...
    ) -> Any: ...

    @overload
    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: type[T], unwrap: bool = ...
    ) -> T: ...

    def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        resp = self._send("POST", self._url(path, "v1"), self._headers(None, json=False), body={"files": files})
        return interpret_json(resp.status_code, resp.headers, resp.content, response_type, unwrap=unwrap)


class AsyncTransport(_BaseTransport):
    """Asynchronous httpx transport (implements :class:`~fortnite_api.protocol.AsyncTransportProtocol`).

    Same redirect and retry behaviour as :class:`SyncTransport`.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        fortnite_token: str | None = None,
        *,
        retry: RetryConfig | None = None,
        follow_redirects: bool = False,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
        user_agent: str | None = None,
    ) -> None:
        super().__init__(
            api_key,
            base_url,
            timeout,
            fortnite_token,
            retry=retry,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            user_agent=user_agent,
        )
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=False)
        self._sleep: Callable[[float], Awaitable[None]] = asyncio.sleep

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def _send_once(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        *,
        params: dict[str, Any] | None,
        body: dict[str, Any],
        follow: bool,
    ) -> httpx.Response:
        hops = 0
        while True:
            request = self._client.build_request(method, url, params=params, headers=headers, **body)
            try:
                resp = await self._client.send(request)
            except httpx.TransportError as exc:
                raise _wrap_transport_error(exc) from exc
            if not (follow and resp.is_redirect):
                return resp
            hops += 1
            method, url, headers, body = self._next_hop(method, str(request.url), headers, body, resp=resp, hops=hops)
            params = None  # the Location already carries the query string

    async def _send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        *,
        params: Mapping[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        retryable: bool = False,
        follow: bool | None = None,
    ) -> httpx.Response:
        follow = self.follow_redirects if follow is None else follow
        attempt = 0
        while True:
            try:
                resp = await self._send_once(
                    method, url, headers, params=clean_params(params), body=body or {}, follow=follow
                )
            except APIConnectionError:
                delay = self._retry_delay(attempt, retryable, None, None)
                if delay is None:
                    raise
            else:
                delay = self._retry_delay(attempt, retryable, resp.status_code, resp.headers)
                if delay is None:
                    return resp
            await self._sleep(delay)
            attempt += 1

    @overload
    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: None = ...,
        retryable: bool = ...,
    ) -> Any: ...

    @overload
    async def request(
        self,
        method: str,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = ...,
        json_body: Any = ...,
        fortnite_token: str | None = ...,
        response_type: type[T],
        retryable: bool = ...,
    ) -> T: ...

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
        resp = await self._send(
            method,
            self._url(path, version),
            self._headers(fortnite_token),
            params=params,
            body={"json": serialize_body(json_body)},
            retryable=retryable,
        )
        return interpret_json(resp.status_code, resp.headers, resp.content, response_type)

    async def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        resp = await self._send(
            "GET", self._url(path, version), self._headers(fortnite_token, json=False), retryable=True
        )
        return interpret_binary(resp.status_code, resp.headers, resp.content)

    async def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        resp = await self._send(
            "GET",
            self._url(path, version),
            self._headers(fortnite_token, json=False),
            params=params,
            retryable=True,
            follow=False,
        )
        return interpret_redirect(resp.status_code, resp.headers, resp.content, str(resp.url))

    @overload
    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: None = ..., unwrap: bool = ...
    ) -> Any: ...

    @overload
    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: type[T], unwrap: bool = ...
    ) -> T: ...

    async def request_multipart(
        self, path: str, files: MultipartFiles, *, response_type: Any = None, unwrap: bool = True
    ) -> Any:
        resp = await self._send("POST", self._url(path, "v1"), self._headers(None, json=False), body={"files": files})
        return interpret_json(resp.status_code, resp.headers, resp.content, response_type, unwrap=unwrap)
