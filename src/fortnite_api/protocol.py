"""The transport interface the generated resources call.

:class:`~fortnite_api.FortniteAPI` / :class:`~fortnite_api.AsyncFortniteAPI` accept any object
implementing :class:`SyncTransportProtocol` / :class:`AsyncTransportProtocol` via ``transport=``.
The built-in :class:`~fortnite_api.SyncTransport` and :class:`~fortnite_api.AsyncTransport`
(httpx) implement them; a custom transport can reuse :mod:`fortnite_api.interpret` to build
requests and interpret responses with identical semantics.

Arguments passed by the resources:

``method``
    HTTP method (``"GET"``, ``"POST"``, ``"DELETE"``...).
``path``
    The path below the version prefix, e.g. ``"/account/abc%2Fdef"``. Path parameters are
    already percent-encoded with :func:`fortnite_api.interpret.path_segment`.
``version``
    ``"v1"`` / ``"v2"``, or ``None`` for unversioned root paths such as ``/health``;
    see :func:`fortnite_api.interpret.build_url`.
``params``
    Query parameters; ``None`` values mean "not set" (:func:`~fortnite_api.interpret.clean_params`).
``json_body``
    Request body, possibly containing pydantic models (:func:`~fortnite_api.interpret.serialize_body`).
``fortnite_token``
    Per-call ``x-fortnite-token`` overriding the transport default.
``response_type``
    Type to validate the (unwrapped) JSON with, or ``None`` for raw JSON
    (:func:`~fortnite_api.interpret.interpret_json`).
``retryable``
    ``True`` when repeating the request has no side effects or cost: the ``GET`` endpoints except
    ``replays.parse*`` (each call consumes parsing credits) and ``oauth.get_token`` (starts a new
    device-code flow), plus the read-only bulk ``POST`` lookups. Transports may only retry requests
    marked this way; :meth:`fortnite_api.retry.RetryConfig.next_delay` implements the SDK's policy.
``files``
    Multipart file fields built with :func:`~fortnite_api.interpret.file_tuple`.
``unwrap``
    Whether to strip the response envelope (:func:`~fortnite_api.interpret.unwrap_envelope`).

``request_multipart`` always posts to ``version="v1"``. ``request_redirect`` must not follow the
redirect: it returns the ``Location`` of a 3xx response, or the request URL for a 2xx response
(:func:`~fortnite_api.interpret.interpret_redirect`).

Requirements for implementations:

* **Do not follow redirects automatically.** httpx (``follow_redirects=True``) and aiohttp (whose
  default is ``allow_redirects=True``) re-send custom headers such as ``x-api-key`` and
  ``x-fortnite-token`` to another origin, which would leak the credentials. Disable it on every
  request (aiohttp: ``allow_redirects=False``) and hand 3xx responses to the ``interpret_*``
  functions, which raise :class:`~fortnite_api.errors.RedirectError`. A transport that follows
  redirects deliberately must send only :func:`~fortnite_api.interpret.redirect_headers` to the
  next hop and cap the number of hops.
* **Raise the SDK's network errors.** Map connection failures to
  :class:`~fortnite_api.errors.APIConnectionError` and timeouts to
  :class:`~fortnite_api.errors.APITimeoutError` (``raise APIConnectionError(...) from exc``), so
  callers catching :class:`~fortnite_api.errors.FortniteAPIError` see them. Do not put the
  original error text into the message: HTTP libraries may echo header values in it.

Both protocols are ``runtime_checkable``, but ``isinstance`` only checks that the four method names
exist, so it cannot tell a sync transport from an async one. The clients additionally check
``inspect.iscoroutinefunction(transport.request)`` and raise :class:`TypeError` on a mismatch.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, TypeVar, overload, runtime_checkable

from .interpret import MultipartFiles

__all__ = ["AsyncTransportProtocol", "SyncTransportProtocol"]

T = TypeVar("T")


@runtime_checkable
class SyncTransportProtocol(Protocol):
    """Blocking transport used by :class:`~fortnite_api.FortniteAPI`."""

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
        """Send a JSON request and return the interpreted (unwrapped, validated) response."""

    def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        """``GET`` a binary resource and return its bytes."""

    def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        """``GET`` an endpoint that redirects and return the target URL without following it."""

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
        """``POST`` multipart ``files`` to ``/api/v1{path}`` and return the interpreted response."""


@runtime_checkable
class AsyncTransportProtocol(Protocol):
    """Asynchronous transport used by :class:`~fortnite_api.AsyncFortniteAPI` (same semantics)."""

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
        """Send a JSON request and return the interpreted (unwrapped, validated) response."""

    async def request_binary(self, path: str, version: str | None, *, fortnite_token: str | None = None) -> bytes:
        """``GET`` a binary resource and return its bytes."""

    async def request_redirect(
        self,
        path: str,
        version: str | None,
        *,
        params: Mapping[str, Any] | None = None,
        fortnite_token: str | None = None,
    ) -> str | None:
        """``GET`` an endpoint that redirects and return the target URL without following it."""

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
        """``POST`` multipart ``files`` to ``/api/v1{path}`` and return the interpreted response."""
