"""Code generator for the Fortnite API SDK.

Reads openapi/swagger.json and a declarative endpoint table, then emits
src/fortnite_api/models.py, resources/*.py and client.py for sync + async.
Run with: uv run python scripts/generate.py
"""

from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "src" / "fortnite_api"
SWAGGER = json.loads((ROOT / "openapi" / "swagger.json").read_text())

def snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and not name[i - 1].isupper():
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


# --------------------------------------------------------------------------- models

PY_PRIMITIVE = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}


def model_type(schema: dict) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    t = schema.get("type")
    if t == "array":
        return f"list[{model_type(schema.get('items', {}))}]"
    if t in PY_PRIMITIVE:
        return PY_PRIMITIVE[t]
    if t == "object":
        ap = schema.get("additionalProperties")
        if isinstance(ap, dict):
            return f"dict[str, {model_type(ap)}]"
        return "dict[str, Any]"
    if "properties" in schema:
        return "dict[str, Any]"
    return "Any"


def gen_models() -> str:
    schemas = SWAGGER["components"]["schemas"]
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from pydantic import BaseModel, ConfigDict, Field",
        "",
        "",
        "class FNModel(BaseModel):",
        '    model_config = ConfigDict(populate_by_name=True, extra="allow")',
        "",
    ]
    names = list(schemas)
    for name in names:
        schema = schemas[name]
        props = schema.get("properties") or {}
        lines.append("")
        lines.append(f"class {name}(FNModel):")
        if not props:
            lines.append("    pass")
            continue
        for prop, pschema in props.items():
            py = snake(prop)
            ann = f"{model_type(pschema)} | None"
            if py != prop:
                lines.append(f'    {py}: {ann} = Field(default=None, alias="{prop}")')
            else:
                lines.append(f"    {py}: {ann} = None")
    lines.append("")
    lines.append("")
    lines.append("__all__ = [")
    for name in names:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")
    lines.append("for _m in list(__all__):")
    lines.append("    globals()[_m].model_rebuild()")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- resources

SCHEMA_NAMES = set(SWAGGER["components"]["schemas"])
HTTP_VERBS = ("get", "post", "put", "patch", "delete")
OPS: dict[tuple[str, str], dict] = {
    (verb.upper(), full_path): op
    for full_path, methods in SWAGGER["paths"].items()
    for verb, op in methods.items()
    if verb in HTTP_VERBS
}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
PATH_RE = re.compile(r"\{([^}]+)\}")
SPEC_KIND = {"integer": "int", "boolean": "bool", "number": "float"}


def full_swagger_path(version, path):
    if version is None:
        return path
    return f"/api/{version}{path}"


def spec_op(e) -> dict | None:
    """The swagger operation for an endpoint (None for SDK-only extras not present in the spec)."""
    key = (e["http"], full_swagger_path(e["version"], e["path"]))
    op = OPS.get(key)
    if op is None and e["in_spec"]:
        raise SystemExit(f"endpoint {e['name']} -> {key} is not in the spec")
    return op


def norm_query(entry):
    """Normalise a query override: name | (name, required, kind, py_name)."""
    if isinstance(entry, str):
        entry = (entry,)
    orig = entry[0]
    required = entry[1] if len(entry) > 1 else None
    kind = entry[2] if len(entry) > 2 else None
    py = entry[3] if len(entry) > 3 else None
    return orig, required, kind, py


def resolve_query(e):
    """Merge the spec's query parameters with the per-endpoint overrides.

    Every spec query parameter is exposed; overrides only adjust required/kind/py-name.
    """
    op = spec_op(e)
    overrides = {o[0]: o for o in e["query_overrides"]}
    out = []
    spec_params = [p for p in (op or {}).get("parameters", []) if p.get("in") == "query"]
    seen = set()
    for param in spec_params:
        name = param["name"]
        seen.add(name)
        _, required, kind, py = overrides.get(name, (name, None, None, None))
        if required is None:
            required = bool(param.get("required", False))
        if kind is None:
            kind = SPEC_KIND.get((param.get("schema") or {}).get("type"), "str")
        out.append((name, required, kind, py or snake(name)))
    for name, (orig, required, kind, py) in overrides.items():
        if name in seen:
            continue
        if op is not None:
            raise SystemExit(f"endpoint {e['name']}: query override {name!r} is not in the spec")
        out.append((orig, bool(required), kind or "str", py or snake(orig)))
    return out


