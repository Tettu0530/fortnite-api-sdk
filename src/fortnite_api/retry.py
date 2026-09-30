"""Opt-in retry policy for the built-in transports.

Retries are disabled unless a :class:`RetryConfig` is passed to the client (``retry=``). When
enabled they apply only to requests the SDK marks as safe to repeat (``retryable=True``): the
``GET`` endpoints and the read-only bulk ``POST`` lookups. ``GET`` endpoints with a cost or side
effect are **not** retryable: the ``replays.parse*`` endpoints (each attempt consumes parsing
credits) and ``oauth.get_token`` (starts a new device-code flow). Neither are other ``POST``,
``DELETE`` or multipart requests. A request is retried after:

* a 429 or 5xx response (see :func:`fortnite_api.interpret.is_retryable_status`), or
* an :class:`~fortnite_api.errors.APIConnectionError` / :class:`~fortnite_api.errors.APITimeoutError`.

The wait honours ``Retry-After`` (capped at ``max_retry_after``); otherwise it is an exponential
backoff ``min(backoff_max, backoff_base * 2**attempt)`` with optional "equal jitter" (a random
value between half and all of that delay). Once ``max_retries`` retries are used up, the last
error is raised.

Custom transports can reuse the whole decision with :meth:`RetryConfig.next_delay`.
"""

from __future__ import annotations

import random as _random
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from .interpret import get_header, is_retryable_status, parse_retry_after

__all__ = ["RetryConfig"]


@dataclass(frozen=True)
class RetryConfig:
    """Retry settings. ``RetryConfig()`` retries up to twice with 0.5s, 1s... backoff."""

    max_retries: int = 2
    """Retries after the first attempt (``0`` disables retrying)."""
    backoff_base: float = 0.5
    """Delay in seconds before the first retry; doubled for every further retry."""
    backoff_max: float = 8.0
    """Upper bound of the exponential backoff delay, in seconds."""
    jitter: bool = True
    """Randomise backoff delays between 50% and 100% to avoid synchronised retries."""
    max_retry_after: float = 60.0
    """Upper bound, in seconds, for waits requested by a ``Retry-After`` header."""

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.backoff_base < 0 or self.backoff_max < 0 or self.max_retry_after < 0:
            raise ValueError("backoff_base, backoff_max and max_retry_after must be >= 0")

    def delay(self, attempt: int, retry_after: float | None, random: Callable[[], float] = _random.random) -> float:
        """Seconds to wait before retry number ``attempt + 1`` (``attempt`` starts at 0).

        ``retry_after`` (seconds requested by the server) is capped at ``max_retry_after``.
        ``random`` returns a float in ``[0, 1)`` and is only used for jitter.
        """
        if retry_after is not None:
            return min(retry_after, self.max_retry_after)
        backoff = min(self.backoff_max, self.backoff_base * (2.0**attempt))
        if self.jitter:
            return backoff / 2 + random() * backoff / 2
        return backoff

    def next_delay(
        self,
        attempt: int,
        *,
        retryable: bool,
        status: int | None,
        headers: Mapping[str, str] | None = None,
        random: Callable[[], float] = _random.random,
    ) -> float | None:
        """Seconds to wait before retrying, or ``None`` when the request must not be retried.

        This is the complete policy of the built-in transports, for reuse in custom transports:
        ``attempt`` counts the retries already made (0 after the first failure), ``retryable`` is
        the flag the resources pass to ``request()``, ``status`` is the HTTP status of the failed
        response or ``None`` for a connection error / timeout, and ``headers`` the response
        headers (for ``Retry-After``). Only 429 and 5xx responses and network errors are retried.
        """
        if not retryable or attempt >= self.max_retries:
            return None
        retry_after = None
        if status is not None:
            if not is_retryable_status(status):
                return None
            retry_after = parse_retry_after(get_header(headers, "retry-after"))
        return self.delay(attempt, retry_after, random)
