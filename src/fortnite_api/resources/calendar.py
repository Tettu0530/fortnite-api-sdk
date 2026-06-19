from __future__ import annotations

from ..models import SeasonEntryDto
from ._base import Resource

class CalendarResource(Resource):
    def get_season(self, *, fortnite_token: str | None = None) -> SeasonEntryDto:
        """Get the current Fortnite season number and start/end dates."""
        return self._t.request("GET", "/season", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=SeasonEntryDto, is_list=False)


class AsyncCalendarResource(Resource):
    async def get_season(self, *, fortnite_token: str | None = None) -> SeasonEntryDto:
        """Get the current Fortnite season number and start/end dates."""
        return await self._t.request("GET", "/season", "v1",
            params=None, json_body=None, fortnite_token=fortnite_token,
            model=SeasonEntryDto, is_list=False)