def path_params(e):
    op = spec_op(e) or {}
    kinds = {
        p["name"]: SPEC_KIND.get((p.get("schema") or {}).get("type"), "str")
        for p in op.get("parameters", [])
        if p.get("in") == "path"
    }
    return [(name, kinds.get(name, "str")) for name in PATH_RE.findall(e["path"])]


def q_pytype(kind: str) -> str:
    if kind in ("csv", "list"):
        return "list[str]"
    return {"int": "int", "bool": "bool", "float": "float"}.get(kind, "str")


def q_value(kind: str, py: str) -> str:
    if kind == "csv":
        return f'",".join({py}) if {py} is not None else None'
    return py


def ep(name, http, path, version, *, query=None, body=None, body_optional=False, ret=None, kind="json",
       in_spec=True, deprecated_hint=None):
    return {
        "name": name,
        "http": http,
        "path": path,
        "version": version,
        "query_overrides": [norm_query(q) for q in (query or [])],
        "body": body,
        "body_optional": body_optional,
        "ret": ret,
        "kind": kind,
        "in_spec": in_spec,
        "deprecated_hint": deprecated_hint,
    }


def json_schema_of(content: dict | None) -> dict | None:
    if not content:
        return None
    for ct in ("application/json", "text/json", "text/plain"):
        if ct in content:
            return content[ct].get("schema")
    return next(iter(content.values())).get("schema")


def uses_model(ann: str) -> bool:
    return any(tok in SCHEMA_NAMES for tok in IDENT_RE.findall(ann))


def response_type(e) -> str | None:
    """Runtime type expression used to validate the JSON response (None = raw JSON)."""
    if e["kind"] in ("binary", "redirect"):
        return None
    ret = e["ret"]
    if ret is not None:
        return f"list[{ret[:-2]}]" if ret.endswith("[]") else ret
    op = spec_op(e) or {}
    schema = json_schema_of(op.get("responses", {}).get("200", {}).get("content"))
    if not schema:
        return None
    ann = model_type(schema)
    return ann if uses_model(ann) else None


def return_ann(e):
    if e["kind"] == "binary":
        return "bytes"
    if e["kind"] == "redirect":
        return "str | None"
    return response_type(e) or "Any"


def body_ann(e) -> str | None:
    if e["kind"] != "json":
        return None
    if e["body"] is not None:
        return e["body"]
    op = spec_op(e) or {}
    rb = op.get("requestBody")
    if not rb:
        return None
    schema = json_schema_of(rb.get("content"))
    if not schema:
        return "Any"
    if "$ref" in schema:
        return f"{model_type(schema)} | dict[str, Any]"
    ann = model_type(schema)
    return ann


def is_deprecated(e) -> bool:
    op = spec_op(e) or {}
    return bool(op.get("deprecated"))


def py_path(path):
    return PATH_RE.sub(lambda m: "{" + snake(m.group(1)) + "}", path)


