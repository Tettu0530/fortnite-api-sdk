"""Verify that the generated SDK covers every operation in openapi/swagger.json.

Every public sync and async resource method is called once through an ``httpx.MockTransport``
with placeholder arguments, and the recorded request is matched back to a spec operation.
The script then checks, per operation:

* exactly one SDK method maps to it (plus client-level ``health`` / ``health_version``),
* every path and query parameter is exposed and every query parameter is actually sent,
* no unknown query parameters are sent,
* deprecated operations (and only those) emit a ``DeprecationWarning``,
* the async method sends the same request as the sync one,
* JSON request bodies are exposed and typed with the spec's schema,
* responses with a ``$ref`` schema are typed (not ``Any``).

Run with ``uv run python scripts/check_spec_coverage.py``. Exits 1 when any gap is found.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import re
import sys
import warnings
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from fortnite_api import AsyncFortniteAPI, FortniteAPI
from fortnite_api.resources._base import Resource

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = ROOT / "openapi" / "swagger.json"
HTTP_VERBS = ("get", "post", "put", "patch", "delete")

# SDK methods that intentionally call endpoints which are live but not (yet) in the spec.
KNOWN_EXTRAS = frozenset(
    {
        "parsing.parse_multiple",
        "parsing.parse_multiple_loot",
        "parsing.parse_multiple_map",
        "parsing.parse_multiple_stats",
    }
)
# Operations served by methods on the client itself rather than on a resource.
CLIENT_LEVEL = {("GET", "/health"): "client.health", ("GET", "/health/version"): "client.health_version"}
# Keyword-only parameters that are not spec parameters.
NON_SPEC_KWARGS = frozenset({"fortnite_token", "filename", "filenames", "body"})

Operation = dict[str, Any]
OpKey = tuple[str, str]  # (HTTP method, path template)


@dataclass
class Call:
    """One recorded SDK method invocation."""

    request: httpx.Request
    signature: inspect.Signature
    warnings: list[str]


@dataclass
class Report:
    operations: int = 0
    sync_methods: int = 0
    async_methods: int = 0
    extras: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"spec operations:      {self.operations}",
            f"sdk methods (sync):   {self.sync_methods} (+ client-level {', '.join(CLIENT_LEVEL.values())})",
            f"sdk methods (async):  {self.async_methods}",
            f"SDK-only extras:      {len(self.extras)} (allow-listed in KNOWN_EXTRAS)",
            *(f"    {x}" for x in self.extras),
            f"GAPS: {len(self.gaps)}",
            *(f"    {g}" for g in self.gaps),
        ]
        return "\n".join(lines)


def snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def load_operations(spec_path: Path) -> dict[OpKey, Operation]:
    spec: dict[str, Any] = json.loads(spec_path.read_text(encoding="utf-8"))
    return {
        (verb.upper(), path): op
        for path, methods in spec["paths"].items()
        for verb, op in methods.items()
        if verb in HTTP_VERBS
    }


# --------------------------------------------------------------------------- recording


def positional_dummy(param: inspect.Parameter) -> Any:
    ann = str(param.annotation)
    if "list[FileInput]" in ann:
        return [b"x"]
    if "FileInput" in ann:
        return b"x"
    if ann.startswith("list"):
        return ["a", "b"]
    if ann == "int":
        return 7
    if ann == "float":
        return 1.5
    if ann == "bool":
        return True
    if "dict" in ann or ann == "Any":
        return {}
    return f"P_{param.name}"


def keyword_dummy(param: inspect.Parameter) -> Any:
    ann = str(param.annotation)
    if ann.startswith("list"):
        return ["k"]
    if ann.startswith("int"):
        return 1
    if ann.startswith("bool"):
        return True
    if ann.startswith("float"):
        return 1.5
    return "v"


def call_args(signature: inspect.Signature) -> tuple[list[Any], dict[str, Any]]:
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    for param in signature.parameters.values():
        if param.kind is param.POSITIONAL_OR_KEYWORD:
            args.append(positional_dummy(param))
        elif param.kind is param.KEYWORD_ONLY and param.name not in NON_SPEC_KWARGS:
            kwargs[param.name] = keyword_dummy(param)
    return args, kwargs


def public_methods(client: FortniteAPI | AsyncFortniteAPI) -> Iterator[tuple[str, Callable[..., Any]]]:
    for attr, resource in sorted(vars(client).items()):
        if attr.startswith("_") or not isinstance(resource, Resource):
            continue
        for name, method in inspect.getmembers(resource, inspect.ismethod):
            if not name.startswith("_"):
                yield f"{attr}.{name}", method


class _Recorder:
    def __init__(self) -> None:
        self.request: httpx.Request | None = None

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        return httpx.Response(200, json={})

    def take(self) -> httpx.Request | None:
        """Return the request recorded since the last call and reset."""
        request, self.request = self.request, None
        return request


def _invoke(name: str, method: Callable[..., Any], recorder: _Recorder, gaps: list[str]) -> Call | None:
    signature = inspect.signature(method)
    args, kwargs = call_args(signature)
    recorder.take()
    error: Exception | None = None
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            method(*args, **kwargs)
        except Exception as exc:  # the canned {} may not validate; the request is what matters
            error = exc
    return _finish(name, recorder.take(), signature=signature, caught=caught, error=error, gaps=gaps)


def _finish(
    name: str,
    request: httpx.Request | None,
    *,
    signature: inspect.Signature,
    caught: list[warnings.WarningMessage],
    error: Exception | None,
    gaps: list[str],
) -> Call | None:
    if request is None:
        gaps.append(f"{name}: no request was sent" + (f" ({error!r})" if error else ""))
        return None
    return Call(request, signature, [w.category.__name__ for w in caught])


def record_sync(gaps: list[str]) -> dict[str, Call]:
    recorder = _Recorder()
    client = FortniteAPI("key")
    client._t._client.close()
    client._t._client = httpx.Client(transport=httpx.MockTransport(recorder))
    calls: dict[str, Call] = {}
    with client:
        for name, method in public_methods(client):
            call = _invoke(name, method, recorder, gaps)
            if call is not None:
                calls[name] = call
    return calls


async def _record_async(gaps: list[str]) -> dict[str, Call]:
    recorder = _Recorder()
    client = AsyncFortniteAPI("key")
    await client._t._client.aclose()
    client._t._client = httpx.AsyncClient(transport=httpx.MockTransport(recorder))
    calls: dict[str, Call] = {}
    async with client:
        for name, method in public_methods(client):
            signature = inspect.signature(method)
            args, kwargs = call_args(signature)
            recorder.take()
            error: Exception | None = None
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    await method(*args, **kwargs)
                except Exception as exc:  # see _invoke
                    error = exc
            call = _finish(
                f"{name} (async)", recorder.take(), signature=signature, caught=caught, error=error, gaps=gaps
            )
            if call is not None:
                calls[name] = call
    return calls


def record_async(gaps: list[str]) -> dict[str, Call]:
    # A private loop (rather than asyncio.run) leaves the thread's current event loop untouched,
    # so this also behaves when called from a test session that manages its own loops.
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_record_async(gaps))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


# --------------------------------------------------------------------------- checks


def match_operation(ops: dict[OpKey, Operation], method: str, url_path: str) -> OpKey | None:
    """The most specific spec template (fewest placeholders) matching the request."""
    candidates = [
        (verb, template)
        for verb, template in ops
        if verb == method and re.fullmatch(re.sub(r"\{[^}]+\}", "[^/]+", template), url_path)
    ]
    candidates.sort(key=lambda key: key[1].count("{"))
    return candidates[0] if candidates else None


def check_params(name: str, op: Operation, call: Call, gaps: list[str]) -> None:
    params: list[dict[str, Any]] = op.get("parameters", [])
    sent = dict(call.request.url.params)
    exposed = call.signature.parameters
    spec_query = {p["name"] for p in params if p.get("in") == "query"}
    for p in params:
        pname = p["name"]
        if p.get("in") == "query" and pname not in sent:
            reason = "not sent" if snake(pname) in exposed else "not exposed"
            gaps.append(f"{name}: query param {pname} {reason}")
        elif p.get("in") == "path" and snake(pname) not in exposed:
            gaps.append(f"{name}: path param {pname} not exposed")
    gaps.extend(f"{name}: sends unknown query param {q}" for q in sent if q not in spec_query)


def check_body(name: str, op: Operation, call: Call, gaps: list[str]) -> None:
    body = op.get("requestBody")
    content: dict[str, Any] = (body or {}).get("content", {})
    if not body or "multipart/form-data" in content:
        return
    if "body" not in call.signature.parameters:
        gaps.append(f"{name}: requestBody not exposed")
        return
    schema: dict[str, Any] = content.get("application/json", {}).get("schema") or {}
    ref = schema.get("$ref")
    if ref and str(ref).split("/")[-1] not in str(call.signature.parameters["body"].annotation):
        gaps.append(f"{name}: body not typed as {ref}")


def check_response(name: str, op: Operation, call: Call, gaps: list[str]) -> None:
    content = op.get("responses", {}).get("200", {}).get("content", {})
    schema = (content.get("application/json") or {}).get("schema")
    ret = str(call.signature.return_annotation)
    if schema and "$ref" in json.dumps(schema) and ret == "Any":
        gaps.append(f"{name}: returns Any but the spec has schema {json.dumps(schema)}")
    if not schema and ret not in ("Any", "bytes", "str | None"):
        gaps.append(f"{name}: typed {ret} without a spec schema")


def check(spec_path: Path = DEFAULT_SPEC) -> Report:
    ops = load_operations(spec_path)
    report = Report(operations=len(ops))
    gaps = report.gaps
    sync_calls = record_sync(gaps)
    async_calls = record_async(gaps)
    report.sync_methods, report.async_methods = len(sync_calls), len(async_calls)

    if set(sync_calls) != set(async_calls):
        gaps.append(f"sync/async method set mismatch: {sorted(set(sync_calls) ^ set(async_calls))}")

    mapped: dict[OpKey, list[str]] = defaultdict(list)
    for client_key, method_name in CLIENT_LEVEL.items():
        attr = method_name.split(".", 1)[1]
        if callable(getattr(FortniteAPI, attr, None)) and callable(getattr(AsyncFortniteAPI, attr, None)):
            mapped[client_key].append(method_name)

    for name, call in sorted(sync_calls.items()):
        key = match_operation(ops, call.request.method, call.request.url.path)
        if key is None:
            extra = f"{name} -> {call.request.method} {call.request.url.path}"
            if name in KNOWN_EXTRAS:
                report.extras.append(extra)
            else:
                gaps.append(f"{extra}: not in the spec (add to KNOWN_EXTRAS if intentional)")
            continue
        mapped[key].append(name)
        op = ops[key]
        check_params(name, op, call, gaps)
        check_body(name, op, call, gaps)
        check_response(name, op, call, gaps)

        deprecated = bool(op.get("deprecated"))
        if deprecated != ("DeprecationWarning" in call.warnings):
            gaps.append(f"{name}: deprecated={deprecated} but warnings={call.warnings}")
        acall = async_calls.get(name)
        if acall is not None:
            if deprecated != ("DeprecationWarning" in acall.warnings):
                gaps.append(f"{name} (async): deprecated={deprecated} but warnings={acall.warnings}")
            if str(acall.request.url) != str(call.request.url) or acall.request.method != call.request.method:
                gaps.append(f"{name}: async request differs from sync")

    for key in sorted(ops):
        names = mapped.get(key, [])
        if len(names) != 1:
            gaps.append(f"{key[0]} {key[1]}: mapped to {len(names)} methods {names}")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC, help="OpenAPI document (default: %(default)s)")
    args = parser.parse_args(argv)
    report = check(args.spec)
    print(report.render())
    return 1 if report.gaps else 0


if __name__ == "__main__":
    sys.exit(main())
