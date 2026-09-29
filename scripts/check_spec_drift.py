"""Detect drift between the live API's OpenAPI document and openapi/swagger.json.

Downloads the published spec, compares it with the committed copy and prints a Markdown
summary of added / removed / changed operations and schemas (suitable for an issue body).

Names taken from the live spec (paths, schema, parameter and property names, ``info.version``)
are untrusted: :func:`_safe` escapes control characters and backticks so they cannot inject
GitHub Actions workflow commands into logs or break out of Markdown code spans / fences.

Exit codes: 0 = identical, 1 = drift detected, 2 = the live spec could not be fetched or parsed.

Usage::

    uv run python scripts/check_spec_drift.py [--output drift.md] [--save new-swagger.json]
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = ROOT / "openapi" / "swagger.json"
DEFAULT_URL = "https://prod.api-fortnite.com/swagger/v1/swagger.json"
HTTP_VERBS = ("get", "post", "put", "patch", "delete", "head", "options")
# Fields of an operation that are compared individually (anything else is reported as "other").
OPERATION_FIELDS = ("summary", "description", "deprecated", "parameters", "requestBody", "responses", "tags")

Json = dict[str, Any]


class FetchError(Exception):
    """The live spec could not be downloaded or parsed."""


@dataclass
class Section:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: dict[str, list[str]] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.added or self.removed or self.changed)


@dataclass
class Drift:
    operations: Section = field(default_factory=Section)
    schemas: Section = field(default_factory=Section)
    other: list[str] = field(default_factory=list)
    local_version: str = "?"
    remote_version: str = "?"

    def __bool__(self) -> bool:
        return bool(self.operations or self.schemas or self.other)


def fetch_spec(url: str, timeout: float = 30.0) -> Json:
    request = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "fortnite-api-sdk-spec-drift"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw: bytes = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"could not download {url}: {exc}") from exc
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise FetchError(f"{url} did not return JSON: {exc}") from exc
    if not isinstance(data, dict) or "paths" not in data:
        raise FetchError(f"{url} did not return an OpenAPI document")
    return data


def _safe(value: object) -> str:
    """Render an untrusted name on one line without control characters or backticks."""
    out: list[str] = []
    for char in str(value):
        if char == "`":
            out.append("'")
        elif unicodedata.category(char) in ("Cc", "Cf", "Zl", "Zp"):
            out.append(f"\\u{ord(char):04x}")
        else:
            out.append(char)
    return "".join(out)


def operations(spec: Json) -> dict[str, Json]:
    return {
        _safe(f"{verb.upper()} {path}"): op
        for path, methods in (spec.get("paths") or {}).items()
        for verb, op in methods.items()
        if verb in HTTP_VERBS
    }


def schemas(spec: Json) -> dict[str, Json]:
    raw: dict[str, Json] = (spec.get("components") or {}).get("schemas") or {}
    return {_safe(name): schema for name, schema in raw.items()}


def _param_key(param: Json) -> str:
    return _safe(f"{param.get('in', '?')}:{param.get('name', param.get('$ref', '?'))}")


def diff_operation(old: Json, new: Json) -> list[str]:
    notes: list[str] = []
    old_params = {_param_key(p): p for p in old.get("parameters", [])}
    new_params = {_param_key(p): p for p in new.get("parameters", [])}
    notes += [f"parameter `{k}` added" for k in sorted(new_params.keys() - old_params.keys())]
    notes += [f"parameter `{k}` removed" for k in sorted(old_params.keys() - new_params.keys())]
    notes += [
        f"parameter `{k}` changed"
        for k in sorted(old_params.keys() & new_params.keys())
        if old_params[k] != new_params[k]
    ]
    if bool(old.get("deprecated")) != bool(new.get("deprecated")):
        notes.append("now deprecated" if new.get("deprecated") else "no longer deprecated")
    for key in ("summary", "description", "requestBody", "responses", "tags"):
        if old.get(key) != new.get(key):
            notes.append(f"`{key}` changed")
    other = {k for k in old.keys() | new.keys() if k not in OPERATION_FIELDS and old.get(k) != new.get(k)}
    notes += [f"`{_safe(k)}` changed" for k in sorted(other)]
    return notes


def diff_schema(old: Json, new: Json) -> list[str]:
    notes: list[str] = []
    old_props: Json = {_safe(k): v for k, v in (old.get("properties") or {}).items()}
    new_props: Json = {_safe(k): v for k, v in (new.get("properties") or {}).items()}
    notes += [f"property `{k}` added" for k in sorted(new_props.keys() - old_props.keys())]
    notes += [f"property `{k}` removed" for k in sorted(old_props.keys() - new_props.keys())]
    notes += [
        f"property `{k}` changed" for k in sorted(old_props.keys() & new_props.keys()) if old_props[k] != new_props[k]
    ]
    other = {k for k in old.keys() | new.keys() if k != "properties" and old.get(k) != new.get(k)}
    notes += [f"`{_safe(k)}` changed" for k in sorted(other)]
    return notes


def diff_section(old: dict[str, Json], new: dict[str, Json], differ: Callable[[Json, Json], list[str]]) -> Section:
    section = Section(added=sorted(new.keys() - old.keys()), removed=sorted(old.keys() - new.keys()))
    for key in sorted(old.keys() & new.keys()):
        if old[key] != new[key]:
            section.changed[key] = differ(old[key], new[key]) or ["changed"]
    return section


def compare(local: Json, remote: Json) -> Drift:
    drift = Drift(
        operations=diff_section(operations(local), operations(remote), diff_operation),
        schemas=diff_section(schemas(local), schemas(remote), diff_schema),
        local_version=_safe((local.get("info") or {}).get("version", "?")),
        remote_version=_safe((remote.get("info") or {}).get("version", "?")),
    )
    for key in sorted(local.keys() | remote.keys()):
        if key in ("paths", "components"):
            continue
        if local.get(key) != remote.get(key):
            drift.other.append(f"top-level `{_safe(key)}` changed")
    local_components = {k: v for k, v in (local.get("components") or {}).items() if k != "schemas"}
    remote_components = {k: v for k, v in (remote.get("components") or {}).items() if k != "schemas"}
    for key in sorted(local_components.keys() | remote_components.keys()):
        if local_components.get(key) != remote_components.get(key):
            drift.other.append(f"`components.{_safe(key)}` changed")
    return drift


def _render_section(title: str, section: Section) -> list[str]:
    lines = [f"### {title}", ""]
    if not section:
        return [*lines, "No changes.", ""]
    lines.append(f"{len(section.added)} added, {len(section.removed)} removed, {len(section.changed)} changed.")
    lines.append("")
    if section.added:
        lines += ["**Added**", "", *(f"- `{k}`" for k in section.added), ""]
    if section.removed:
        lines += ["**Removed**", "", *(f"- `{k}`" for k in section.removed), ""]
    if section.changed:
        lines += ["**Changed**", ""]
        lines += [f"- `{k}`: {'; '.join(notes)}" for k, notes in section.changed.items()]
        lines.append("")
    return lines


def render(drift: Drift, url: str, spec_path: Path) -> str:
    try:
        shown_path = spec_path.resolve().relative_to(ROOT)
    except ValueError:
        shown_path = spec_path
    lines = ["## OpenAPI spec drift", ""]
    if not drift:
        return "\n".join([*lines, f"`{shown_path}` matches {url}. No drift detected.", ""])
    lines += [
        f"The live spec at {url} differs from the committed `{shown_path}`.",
        "",
        f"- Committed `info.version`: `{drift.local_version}`",
        f"- Live `info.version`: `{drift.remote_version}`",
        "",
        *_render_section("Operations", drift.operations),
        *_render_section("Schemas", drift.schemas),
    ]
    if drift.other:
        lines += ["### Other", "", *(f"- {note}" for note in drift.other), ""]
    lines += [
        "### Next steps",
        "",
        "1. Download the new spec into `openapi/swagger.json`.",
        "2. Run `uv run python scripts/generate.py` (update the endpoint table for new operations).",
        "3. Run `uv run python scripts/check_spec_coverage.py` and the test suite.",
        "4. Update the README where relevant. See `docs/TESTING.md` for details.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare the live OpenAPI spec with openapi/swagger.json.")
    parser.add_argument("--url", default=DEFAULT_URL, help="live spec URL (default: %(default)s)")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="committed spec (default: %(default)s)")
    parser.add_argument("--output", type=Path, help="also write the Markdown summary to this file")
    parser.add_argument("--save", type=Path, help="write the downloaded live spec to this file")
    parser.add_argument("--timeout", type=float, default=30.0, help="network timeout in seconds")
    args = parser.parse_args(argv)

    local: Json = json.loads(args.spec.read_text(encoding="utf-8"))
    try:
        remote = fetch_spec(args.url, args.timeout)
    except FetchError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.save:
        args.save.write_text(json.dumps(remote, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    drift = compare(local, remote)
    summary = render(drift, args.url, args.spec)
    print(summary)
    if args.output:
        args.output.write_text(summary, encoding="utf-8")
    return 1 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