def build_method(e, is_async, attr):
    query = resolve_query(e)
    required_q = [q for q in query if q[1]]
    optional_q = [q for q in query if not q[1]]
    token = e["kind"] in ("json", "binary", "redirect")
    body = body_ann(e)
    rtype = response_type(e)

    pos = [f"{snake(p)}: {q_pytype(k)}" for p, k in path_params(e)]
    for orig, required, kind, py in required_q:
        pos.append(f"{py}: {q_pytype(kind)}")
    kw = []
    if body is not None:
        if e["body_optional"]:
            kw.append(f"body: {body} | None = None")
        else:
            pos.append(f"body: {body}")

    kw += [f"{py}: {q_pytype(kind)} | None = None" for orig, required, kind, py in optional_q]
    if token:
        kw.append("fortnite_token: str | None = None")

    if e["kind"] == "multipart":
        pos = ["file: FileInput"]
        kw = ["filename: str | None = None"]
    elif e["kind"] == "multipart_multi":
        pos = ["files: list[FileInput]"]
        kw = ["filenames: list[str] | None = None"]

    sig = ["self"] + pos
    if kw:
        sig.append("*")
        sig += kw

    async_kw = "async " if is_async else ""
    await_kw = "await " if is_async else ""
    head = f"    {async_kw}def {e['name']}({', '.join(sig)}) -> {return_ann(e)}:"

    full = full_swagger_path(e["version"], e["path"])
    op = spec_op(e) or {}
    summary = " ".join((op.get("summary") or "").split()) or f"{e['http']} {full}"
    summary = summary.replace("\\", "\\\\").replace('"""', "'''")
    deprecated = is_deprecated(e)
    doc_body = [*textwrap.wrap(summary, 100), "",f"``{e['http']} {full}``"]
    warn_lines = []
    if deprecated:
        hint = e["deprecated_hint"]
        doc_body += ["", ".. deprecated::", "    This endpoint is marked as deprecated by the API."]
        if hint:
            doc_body.append(f"    {hint}")
        msg = f"{attr}.{e['name']}() calls {e['http']} {full}, which is deprecated by the API."
        if hint:
            msg += f" {hint}"
        warn_lines = [
            "        warnings.warn(",
            f"            {msg!r},",
            "            DeprecationWarning,",
            "            stacklevel=2,",
            "        )",
        ]
    doc = ['        """' + doc_body[0]] + [("        " + ln) if ln else "" for ln in doc_body[1:]] + ['        """']

    pp = py_path(e["path"])
    path_expr = f'f"{pp}"' if "{" in pp else f'"{pp}"'
    version_expr = "None" if e["version"] is None else f'"{e["version"]}"'

    if query:
        pairs = ", ".join(f'"{orig}": {q_value(kind, py)}' for orig, required, kind, py in query)
        params_expr = "{" + pairs + "}"
    else:
        params_expr = "None"
    rt_expr = rtype or "None"

    if e["kind"] == "binary":
        body_lines = [
            f"        return {await_kw}self._t.request_binary({path_expr}, {version_expr}, fortnite_token=fortnite_token)"
        ]
    elif e["kind"] == "redirect":
        body_lines = [
            f"        return {await_kw}self._t.request_redirect({path_expr}, {version_expr}, "
            f"params={params_expr}, fortnite_token=fortnite_token)"
        ]
    elif e["kind"] == "multipart":
        body_lines = [
            '        payload = {"file": self._t._file_tuple(file, filename)}',
            f"        return {await_kw}self._t.request_multipart({path_expr}, payload, response_type={rt_expr})",
        ]
    elif e["kind"] == "multipart_multi":
        body_lines = [
            "        payload = [",
            '            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))',
            "            for i, f in enumerate(files)",
            "        ]",
            f"        return {await_kw}self._t.request_multipart({path_expr}, payload, response_type={rt_expr})",
        ]
    else:
        body_expr = "body" if body is not None else "None"
        body_lines = [
            f'        return {await_kw}self._t.request("{e["http"]}", {path_expr}, {version_expr},',
            f"            params={params_expr}, json_body={body_expr}, fortnite_token=fortnite_token,",
            f"            response_type={rt_expr})",
        ]

    return "\n".join([head, *doc, *warn_lines, *body_lines])


