"""Deterministic tests for the opt-in retry policy (sleep and random are injected)."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any

import httpx
import pytest

from fortnite_api import (
    APIConnectionError,
    APITimeoutError,
    AsyncFortniteAPI,
    ClientError,
    FortniteAPI,
    RateLimitError,
    RetryConfig,
    ServerError,
)
from tests.helpers import async_transport, mock_async, mock_sync, sync_transport

NO_JITTER = RetryConfig(max_retries=3, backoff_base=1.0, backoff_max=5.0, jitter=False, max_retry_after=10.0)


class Script:
    """Answers requests from a list of responses (or exceptions), recording each request."""

    def __init__(self, *steps: httpx.Response | type[httpx.TransportError]) -> None:
        self.steps: Iterator[httpx.Response | type[httpx.TransportError]] = iter(steps)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        step = next(self.steps)
        if isinstance(step, httpx.Response):
            return step
        raise step("boom", request=request)


def ok(payload: Any = None) -> httpx.Response:
    return httpx.Response(200, json={} if payload is None else payload)


def status(code: int, headers: Mapping[str, str] | None = None) -> httpx.Response:
    return httpx.Response(code, headers=headers, json={"error": f"status {code}"})


def sync_with(script: Script, retry: RetryConfig | None = NO_JITTER) -> tuple[FortniteAPI, list[float]]:
    client = mock_sync(script, retry=retry)
    sleeps: list[float] = []
    transport = sync_transport(client)
    transport._sleep = sleeps.append
    transport._random = lambda: 0.5
    return client, sleeps


def async_with(script: Script, retry: RetryConfig | None = NO_JITTER) -> tuple[AsyncFortniteAPI, list[float]]:
    client = mock_async(script, retry=retry)
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    transport = async_transport(client)
    transport._sleep = fake_sleep
    transport._random = lambda: 0.5
    return client, sleeps


# --- RetryConfig ------------------------------------------------------------------------------


def test_retry_config_defaults_and_validation() -> None:
    config = RetryConfig()
    assert (config.max_retries, config.backoff_base, config.backoff_max, config.jitter) == (2, 0.5, 8.0, True)
    with pytest.raises(ValueError, match="max_retries"):
        RetryConfig(max_retries=-1)
    with pytest.raises(ValueError, match="backoff_base"):
        RetryConfig(backoff_base=-0.1)


def test_retry_config_delay() -> None:
    assert [NO_JITTER.delay(n, None, lambda: 0.0) for n in range(4)] == [1.0, 2.0, 4.0, 5.0]
    jittered = RetryConfig(backoff_base=2.0, jitter=True)
    assert jittered.delay(0, None, lambda: 0.0) == 1.0
    assert jittered.delay(0, None, lambda: 1.0) == 2.0
    assert jittered.delay(1, None, lambda: 0.5) == 3.0
    assert NO_JITTER.delay(0, 3.0, lambda: 0.0) == 3.0
    assert NO_JITTER.delay(0, 999.0, lambda: 0.0) == 10.0
    assert 1.0 <= jittered.delay(0, None) <= 2.0  # default random.random


def test_retry_config_next_delay() -> None:
    cfg = NO_JITTER
    assert cfg.next_delay(0, retryable=False, status=500) is None
    assert cfg.next_delay(3, retryable=True, status=500) is None
    assert cfg.next_delay(0, retryable=True, status=404) is None
    assert cfg.next_delay(0, retryable=True, status=None) == 1.0
    assert cfg.next_delay(1, retryable=True, status=503) == 2.0
    assert cfg.next_delay(0, retryable=True, status=429, headers={"Retry-After": "4"}) == 4.0
    assert cfg.next_delay(0, retryable=True, status=429, headers={"retry-after": "9999"}) == 10.0
    jittered = RetryConfig(backoff_base=2.0)
    assert jittered.next_delay(0, retryable=True, status=None, random=lambda: 0.0) == 1.0


# --- sync -------------------------------------------------------------------------------------


def test_retries_are_disabled_by_default() -> None:
    script = Script(status(503))
    client, _ = sync_with(script, retry=None)
    with pytest.raises(ServerError):
        client.shop.get_current()
    assert len(script.requests) == 1
    client.close()


def test_retry_on_5xx_then_success() -> None:
    script = Script(status(503), status(500), ok({"x": 1}))
    client, sleeps = sync_with(script)
    assert client.weapons.get_lootpool() == {"x": 1}
    assert sleeps == [1.0, 2.0]
    assert len(script.requests) == 3
    client.close()


def test_retry_honours_retry_after_with_cap() -> None:
    script = Script(status(429, {"Retry-After": "3"}), status(429, {"Retry-After": "600"}), ok())
    client, sleeps = sync_with(script)
    client.health()
    assert sleeps == [3.0, 10.0]
    client.close()


def test_retry_uses_jitter_from_injected_random() -> None:
    script = Script(status(502), ok())
    client, sleeps = sync_with(script, RetryConfig(max_retries=1, backoff_base=4.0))
    client.health()
    assert sleeps == [3.0]  # 4.0 / 2 + 0.5 * 4.0 / 2
    client.close()


def test_retry_exhausted_raises_last_error() -> None:
    script = Script(status(503), status(503), status(503), status(429, {"Retry-After": "1"}))
    client, sleeps = sync_with(script)
    with pytest.raises(RateLimitError) as info:
        client.shop.get_current()
    assert info.value.retry_after == 1.0
    assert sleeps == [1.0, 2.0, 4.0]
    assert len(script.requests) == 4
    client.close()


def test_client_errors_are_not_retried() -> None:
    script = Script(status(400))
    client, sleeps = sync_with(script)
    with pytest.raises(ClientError):
        client.shop.get_current()
    assert sleeps == []
    client.close()


def test_connection_errors_are_retried() -> None:
    script = Script(httpx.ConnectError, httpx.ReadTimeout, ok({"ok": 1}))
    client, sleeps = sync_with(script)
    assert client.account.get_by_id("a") == {"ok": 1}
    assert sleeps == [1.0, 2.0]
    client.close()


def test_connection_errors_exhausted() -> None:
    script = Script(httpx.ConnectTimeout, httpx.ConnectTimeout)
    client, sleeps = sync_with(script, RetryConfig(max_retries=1, jitter=False))
    with pytest.raises(APITimeoutError):
        client.shop.get_current()
    assert sleeps == [0.5]
    client.close()


def test_non_idempotent_post_is_not_retried() -> None:
    for call in (
        lambda c: c.custom_match.initiate({"custom_key": "k"}),
        lambda c: c.oauth.refresh_token({"refreshToken": "r"}),
        lambda c: c.parsing.parse_replay(b"x"),
    ):
        script = Script(status(503))
        client, sleeps = sync_with(script)
        with pytest.raises(ServerError):
            call(client)
        assert sleeps == []
        client.close()


def test_non_idempotent_post_connection_error_is_not_retried() -> None:
    script = Script(httpx.ConnectError)
    client, sleeps = sync_with(script)
    with pytest.raises(APIConnectionError):
        client.custom_match.initiate({"custom_key": "k"})
    assert sleeps == []
    client.close()


@pytest.mark.parametrize(
    "call",
    [
        lambda c: c.account.bulk_external_display_names({"displayNames": ["a"]}),
        lambda c: c.account.bulk_external_ids({"ids": ["a"]}),
        lambda c: c.stats.get_bulk({"accountIds": ["a"], "stats": ["s"]}),
        lambda c: c.profile.bulk_track_progress(["a"]),
        lambda c: c.profile.get_leaderboard("HazelnutSpread", account_id="a"),
        lambda c: c.replays.download("m"),
        lambda c: c.map.get_image(),
    ],
)
def test_read_only_requests_are_retried(call: Any) -> None:
    script = Script(status(503), ok())
    client, sleeps = sync_with(script)
    call(client)
    assert sleeps == [1.0]
    assert script.requests[0].method == script.requests[1].method
    assert script.requests[0].content == script.requests[1].content
    client.close()


# --- async ------------------------------------------------------------------------------------


async def test_async_retry_then_success() -> None:
    script = Script(status(504), httpx.ConnectError, ok([1]))
    client, sleeps = async_with(script)
    assert await client.stats.get_bulk({"accountIds": ["a"], "stats": ["s"]}) == [1]
    assert sleeps == [1.0, 2.0]
    await client.close()


async def test_async_retry_exhausted_and_not_retryable() -> None:
    script = Script(httpx.ConnectError, httpx.ConnectError)
    client, sleeps = async_with(script, RetryConfig(max_retries=1, jitter=False))
    with pytest.raises(APIConnectionError):
        await client.shop.get_current()
    assert sleeps == [0.5]
    await client.close()

    script = Script(status(500))
    client, sleeps = async_with(script)
    with pytest.raises(ServerError):
        await client.fn.update_privacy("acc", {"optOutOfPublicLeaderboards": True})
    assert sleeps == []
    await client.close()


async def test_async_default_sleep_is_used() -> None:
    script = Script(status(503), ok())
    client = mock_async(script, retry=RetryConfig(max_retries=1, backoff_base=0.0))
    assert await client.health() == {}
    assert len(script.requests) == 2
    await client.close()


def test_sync_default_sleep_is_used() -> None:
    script = Script(status(503), ok())
    client = mock_sync(script, retry=RetryConfig(max_retries=1, backoff_base=0.0))
    assert client.health() == {}
    assert len(script.requests) == 2
    client.close()
