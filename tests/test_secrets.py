"""The API key and user token never appear in reprs, exception messages or exception data."""

from __future__ import annotations

import socket
from collections.abc import Iterator

import httpx
import pytest

from fortnite_api import (
    APIConnectionError,
    APITimeoutError,
    AsyncFortniteAPI,
    AsyncTransport,
    AuthError,
    ClientError,
    DecodeError,
    FortniteAPI,
    FortniteAPIError,
    NotFoundError,
    PlanRequiredError,
    RateLimitError,
    RedirectError,
    ServerError,
    SyncTransport,
    UnsuccessfulResponseError,
    ValidationError,
)
from fortnite_api._transport import _wrap_transport_error
from tests.helpers import SECRET_KEY, SECRET_TOKEN, Handler, async_transport, mock_async, mock_sync, sync_transport

SECRETS = (SECRET_KEY, SECRET_TOKEN)


def assert_clean(*texts: str) -> None:
    for text in texts:
        for secret in SECRETS:
            assert secret not in text


def test_client_and_transport_reprs_mask_credentials() -> None:
    client = FortniteAPI(SECRET_KEY, fortnite_token=SECRET_TOKEN)
    transport = client.transport
    assert_clean(repr(client), str(client), repr(transport), str(transport))
    assert "'***'" in repr(transport)
    client.close()
    sync_t = SyncTransport(SECRET_KEY, fortnite_token=SECRET_TOKEN)
    async_t = AsyncTransport(SECRET_KEY, fortnite_token=SECRET_TOKEN)
    async_client = AsyncFortniteAPI(SECRET_KEY, fortnite_token=SECRET_TOKEN)
    assert_clean(repr(sync_t), repr(async_t), repr(async_client), repr(async_client.transport))
    sync_t.close()


def _raise(exc: type[httpx.TransportError]) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        raise exc(f"failed for {request.url}", request=request)

    return handler


CASES: list[tuple[Handler, type[FortniteAPIError]]] = [
    (lambda _r: httpx.Response(302, headers={"location": "https://elsewhere.test/"}), RedirectError),
    (lambda _r: httpx.Response(400, json={"error": "bad"}), ClientError),
    (lambda _r: httpx.Response(401, json={"error": "bad key"}), AuthError),
    (lambda _r: httpx.Response(403, json={"error": "plan"}), PlanRequiredError),
    (lambda _r: httpx.Response(404, json={"error": "missing"}), NotFoundError),
    (lambda _r: httpx.Response(429, headers={"retry-after": "1"}, json={"error": "slow"}), RateLimitError),
    (lambda _r: httpx.Response(500, text="oops"), ServerError),
    (lambda _r: httpx.Response(200, json={"success": False, "error": "no"}), UnsuccessfulResponseError),
    (lambda _r: httpx.Response(200, text="<html>"), DecodeError),
    (lambda _r: httpx.Response(200, json={"chapter": "x"}), ValidationError),
    (_raise(httpx.ConnectError), APIConnectionError),
    (_raise(httpx.ReadTimeout), APITimeoutError),
]


@pytest.mark.parametrize(("handler", "cls"), CASES, ids=[c.__name__ for _h, c in CASES])
def test_exceptions_never_contain_credentials(handler: Handler, cls: type[FortniteAPIError]) -> None:
    client = mock_sync(handler, api_key=SECRET_KEY, fortnite_token=SECRET_TOKEN)
    with pytest.raises(cls) as info:
        client.map.get()
    err = info.value
    assert type(err) is cls
    assert_clean(str(err), repr(err), err.message, repr(err.data), str(err.data), repr(vars(err)))
    if isinstance(err, APIConnectionError):
        cause = err.__cause__
        assert isinstance(cause, httpx.TransportError)
        assert_clean(repr(cause.request.headers), str(dict(cause.request.headers)), repr(vars(cause)))
        assert cause.request.headers["x-api-key"] == "***"
        assert cause.request.headers["x-fortnite-token"] == "***"
    client.close()


