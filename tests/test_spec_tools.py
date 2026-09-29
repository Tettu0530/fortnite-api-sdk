"""Tests for the spec maintenance scripts (coverage cross-check and drift detection)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from scripts import check_spec_coverage, check_spec_drift

SPEC_PATH = Path(__file__).resolve().parent.parent / "openapi" / "swagger.json"


@pytest.fixture(scope="module")
def spec() -> dict[str, Any]:
    data: dict[str, Any] = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    return data


def _write(tmp_path: Path, data: dict[str, Any], name: str = "spec.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# --- check_spec_coverage ------------------------------------------------------------------------


def test_generated_sdk_covers_the_spec() -> None:
    """Every spec operation is served by exactly one sync + async method (drives all 146 methods)."""
    report = check_spec_coverage.check(SPEC_PATH)
    assert report.gaps == []
    assert report.operations > 100
    assert report.sync_methods == report.async_methods
    assert len(report.extras) == len(check_spec_coverage.KNOWN_EXTRAS)
    assert "GAPS: 0" in report.render()


def test_coverage_reports_gaps_for_a_changed_spec(tmp_path: Path, spec: dict[str, Any]) -> None:
    mutated = copy.deepcopy(spec)
    mutated["paths"]["/api/v1/brand-new"] = {"get": {"summary": "new"}}
    mutated["paths"]["/api/v1/shop"]["get"]["deprecated"] = True
    mutated["paths"]["/api/v1/shop"]["get"].setdefault("parameters", []).append(
        {"name": "newParam", "in": "query", "schema": {"type": "string"}}
    )
    report = check_spec_coverage.check(_write(tmp_path, mutated))
    joined = "\n".join(report.gaps)
    assert "GET /api/v1/brand-new: mapped to 0 methods" in joined
    assert "shop.get_current: deprecated=True" in joined
    assert "shop.get_current: query param newParam not exposed" in joined


def test_coverage_main_exit_codes(tmp_path: Path, spec: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    assert check_spec_coverage.main(["--spec", str(SPEC_PATH)]) == 0
    mutated = copy.deepcopy(spec)
    mutated["paths"]["/api/v1/brand-new"] = {"get": {}}
    assert check_spec_coverage.main(["--spec", str(_write(tmp_path, mutated))]) == 1
    assert "GAPS: 1" in capsys.readouterr().out


def test_snake_case() -> None:
    assert check_spec_coverage.snake("accountId") == "account_id"
    assert check_spec_coverage.snake("URLValue") == "urlvalue"


# --- check_spec_drift ---------------------------------------------------------------------------


def test_drift_identical(spec: dict[str, Any]) -> None:
    drift = check_spec_drift.compare(spec, copy.deepcopy(spec))
    assert not drift
    assert "No drift detected" in check_spec_drift.render(drift, "http://x", SPEC_PATH)


def test_drift_detects_operation_and_schema_changes(spec: dict[str, Any]) -> None:
    remote = copy.deepcopy(spec)
    remote["paths"]["/api/v9/new"] = {"post": {"summary": "new"}}
    del remote["paths"]["/api/v1/season"]
    shop = remote["paths"]["/api/v1/shop"]["get"]
    shop["deprecated"] = True
    shop["summary"] = "changed"
    shop["parameters"] = [*shop.get("parameters", [])[1:], {"name": "extra", "in": "query"}]
    shop["x-custom"] = 1
    schemas = remote["components"]["schemas"]
    first = next(iter(schemas))
    schemas[first] = {**schemas[first], "properties": {"brandNew": {"type": "string"}}, "nullable": True}
    schemas["NewDto"] = {"type": "object"}
    remote["info"] = {**remote.get("info", {}), "version": "v2"}
    remote.setdefault("components", {})["securitySchemes"] = {"k": {}}

    drift = check_spec_drift.compare(spec, remote)
    assert drift
    assert drift.operations.added == ["POST /api/v9/new"]
    assert drift.operations.removed == ["GET /api/v1/season"]
    notes = drift.operations.changed["GET /api/v1/shop"]
    assert "now deprecated" in notes
    assert "`summary` changed" in notes
    assert "parameter `query:extra` added" in notes
    assert "`x-custom` changed" in notes
    assert drift.schemas.added == ["NewDto"]
    assert "property `brandNew` added" in drift.schemas.changed[first]
    assert "`nullable` changed" in drift.schemas.changed[first]
    assert "top-level `info` changed" in drift.other
    assert "`components.securitySchemes` changed" in drift.other

    markdown = check_spec_drift.render(drift, "http://example/swagger.json", SPEC_PATH)
    assert markdown.startswith("## OpenAPI spec drift")
    assert "`POST /api/v9/new`" in markdown
    assert "### Next steps" in markdown


def test_drift_main_with_file_urls(tmp_path: Path, spec: dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
    local = _write(tmp_path, spec, "local.json")
    same_url = local.as_uri()
    assert check_spec_drift.main(["--spec", str(local), "--url", same_url]) == 0

    remote_data = copy.deepcopy(spec)
    remote_data["paths"]["/api/v9/new"] = {"get": {}}
    remote_url = _write(tmp_path, remote_data, "remote.json").as_uri()
    out, saved = tmp_path / "drift.md", tmp_path / "saved.json"
    code = check_spec_drift.main(
        ["--spec", str(local), "--url", remote_url, "--output", str(out), "--save", str(saved)]
    )
    assert code == 1
    assert "`GET /api/v9/new`" in out.read_text(encoding="utf-8")
    assert json.loads(saved.read_text(encoding="utf-8")) == remote_data
    capsys.readouterr()


@pytest.mark.parametrize("content", [b"not json", b"[1, 2]"])
def test_drift_bad_payload_exits_2(tmp_path: Path, content: bytes, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.json"
    bad.write_bytes(content)
    assert check_spec_drift.main(["--spec", str(SPEC_PATH), "--url", bad.as_uri()]) == 2
    assert "error:" in capsys.readouterr().err


def test_drift_network_error_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = (tmp_path / "missing.json").as_uri()
    assert check_spec_drift.main(["--spec", str(SPEC_PATH), "--url", missing]) == 2
    assert "could not download" in capsys.readouterr().err


def test_drift_escapes_untrusted_names(spec: dict[str, Any]) -> None:
    remote = copy.deepcopy(spec)
    hostile = "/x\n::stop-commands::tok\n```\n[phish](https://evil.example)\u2028"
    remote["paths"][hostile] = {"get": {"responses": {}}}
    schemas = remote.setdefault("components", {}).setdefault("schemas", {})
    schemas["Evil\r\n::error::x`"] = {"type": "object"}
    remote["info"] = {**remote.get("info", {}), "version": "1\n::warning::`v`"}
    drift = check_spec_drift.compare(spec, remote)
    markdown = check_spec_drift.render(drift, "https://example/swagger.json", SPEC_PATH)
    assert "```" not in markdown
    assert not any(line.startswith("::") for line in markdown.splitlines())
    assert "\\u000a::stop-commands::tok" in markdown
    assert "\\u2028" in markdown
    assert "Evil\\u000d\\u000a::error::x'" in markdown
    assert check_spec_drift._safe("a`b\tc") == "a'b\\u0009c"
