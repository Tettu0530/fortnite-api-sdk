from __future__ import annotations

from typing import Any


class FortniteAPIError(Exception):
    """Raised when the Fortnite API returns a non-success HTTP status."""

    def __init__(self, message: str, status: int, data: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.data = data

    def __str__(self) -> str:
        return f"[{self.status}] {self.message}"
