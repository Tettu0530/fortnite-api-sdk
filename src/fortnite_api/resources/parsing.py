from __future__ import annotations

from typing import Any

from .._transport import FileInput
from ._base import Resource

class ParsingResource(Resource):
    def parse_replay(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and extract match statistics."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing", payload, model=None, is_list=False)

    def parse_stats(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return only basic match statistics."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/stats", payload, model=None, is_list=False)

    def parse_map(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return full map context."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/map", payload, model=None, is_list=False)

    def parse_loot(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return ground loot data."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/loot", payload, model=None, is_list=False)

    def parse_timeline(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return a time-ordered match timeline."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/timeline", payload, model=None, is_list=False)

    def parse_zones(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return storm zone data."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/zones", payload, model=None, is_list=False)

    def parse_lobby(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the full player lobby."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/lobby", payload, model=None, is_list=False)

    def parse_broadcast(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the complete broadcast payload."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/broadcast", payload, model=None, is_list=False)

    def parse_multiple(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple", payload, model=None, is_list=False)

    def parse_multiple_stats(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/stats", payload, model=None, is_list=False)

    def parse_multiple_map(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/map", payload, model=None, is_list=False)

    def parse_multiple_loot(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/loot", payload, model=None, is_list=False)


class AsyncParsingResource(Resource):
    async def parse_replay(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and extract match statistics."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing", payload, model=None, is_list=False)

    async def parse_stats(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return only basic match statistics."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/stats", payload, model=None, is_list=False)

    async def parse_map(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return full map context."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/map", payload, model=None, is_list=False)

    async def parse_loot(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return ground loot data."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/loot", payload, model=None, is_list=False)

    async def parse_timeline(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return a time-ordered match timeline."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/timeline", payload, model=None, is_list=False)

    async def parse_zones(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return storm zone data."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/zones", payload, model=None, is_list=False)

    async def parse_lobby(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the full player lobby."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/lobby", payload, model=None, is_list=False)

    async def parse_broadcast(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the complete broadcast payload."""
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/broadcast", payload, model=None, is_list=False)

    async def parse_multiple(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple", payload, model=None, is_list=False)

    async def parse_multiple_stats(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/stats", payload, model=None, is_list=False)

    async def parse_multiple_map(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/map", payload, model=None, is_list=False)

    async def parse_multiple_loot(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/loot", payload, model=None, is_list=False)
