from __future__ import annotations

from typing import Any


class Resource:
    def __init__(self, transport: Any) -> None:
        # SyncTransport for sync resources, AsyncTransport for async ones.
        self._t: Any = transport
