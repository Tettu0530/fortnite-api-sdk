"""Regression tests for model fields whose live responses differ from the spec."""

from __future__ import annotations

from fortnite_api.models import CashPrizeRankDto, EpicEventDto


def test_event_link_accepts_object_and_string() -> None:
    link = {"type": "br:tournament", "code": "tournament_epicgames_s42_psnickeh30_naw"}
    assert EpicEventDto.model_validate({"link": link}).link == link
    assert EpicEventDto.model_validate({"link": "https://example.test"}).link == "https://example.test"


def test_cash_prize_threshold_accepts_fractions() -> None:
    assert CashPrizeRankDto.model_validate({"threshold": 0.5}).threshold == 0.5
    assert CashPrizeRankDto.model_validate({"threshold": 10}).threshold == 10