def gen_resource_file(attr, prefix, endpoints):
    anns = []
    for e in endpoints:
        anns.append(return_ann(e))
        b = body_ann(e)
        if b:
            anns.append(b)
    models_used = sorted({tok for ann in anns for tok in IDENT_RE.findall(ann) if tok in SCHEMA_NAMES})
    has_multipart = any(e["kind"].startswith("multipart") for e in endpoints)
    uses_any = any("Any" in IDENT_RE.findall(ann) for ann in anns)
    has_deprecated = any(is_deprecated(e) for e in endpoints)

    header = ["from __future__ import annotations", ""]
    if has_deprecated:
        header.append("import warnings")
    if uses_any:
        header.append("from typing import Any")
    if has_deprecated or uses_any:
        header.append("")
    if has_multipart:
        header.append("from .._transport import FileInput")
    if models_used:
        header.append(f"from ..models import {', '.join(models_used)}")
    header += ["from ._base import Resource", "", ""]

    blocks = []
    for is_async in (False, True):
        cls = f"Async{prefix}Resource" if is_async else f"{prefix}Resource"
        methods = "\n\n".join(build_method(e, is_async, attr) for e in endpoints)
        blocks.append(f"class {cls}(Resource):\n{methods}\n")

    return "\n".join(header) + "\n\n".join(blocks)


# --------------------------------------------------------------------------- endpoint table

