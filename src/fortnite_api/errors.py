"""Exception hierarchy of the SDK.

Every exception raised for a failed API call derives from :class:`FortniteAPIError`, so
``except FortniteAPIError`` keeps catching everything. The subclasses let callers react to a
specific failure without inspecting ``status``:

==========================  ==============================================================
HTTP status / condition     Exception
==========================  ==============================================================
3xx                         :class:`RedirectError`
401                         :class:`AuthError`
403                         :class:`PlanRequiredError`
404                         :class:`NotFoundError`
429                         :class:`RateLimitError` (``retry_after`` in seconds or ``None``)
any other 4xx               :class:`ClientError`
5xx                         :class:`ServerError`
any other status            :class:`FortniteAPIError`
2xx with ``success: false`` :class:`UnsuccessfulResponseError`
2xx with a non-JSON body    :class:`DecodeError`
2xx failing model checks    :class:`ValidationError`
connection failure          :class:`APIConnectionError` (``status == 0``)
timeout                     :class:`APITimeoutError` (``status == 0``)
==========================  ==============================================================

Exceptions never hold request headers: ``str()``, ``repr()`` and ``data`` only contain the
status, a message and the response body, so the API key and user tokens cannot leak through
logs or error reports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pydantic

__all__ = [
    "NETWORK_ERROR_STATUS",
    "APIConnectionError",
    "APITimeoutError",
    "AuthError",
    "ClientError",
    "DecodeError",
    "FortniteAPIError",
    "NotFoundError",
    "PlanRequiredError",
    "RateLimitError",
    "RedirectError",
    "ServerError",
    "UnsuccessfulResponseError",
    "ValidationError",
]

NETWORK_ERROR_STATUS = 0
"""``status`` of errors raised before any HTTP response was received (connection errors, timeouts)."""


class FortniteAPIError(Exception):
    """Base class of every error raised by the SDK for a failed API call.

    Attributes:
        message: A human-readable description (taken from the response body when possible).
        status: The HTTP status code of the response, or ``0`` (:data:`NETWORK_ERROR_STATUS`)
            when no response was received.
        data: The decoded response body (or ``None``). Never contains request headers.
    """

    def __init__(self, message: str, status: int, data: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.data = data

    def __str__(self) -> str:
        return f"[{self.status}] {self.message}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status={self.status!r}, message={self.message!r})"


class RedirectError(FortniteAPIError):
    """The API answered with a 3xx redirect that the SDK did not follow.

    Redirects are not followed by default because the API key would be re-sent to the target.
    ``location`` holds the ``Location`` header (or ``None``).
    """

    def __init__(self, message: str, status: int, data: Any = None, *, location: str | None = None) -> None:
        super().__init__(message, status, data)
        self.location = location


class ClientError(FortniteAPIError):
    """A 4xx response without a more specific subclass (e.g. 400, 409, 413, 422)."""


class AuthError(ClientError):
    """401: the API key (or the ``x-fortnite-token``) is missing, invalid or expired."""


class PlanRequiredError(ClientError):
    """403: the API key's plan does not include this endpoint, or access is forbidden."""


class NotFoundError(ClientError):
    """404: the requested resource does not exist."""


class RateLimitError(ClientError):
    """429: too many requests or quota exhausted.

    ``retry_after`` is the number of seconds from the ``Retry-After`` header (given either as
    seconds or as an HTTP date), or ``None`` when the header is absent or malformed. It is the
    server's value and is **not** capped: clamp it before sleeping on it (the built-in retries cap
    it at :attr:`RetryConfig.max_retry_after <fortnite_api.retry.RetryConfig.max_retry_after>`).
    """

    def __init__(self, message: str, status: int, data: Any = None, *, retry_after: float | None = None) -> None:
        super().__init__(message, status, data)
        self.retry_after = retry_after


class ServerError(FortniteAPIError):
    """5xx: the API failed to handle the request."""


class UnsuccessfulResponseError(FortniteAPIError):
    """A 2xx response whose body is a ``{"success": false, ...}`` envelope.

    ``status`` is the real HTTP status (not a synthetic 422) and ``data`` the full envelope.
    """


class DecodeError(FortniteAPIError):
    """A 2xx response whose body is not valid JSON although JSON was expected.

    ``data`` holds (up to 1000 characters of) the undecodable body as text.
    """


class ValidationError(FortniteAPIError):
    """A response body that does not match the expected model.

    ``validation_error`` (also available as ``__cause__``) is the underlying
    :class:`pydantic.ValidationError`; ``data`` is the JSON payload that failed validation.
    """

    def __init__(
        self,
        message: str,
        status: int,
        data: Any = None,
        *,
        validation_error: pydantic.ValidationError | None = None,
    ) -> None:
        super().__init__(message, status, data)
        self.validation_error = validation_error


class APIConnectionError(FortniteAPIError):
    """The request could not be completed (DNS, connection refused, TLS, protocol error...).

    ``status`` is ``0`` (:data:`NETWORK_ERROR_STATUS`); the original transport exception is kept as
    ``__cause__``. The message only names the exception type (never its text, which can echo
    header values), and the built-in transports mask the credential headers of the request
    attached to the cause (``__cause__.request.headers``).
    """

    def __init__(self, message: str, status: int = NETWORK_ERROR_STATUS, data: Any = None) -> None:
        super().__init__(message, status, data)


class APITimeoutError(APIConnectionError):
    """The request timed out (connect, read, write or pool timeout). ``status`` is ``0``."""
