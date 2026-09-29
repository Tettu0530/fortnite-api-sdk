from __future__ import annotations

from typing import Any

from .._transport import FileInput
from ._base import Resource

class ParsingResource(Resource):
    def parse_replay(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and extract match statistics. Subject to per-plan parsing quota
        limits.

        ``POST /api/v1/parsing``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing", payload, response_type=None)

    def parse_stats(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return only basic match statistics. Significantly faster
        than full parsing — skips movement, zones, and kill feed. Returns: name, replayId, version, stats
        (elims, damage, accuracy, placement, assists, damageTaken, damageStructures, matsFarm, matsUsed,
        totalPlayers).

        ``POST /api/v1/parsing/stats``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/stats", payload, response_type=None)

    def parse_map(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return full map context. Returns: bus flight path + drop
        window, all storm circles with timing, supply drops, llamas, reboot vans.

        ``POST /api/v1/parsing/map``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/map", payload, response_type=None)

    def parse_loot(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return ground loot data. Returns all items that were on the
        ground near the player: position, item ID, picked-up status and time. Times are on the replay world
        clock — subtract referenceTime, NOT matchStartTime (a heuristic kept only for existing consumers).
        Field reference: https://api-fortnite.com/docs/replay-parser

        ``POST /api/v1/parsing/loot``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/loot", payload, response_type=None)

    def parse_timeline(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return a time-ordered match timeline. Returns all events
        with t in seconds since referenceTime (match start): kills, knocks, own death, damage dealt, damage
        taken, healed, pickups. Requires full parse mode — slower than /parsing/stats but richer than
        /parsing.

        ``POST /api/v1/parsing/timeline``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/timeline", payload, response_type=None)

    def parse_zones(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return storm zone data. Returns all safe zone phases with
        circle positions, timing, damage per tick, and phase count.

        ``POST /api/v1/parsing/zones``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/zones", payload, response_type=None)

    def parse_lobby(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the full player lobby. Returns all players with
        placement, kills, death info, cosmetics, and team data.

        ``POST /api/v1/parsing/lobby``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/lobby", payload, response_type=None)

    def parse_broadcast(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the complete broadcast payload. Combines all data:
        header, stats, full player lobby, storm zones, map objects, ground loot, and timeline events.
        Requires full parse mode — equivalent to calling all endpoints in one request.

        ``POST /api/v1/parsing/broadcast``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return self._t.request_multipart("/parsing/broadcast", payload, response_type=None)

    def parse_multiple(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple

        ``POST /api/v1/parsing/multiple``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple", payload, response_type=None)

    def parse_multiple_stats(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/stats

        ``POST /api/v1/parsing/multiple/stats``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/stats", payload, response_type=None)

    def parse_multiple_map(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/map

        ``POST /api/v1/parsing/multiple/map``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/map", payload, response_type=None)

    def parse_multiple_loot(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/loot

        ``POST /api/v1/parsing/multiple/loot``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return self._t.request_multipart("/parsing/multiple/loot", payload, response_type=None)


class AsyncParsingResource(Resource):
    async def parse_replay(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and extract match statistics. Subject to per-plan parsing quota
        limits.

        ``POST /api/v1/parsing``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing", payload, response_type=None)

    async def parse_stats(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return only basic match statistics. Significantly faster
        than full parsing — skips movement, zones, and kill feed. Returns: name, replayId, version, stats
        (elims, damage, accuracy, placement, assists, damageTaken, damageStructures, matsFarm, matsUsed,
        totalPlayers).

        ``POST /api/v1/parsing/stats``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/stats", payload, response_type=None)

    async def parse_map(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return full map context. Returns: bus flight path + drop
        window, all storm circles with timing, supply drops, llamas, reboot vans.

        ``POST /api/v1/parsing/map``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/map", payload, response_type=None)

    async def parse_loot(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return ground loot data. Returns all items that were on the
        ground near the player: position, item ID, picked-up status and time. Times are on the replay world
        clock — subtract referenceTime, NOT matchStartTime (a heuristic kept only for existing consumers).
        Field reference: https://api-fortnite.com/docs/replay-parser

        ``POST /api/v1/parsing/loot``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/loot", payload, response_type=None)

    async def parse_timeline(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return a time-ordered match timeline. Returns all events
        with t in seconds since referenceTime (match start): kills, knocks, own death, damage dealt, damage
        taken, healed, pickups. Requires full parse mode — slower than /parsing/stats but richer than
        /parsing.

        ``POST /api/v1/parsing/timeline``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/timeline", payload, response_type=None)

    async def parse_zones(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return storm zone data. Returns all safe zone phases with
        circle positions, timing, damage per tick, and phase count.

        ``POST /api/v1/parsing/zones``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/zones", payload, response_type=None)

    async def parse_lobby(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the full player lobby. Returns all players with
        placement, kills, death info, cosmetics, and team data.

        ``POST /api/v1/parsing/lobby``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/lobby", payload, response_type=None)

    async def parse_broadcast(self, file: FileInput, *, filename: str | None = None) -> Any:
        """Parse a single Fortnite .replay file and return the complete broadcast payload. Combines all data:
        header, stats, full player lobby, storm zones, map objects, ground loot, and timeline events.
        Requires full parse mode — equivalent to calling all endpoints in one request.

        ``POST /api/v1/parsing/broadcast``
        """
        payload = {"file": self._t._file_tuple(file, filename)}
        return await self._t.request_multipart("/parsing/broadcast", payload, response_type=None)

    async def parse_multiple(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple

        ``POST /api/v1/parsing/multiple``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple", payload, response_type=None)

    async def parse_multiple_stats(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/stats

        ``POST /api/v1/parsing/multiple/stats``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/stats", payload, response_type=None)

    async def parse_multiple_map(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/map

        ``POST /api/v1/parsing/multiple/map``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/map", payload, response_type=None)

    async def parse_multiple_loot(self, files: list[FileInput], *, filenames: list[str] | None = None) -> Any:
        """POST /api/v1/parsing/multiple/loot

        ``POST /api/v1/parsing/multiple/loot``
        """
        payload = [
            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))
            for i, f in enumerate(files)
        ]
        return await self._t.request_multipart("/parsing/multiple/loot", payload, response_type=None)