# Query parameters are taken from the spec automatically; ``query=`` only overrides
# (name, required, kind, py_name) for individual parameters. Response types are derived
# from the spec's 200 schema unless ``ret=`` is given; request bodies from ``requestBody``.
RESOURCES = {
    "account": ("Account", [
        ep("get_by_id", "GET", "/account/{accountId}", "v1"),
        ep("get_bulk", "GET", "/account/bulk", "v1", query=[("accountId", True, "list", "account_ids")]),
        ep("get_by_display_name", "GET", "/account/displayName/{displayName}", "v1"),
        ep("get_display_names", "GET", "/account/displaynames", "v1", query=[("ids", True, "csv", "account_ids")]),
        ep("bulk_external_display_names", "POST", "/account/external/displayNames/bulk", "v1"),
        ep("bulk_external_ids", "POST", "/account/external/ids/bulk", "v1"),
        ep("get_by_external_display_name", "GET", "/account/external/{externalAuthType}/displayName/{displayName}", "v1",
           query=[("caseInsensitive", False, "bool")]),
        ep("get_epic_id_sdk", "GET", "/account/sdk", "v1", query=[("accountId", True, "csv", "account_ids")]),
        ep("get_external_auths", "GET", "/account/{accountId}/externalAuths", "v1"),
        ep("get_external_auth", "GET", "/account/{accountId}/externalAuths/{authType}", "v1"),
    ]),
    "aes": ("Aes", [
        ep("get_keys", "GET", "/aes", "v1"),
        ep("get_history", "GET", "/aes/history", "v1"),
        ep("get_mappings", "GET", "/mappings", "v1"),
    ]),
    "assets": ("Assets", [
        ep("get_shop_bundles", "GET", "/assets/bundles/shop", "v1"),
        ep("get_tournament_bundles", "GET", "/assets/bundles/tournaments", "v1"),
    ]),
    "battlepass": ("BattlePass", [
        ep("get", "GET", "/battlepass", "v2"),
        ep("get_seasons", "GET", "/battlepass/seasons", "v2"),
        ep("get_legacy", "GET", "/shop/battlepass", "v1",
           deprecated_hint="Use battlepass.get() (GET /api/v2/battlepass) instead."),
    ]),
    "calendar": ("Calendar", [
        ep("get_season", "GET", "/season", "v1"),
    ]),
    "cosmetics": ("Cosmetics", [
        ep("get_all", "GET", "/cosmetics/all", "v2"),
        ep("get_new", "GET", "/cosmetics/new", "v2"),
        ep("search", "GET", "/cosmetics/search", "v2", query=[("q", True, "str")]),
        ep("get_by_id", "GET", "/cosmetics/{id}", "v2"),
    ]),
    "crew": ("Crew", [
        ep("get_current", "GET", "/crew/current", "v1"),
        ep("get_history", "GET", "/crew/history", "v1"),
    ]),
    "custom_match": ("CustomMatch", [
        ep("initiate", "POST", "/custom-match/initiate", "v1"),
        ep("get_status", "GET", "/custom-match/status/{playerId}", "v1"),
        ep("get_bots", "GET", "/custom-match/bots", "v1"),
        ep("register_account", "POST", "/custom-match/accounts", "v1"),
        ep("delete_account", "DELETE", "/custom-match/accounts/{id}", "v1"),
    ]),
    "events": ("Events", [
        ep("get_player_history", "GET", "/events/players/{accountId}/history", "v2"),
        ep("get_window_leaderboard", "GET", "/events/{eventId}/windows/{eventWindowId}/leaderboard", "v2"),
        ep("get_window_leaderboard_player", "GET", "/events/{eventId}/windows/{eventWindowId}/leaderboard/player", "v2"),
        ep("get_player_window_standing", "GET", "/events/{eventId}/windows/{eventWindowId}/players/{accountId}", "v2"),
    ]),
    "fn": ("FN", [
        ep("get_br_inventory", "GET", "/fn/br-inventory/{accountId}", "v2"),
        ep("get_enabled_features", "GET", "/fn/enabled-features", "v2"),
        ep("get_entitlement", "GET", "/fn/entitlement", "v2"),
        ep("request_entitlement", "POST", "/fn/entitlement/{accountId}", "v2"),
        ep("get_keychain", "GET", "/fn/keychain", "v2"),
        ep("get_privacy", "GET", "/fn/privacy/{accountId}", "v2"),
        ep("update_privacy", "POST", "/fn/privacy/{accountId}", "v2"),
        ep("get_receipts", "GET", "/fn/receipts/{accountId}", "v2"),
        ep("get_version", "GET", "/fn/version/{platform}", "v2"),
    ]),
    "friends": ("Friends", [
        ep("get_blocklist", "GET", "/friends/{accountId}/blocklist", "v1"),
        ep("get_friends", "GET", "/friends/{accountId}/friends", "v1"),
        ep("get_friend", "GET", "/friends/{accountId}/friends/{friendId}", "v1"),
        ep("get_mutual_friends", "GET", "/friends/{accountId}/friends/{friendId}/mutual", "v1"),
        ep("get_incoming", "GET", "/friends/{accountId}/incoming", "v1"),
        ep("get_outgoing", "GET", "/friends/{accountId}/outgoing", "v1"),
        ep("get_suggested", "GET", "/friends/{accountId}/suggested", "v1"),
        ep("get_summary", "GET", "/friends/{accountId}/summary", "v1"),
    ]),
    "identity": ("Identity", [
        ep("link", "POST", "/identity/link", "v1"),
        ep("get", "GET", "/identity/{discordId}", "v1"),
    ]),
    "map": ("Map", [
        ep("get", "GET", "/map", "v1"),
        ep("get_history", "GET", "/map/history", "v1"),
        ep("get_image", "GET", "/map/image", "v1", kind="redirect"),
    ]),
    "news": ("News", [
        ep("get_all", "GET", "/news", "v1"),
        ep("get_br", "GET", "/news/br", "v1"),
        ep("get_creative", "GET", "/news/creative", "v1"),
        ep("get_festival", "GET", "/news/festival", "v1"),
        ep("get_notices", "GET", "/news/notices", "v1"),
        ep("get_stw", "GET", "/news/stw", "v1"),
    ]),
    "oauth": ("OAuth", [
        ep("get_authorize_url", "GET", "/oauth/authorize-url", "v1"),
        ep("complete", "POST", "/oauth/complete", "v1"),
        ep("exchange_code", "POST", "/oauth/exchange-code", "v1"),
        ep("get_token", "GET", "/oauth/get-token", "v1"),
        ep("link", "POST", "/oauth/link", "v1"),
        ep("refresh_device", "POST", "/oauth/refresh-device", "v1"),
        ep("refresh_token", "POST", "/oauth/refresh-token", "v1"),
        ep("revoke_device", "POST", "/oauth/revoke-device", "v1"),
    ]),
    "parsing": ("Parsing", [
        ep("parse_replay", "POST", "/parsing", "v1", kind="multipart"),
        ep("parse_stats", "POST", "/parsing/stats", "v1", kind="multipart"),
        ep("parse_map", "POST", "/parsing/map", "v1", kind="multipart"),
        ep("parse_loot", "POST", "/parsing/loot", "v1", kind="multipart"),
        ep("parse_timeline", "POST", "/parsing/timeline", "v1", kind="multipart"),
        ep("parse_zones", "POST", "/parsing/zones", "v1", kind="multipart"),
        ep("parse_lobby", "POST", "/parsing/lobby", "v1", kind="multipart"),
        ep("parse_broadcast", "POST", "/parsing/broadcast", "v1", kind="multipart"),
        # Multi-file parsing endpoints are live but not (yet) published in the OpenAPI spec.
        ep("parse_multiple", "POST", "/parsing/multiple", "v1", kind="multipart_multi", in_spec=False),
        ep("parse_multiple_stats", "POST", "/parsing/multiple/stats", "v1", kind="multipart_multi", in_spec=False),
        ep("parse_multiple_map", "POST", "/parsing/multiple/map", "v1", kind="multipart_multi", in_spec=False),
        ep("parse_multiple_loot", "POST", "/parsing/multiple/loot", "v1", kind="multipart_multi", in_spec=False),
    ]),
    "playlists": ("Playlists", [
        ep("get_all", "GET", "/playlists", "v2"),
        ep("get_active", "GET", "/playlists/active", "v2"),
        ep("get_by_id", "GET", "/playlists/{playlistId}", "v2"),
    ]),
    "power_rankings": ("PowerRankings", [
        ep("get_leaderboard", "GET", "/events/powerrankings", "v1"),
        ep("get_player", "GET", "/events/powerrankings/player/{identifier}", "v1"),
        ep("search", "GET", "/events/powerrankings/search", "v1"),
        ep("get_from_archive", "GET", "/events/powerrankings/archive/{accountId}", "v1"),
    ]),
    "profile": ("Profile", [
        ep("get_leaderboard", "POST", "/profile/leaderboard/{gameId}", "v1"),
        ep("get_level", "GET", "/profile/level", "v1"),
        ep("get_progress", "GET", "/profile/progress", "v1"),
        ep("get_ranked", "GET", "/profile/ranked", "v1"),
        ep("bulk_track_progress", "POST", "/profile/trackprogress/bulk", "v1"),
        ep("get_tracks", "GET", "/profile/tracks", "v1"),
    ]),
    "quests": ("Quests", [
        ep("get", "GET", "/quests/{accountId}", "v2"),
        ep("get_definitions", "GET", "/quests/definitions", "v2"),
        ep("get_definition", "GET", "/quests/definitions/{templateId}", "v2"),
    ]),
    "replays": ("Replays", [
        ep("download", "GET", "/replays/{matchId}", "v1", kind="binary"),
        ep("get_metadata", "GET", "/replays/{matchId}/metadata", "v1"),
        ep("parse", "GET", "/replays/{matchId}/parse", "v1"),
        ep("parse_broadcast", "GET", "/replays/{matchId}/parse/broadcast", "v1",
           deprecated_hint="Use replays.parse() or the individual parse_* methods instead."),
        ep("parse_lobby", "GET", "/replays/{matchId}/parse/lobby", "v1"),
        ep("parse_loot", "GET", "/replays/{matchId}/parse/loot", "v1"),
        ep("parse_map", "GET", "/replays/{matchId}/parse/map", "v1"),
        ep("parse_stats", "GET", "/replays/{matchId}/parse/stats", "v1"),
        ep("parse_timeline", "GET", "/replays/{matchId}/parse/timeline", "v1"),
        ep("parse_tracks", "GET", "/replays/{matchId}/parse/tracks", "v1"),
        ep("parse_zones", "GET", "/replays/{matchId}/parse/zones", "v1"),
    ]),
    "shop": ("Shop", [
        ep("get_current", "GET", "/shop", "v1"),
    ]),
    "sprites": ("Sprites", [
        ep("get", "GET", "/sprites", "v2"),
        ep("get_all", "GET", "/sprites/all", "v2"),
        ep("get_versions", "GET", "/sprites/versions", "v2"),
        ep("get_boons", "GET", "/sprites/boons", "v2"),
        ep("get_by_id", "GET", "/sprites/{id}", "v2"),
        ep("get_collection", "GET", "/sprites/collection", "v2"),
        ep("get_all_collections", "GET", "/sprites/collection/all", "v2"),
        ep("publish_collection", "POST", "/sprites/collection/publish", "v2", body_optional=True),
        ep("unpublish_collection", "DELETE", "/sprites/collection/publish", "v2"),
        ep("get_shared_collection", "GET", "/sprites/collection/shared/{accountIdOrName}", "v2"),
    ]),
    "stats": ("Stats", [
        ep("get_bulk", "POST", "/stats/bulk", "v2"),
        ep("get_leaderboard", "GET", "/stats/leaderboard/{stat}", "v2"),
        ep("get", "GET", "/stats/{accountId}", "v2"),
    ]),
    "tournaments": ("Tournaments", [
        ep("get_cashprize", "GET", "/events/cashprize/{eventWindowId}", "v1"),
        ep("get_cashprizes", "GET", "/events/cashprizes", "v1"),
        ep("get_current", "GET", "/events/global", "v1"),
        ep("get_global_history", "GET", "/events/global/history", "v1"),
        ep("get_leaderboard", "GET", "/events/global/leaderboard", "v1"),
        ep("get_player", "GET", "/events/player", "v1"),
        ep("get_player_matches", "GET", "/events/player/{accountId}/matches", "v1"),
        ep("get_player_session", "GET", "/events/player/{accountId}/session", "v1"),
        ep("get_player_window_matches", "GET", "/events/{eventId}/{eventWindowId}/player/{accountId}/matches", "v1"),
        ep("get_scoring", "GET", "/events/scoring", "v1"),
        ep("get_window_scoring", "GET", "/events/scoring/{eventWindowId}", "v1"),
        ep("get_sessions", "GET", "/events/sessions", "v1"),
        ep("get_stat_leaders", "GET", "/events/stats/{eventId}/{eventWindowId}/{statKey}", "v1"),
        ep("get_team_stats", "GET", "/events/stats/{eventId}/{eventWindowId}/{statKey}/{teamIdentifier}", "v1"),
        ep("get_tokens", "GET", "/events/tokens", "v1",
           query=[("teamAccountIds", True, "csv", "team_account_ids")]),
        ep("get_tracker", "GET", "/events/tracker", "v1"),
        ep("get_tracker_eligibility", "GET", "/events/tracker/eligibility", "v1"),
        ep("check_eligibility", "GET", "/events/tracker/eligibility/{identifier}/{eventId}", "v1"),
    ]),
    "weapons": ("Weapons", [
        ep("get", "GET", "/weapons", "v2"),
        ep("get_by_id", "GET", "/weapons/{id}", "v2"),
        ep("get_lootpool", "GET", "/weapons/lootpool", "v2"),
        ep("get_patches", "GET", "/weapons/patches", "v2"),
        ep("get_rarities", "GET", "/weapons/rarity", "v2"),
    ]),
}


