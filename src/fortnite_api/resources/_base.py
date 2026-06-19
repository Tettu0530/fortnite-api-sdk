from __future__ import annotations


class Resource:
    def __init__(self, transport: object) -> None:
        self._t = transport
