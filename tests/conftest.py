"""Shared pytest configuration."""

from __future__ import annotations

from collections.abc import Generator

import pytest

from fortnite_api.errors import PlanRequiredError


def pytest_configure(config: pytest.Config) -> None:
    # `pytest -m live` only exercises a thin slice of the package against the real API, so the
    # coverage threshold (meant for the offline suite) is not enforced for it. pytest-cov keeps
    # its own copy of the options, hence the plugin lookup.
    markexpr = str(config.getoption("markexpr", default="") or "")
    if "live" not in markexpr or "not live" in markexpr:
        return
    cov_plugin = config.pluginmanager.get_plugin("_cov")
    options = getattr(cov_plugin, "options", None)
    if options is not None and getattr(options, "cov_fail_under", None):
        options.cov_fail_under = 0


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, object, object]:
    # API keys only unlock the endpoints of their plan. For live tests, a 403 "not included in
    # your plan" says nothing about the SDK, so it is reported as a skip instead of a failure.
    try:
        return (yield)
    except PlanRequiredError as exc:
        if item.get_closest_marker("live") is None:
            raise
        pytest.skip(f"endpoint not included in the API key's plan ({exc})")