@pytest.mark.parametrize(("handler", "cls"), CASES, ids=[c.__name__ for _h, c in CASES])
async def test_async_exceptions_never_contain_credentials(handler: Handler, cls: type[FortniteAPIError]) -> None:
    client = mock_async(handler, api_key=SECRET_KEY, fortnite_token=SECRET_TOKEN)
    with pytest.raises(cls) as info:
        await client.map.get()
    err = info.value
    assert_clean(str(err), repr(err), repr(err.data), repr(vars(err)))
    if isinstance(err, APIConnectionError):
        assert isinstance(err.__cause__, httpx.TransportError)
        assert_clean(repr(err.__cause__.request.headers))
    await client.close()


# --- credentials that are not valid header values ---------------------------------------------

BAD_VALUES = [SECRET_KEY + "\n", SECRET_KEY + "\r\n", SECRET_KEY + " ", SECRET_KEY + "\x00", SECRET_KEY + "é"]


@pytest.mark.parametrize("value", BAD_VALUES)
def test_invalid_credentials_are_rejected_without_echoing_them(value: str) -> None:
    for make in (
        lambda: FortniteAPI(value),
        lambda: FortniteAPI("key", fortnite_token=value),
        lambda: AsyncFortniteAPI(value),
        lambda: SyncTransport(value),
        lambda: AsyncTransport("key", fortnite_token=value),
    ):
        with pytest.raises(ValueError, match="contains characters") as info:
            make()
        assert_clean(str(info.value), repr(info.value))


@pytest.fixture
def silent_server() -> Iterator[str]:
    """A real TCP socket that accepts connections (via the backlog) and never answers."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(8)
        yield f"http://127.0.0.1:{sock.getsockname()[1]}/api"


def test_per_call_token_is_validated_before_sending(silent_server: str) -> None:
    client = FortniteAPI(SECRET_KEY, base_url=silent_server, timeout=2.0)
    with pytest.raises(ValueError, match="fortnite_token contains characters") as info:
        client.map.get(fortnite_token=SECRET_TOKEN + "\r\n")
    assert_clean(str(info.value))
    client.close()


def test_h11_rejection_over_a_real_socket_does_not_leak(silent_server: str) -> None:
    """Even if an invalid value slips past validation, h11's message (which echoes it) is not used."""
    client = FortniteAPI(SECRET_KEY, base_url=silent_server, timeout=2.0)
    transport = sync_transport(client)
    # bypass the validation in build_headers on purpose
    transport._headers = lambda fortnite_token, json=True: {"x-api-key": SECRET_KEY + "\n"}  # type: ignore[method-assign]
    with pytest.raises(APIConnectionError) as info:
        transport.request("GET", "/weapons", "v2")
    err = info.value
    assert err.message == "Connection failed (LocalProtocolError)"
    assert isinstance(err.__cause__, httpx.LocalProtocolError)
    assert SECRET_KEY in str(err.__cause__)  # h11 does echo the value - hence type names only
    assert_clean(str(err), repr(err), repr(vars(err)), repr(err.__cause__.request.headers))
    client.close()


async def test_async_h11_rejection_over_a_real_socket_does_not_leak(silent_server: str) -> None:
    client = AsyncFortniteAPI(SECRET_KEY, base_url=silent_server, timeout=2.0)
    transport = async_transport(client)
    transport._headers = lambda fortnite_token, json=True: {"x-fortnite-token": SECRET_TOKEN + "\n"}  # type: ignore[method-assign]
    with pytest.raises(APIConnectionError) as info:
        await transport.request("GET", "/weapons", "v2")
    assert_clean(str(info.value), repr(info.value), repr(info.value.__cause__.request.headers))  # type: ignore[union-attr]
    await client.close()


def test_wrap_transport_error_without_request() -> None:
    err = _wrap_transport_error(httpx.ConnectError(f"refused {SECRET_KEY}"))
    assert err.message == "Connection failed (ConnectError)"
