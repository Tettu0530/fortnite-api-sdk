"""Shared pytest configuration."""

from __future__ import annotations

import pytest


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