def gen_resources_init():
    lines = ["from __future__ import annotations", ""]
    for attr, (prefix, _) in RESOURCES.items():
        lines.append(f"from .{attr} import {prefix}Resource, Async{prefix}Resource")
    lines.append("")
    lines.append("__all__ = [")
    for attr, (prefix, _) in RESOURCES.items():
        lines.append(f'    "{prefix}Resource",')
        lines.append(f'    "Async{prefix}Resource",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def gen_client():
    imports = "\n".join(
        f"    {prefix}Resource,\n    Async{prefix}Resource," for prefix, _ in RESOURCES.values()
    )
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from ._transport import DEFAULT_BASE_URL, AsyncTransport, SyncTransport",
        "from .resources import (",
        imports,
        ")",
        "",
        "",
    ]

    def client_class(is_async):
        cls = "AsyncFortniteAPI" if is_async else "FortniteAPI"
        transport = "AsyncTransport" if is_async else "SyncTransport"
        body = [f"class {cls}:"]
        body.append('    """Client for the Fortnite API (https://api-fortnite.com)."""')
        body.append("")
        body.append("    def __init__(")
        body.append("        self,")
        body.append("        api_key: str,")
        body.append("        *,")
        body.append("        base_url: str = DEFAULT_BASE_URL,")
        body.append("        timeout: float = 30.0,")
        body.append("        fortnite_token: str | None = None,")
        body.append("    ) -> None:")
        body.append(f"        self._t = {transport}(api_key, base_url, timeout, fortnite_token)")
        for attr, (prefix, _) in RESOURCES.items():
            rcls = f"Async{prefix}Resource" if is_async else f"{prefix}Resource"
            body.append(f"        self.{attr} = {rcls}(self._t)")
        body.append("")
        if is_async:
            body.append("    async def health(self) -> Any:")
            body.append('        """``GET /health`` - service health check."""')
            body.append('        return await self._t.request("GET", "/health", None)')
            body.append("")
            body.append("    async def health_version(self) -> Any:")
            body.append('        """``GET /health/version`` - deployed API version information."""')
            body.append('        return await self._t.request("GET", "/health/version", None)')
            body.append("")
            body.append("    async def close(self) -> None:")
            body.append("        await self._t.close()")
            body.append("")
            body.append("    async def __aenter__(self) -> AsyncFortniteAPI:")
            body.append("        return self")
            body.append("")
            body.append("    async def __aexit__(self, *exc: Any) -> None:")
            body.append("        await self.close()")
        else:
            body.append("    def health(self) -> Any:")
            body.append('        """``GET /health`` - service health check."""')
            body.append('        return self._t.request("GET", "/health", None)')
            body.append("")
            body.append("    def health_version(self) -> Any:")
            body.append('        """``GET /health/version`` - deployed API version information."""')
            body.append('        return self._t.request("GET", "/health/version", None)')
            body.append("")
            body.append("    def close(self) -> None:")
            body.append("        self._t.close()")
            body.append("")
            body.append("    def __enter__(self) -> FortniteAPI:")
            body.append("        return self")
            body.append("")
            body.append("    def __exit__(self, *exc: Any) -> None:")
            body.append("        self.close()")
        body.append("")
        return "\n".join(body)

    return "\n".join(lines) + client_class(False) + "\n\n" + client_class(True) + "\n"


def main():
    (PKG / "models.py").write_text(gen_models())
    res_dir = PKG / "resources"
    res_dir.mkdir(exist_ok=True)
    (res_dir / "_base.py").write_text(
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n\n"
        "class Resource:\n"
        "    def __init__(self, transport: Any) -> None:\n"
        "        # SyncTransport for sync resources, AsyncTransport for async ones.\n"
        "        self._t: Any = transport\n"
    )
    for attr, (prefix, endpoints) in RESOURCES.items():
        (res_dir / f"{attr}.py").write_text(gen_resource_file(attr, prefix, endpoints))
    (res_dir / "__init__.py").write_text(gen_resources_init())
    (PKG / "client.py").write_text(gen_client())

    total = sum(len(v[1]) for v in RESOURCES.values())
    print(f"generated {len(SWAGGER['components']['schemas'])} models, "
          f"{len(RESOURCES)} resources, {total} endpoints")


if __name__ == "__main__":
    main()
