"""Code generator for the Fortnite API SDK.

Reads openapi/swagger.json and a declarative endpoint table, then emits
src/fortnite_api/models.py, resources/*.py and client.py for sync + async.
Run with: uv run python scripts/generate.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "src" / "fortnite_api"
SWAGGER = json.loads((ROOT / "openapi" / "swagger.json").read_text())

INT_NAMES = {"page", "pageSize", "limit", "offset", "top", "fromIndex", "days", "requiredTournaments"}


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

SUMMARIES: dict[tuple[str, str], str] = {}
for full_path, methods in SWAGGER["paths"].items():
    for verb, op in methods.items():
        s = (op.get("summary") or "").strip().splitlines()
        if s:
            SUMMARIES[(verb.upper(), full_path)] = s[0]


def norm_query(entry):
    if isinstance(entry, str):
        orig, required, kind, py = entry, False, None, None
    else:
        orig = entry[0]
        required = entry[1] if len(entry) > 1 else False
        kind = entry[2] if len(entry) > 2 else None
        py = entry[3] if len(entry) > 3 else None
    if kind is None:
        kind = "int" if orig in INT_NAMES else "str"
    if py is None:
        py = snake(orig)
    return orig, required, kind, py


def q_pytype(kind: str) -> str:
    if kind in ("csv", "list"):
        return "list[str]"
    return {"int": "int", "bool": "bool"}.get(kind, "str")


def q_value(kind: str, py: str) -> str:
    if kind == "csv":
        return f'",".join({py})'
    return py


def ep(name, http, path, version, *, query=None, body=None, ret=None, kind="json"):
    return {
        "name": name,
        "http": http,
        "path": path,
        "version": version,
        "query": [norm_query(q) for q in (query or [])],
        "body": body,
        "ret": ret,
        "kind": kind,
    }


def full_swagger_path(version, path):
    if version is None:
        return path
    return f"/api/{version}{path}"


def return_ann(e):
    if e["kind"] == "binary":
        return "bytes"
    if e["kind"] == "redirect":
        return "str | None"
    ret = e["ret"]
    if ret is None:
        return "Any"
    if ret.endswith("[]"):
        return f"list[{ret[:-2]}]"
    return ret


def model_args(e):
    ret = e["ret"]
    if not ret:
        return "None, is_list=False"
    if ret.endswith("[]"):
        return f"{ret[:-2]}, is_list=True"
    return f"{ret}, is_list=False"


PATH_RE = re.compile(r"\{([^}]+)\}")


def py_path(path):
    return PATH_RE.sub(lambda m: "{" + snake(m.group(1)) + "}", path)


def build_method(e, is_async):
    path_params = PATH_RE.findall(e["path"])
    required_q = [q for q in e["query"] if q[1]]
    optional_q = [q for q in e["query"] if not q[1]]
    token = e["kind"] in ("json", "binary", "redirect")

    pos = [f"{snake(p)}: str" for p in path_params]
    for orig, required, kind, py in required_q:
        pos.append(f"{py}: {q_pytype(kind)}")
    if e["body"] is not None:
        pos.append(f"body: {e['body']}")

    kw = [f"{py}: {q_pytype(kind)} | None = None" for orig, required, kind, py in optional_q]
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

    summary = SUMMARIES.get((e["http"], full_swagger_path(e["version"], e["path"])))
    doc = [f'        """{summary}"""'] if summary else []

    pp = py_path(e["path"])
    path_expr = f'f"{pp}"' if "{" in pp else f'"{pp}"'
    version_expr = "None" if e["version"] is None else f'"{e["version"]}"'

    if e["query"]:
        pairs = ", ".join(f'"{orig}": {q_value(kind, py)}' for orig, required, kind, py in e["query"])
        params_expr = "{" + pairs + "}"
    else:
        params_expr = "None"

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
            f"        return {await_kw}self._t.request_multipart({path_expr}, payload, model={model_args(e)})",
        ]
    elif e["kind"] == "multipart_multi":
        body_lines = [
            "        payload = [",
            '            ("files", self._t._file_tuple(f, filenames[i] if filenames else None))',
            "            for i, f in enumerate(files)",
            "        ]",
            f"        return {await_kw}self._t.request_multipart({path_expr}, payload, model={model_args(e)})",
        ]
    else:
        body_expr = "body" if e["body"] is not None else "None"
        body_lines = [
            f'        return {await_kw}self._t.request("{e["http"]}", {path_expr}, {version_expr},',
            f"            params={params_expr}, json_body={body_expr}, fortnite_token=fortnite_token,",
            f"            model={model_args(e)})",
        ]

    return "\n".join([head, *doc, *body_lines])


def gen_resource_file(prefix, endpoints):
    models_used = sorted({e["ret"][:-2] if e["ret"].endswith("[]") else e["ret"] for e in endpoints if e["ret"]})
    has_multipart = any(e["kind"].startswith("multipart") for e in endpoints)
    uses_any = any(return_ann(e) == "Any" or e["body"] == "Any" for e in endpoints)

    header = ["from __future__ import annotations", ""]
    if uses_any:
        header += ["from typing import Any", ""]
    if has_multipart:
        header.append("from .._transport import FileInput")
    if models_used:
        header.append(f"from ..models import {', '.join(models_used)}")
    header += ["from ._base import Resource", "", ""]

    blocks = []
    for is_async in (False, True):
        cls = f"Async{prefix}Resource" if is_async else f"{prefix}Resource"
        methods = "\n\n".join(build_method(e, is_async) for e in endpoints)
        blocks.append(f"class {cls}(Resource):\n{methods}\n")

    return "\n".join(header) + "\n\n".join(blocks)


# --------------------------------------------------------------------------- endpoint table

RESOURCES = {
    "account": ("Account", [
        ep("get_by_id", "GET", "/account/{accountId}", "v1"),
        ep("get_bulk", "GET", "/account/bulk", "v1", query=[("accountId", True, "list", "account_ids")]),
        ep("get_by_display_name", "GET", "/account/displayName/{displayName}", "v1"),
        ep("get_display_names", "GET", "/account/displaynames", "v1", query=[("ids", True, "csv", "account_ids")]),
        ep("bulk_external_display_names", "POST", "/account/external/displayNames/bulk", "v1", body="Any"),
        ep("bulk_external_ids", "POST", "/account/external/ids/bulk", "v1", body="Any"),
        ep("get_by_external_display_name", "GET", "/account/external/{externalAuthType}/displayName/{displayName}", "v1",
           query=[("caseInsensitive", False, "bool")]),
        ep("get_epic_id_sdk", "GET", "/account/sdk", "v1", query=[("accountId", True, "csv", "account_ids")]),
        ep("get_external_auths", "GET", "/account/{accountId}/externalAuths", "v1"),
        ep("get_external_auth", "GET", "/account/{accountId}/externalAuths/{authType}", "v1"),
    ]),
    "aes": ("Aes", [
        ep("get_keys", "GET", "/aes", "v1"),
        ep("get_mappings", "GET", "/mappings", "v1"),
    ]),
    "assets": ("Assets", [
        ep("get_shop_bundles", "GET", "/assets/bundles/shop", "v1"),
        ep("get_tournament_bundles", "GET", "/assets/bundles/tournaments", "v1"),
    ]),
    "calendar": ("Calendar", [
        ep("get_season", "GET", "/season", "v1", ret="SeasonEntryDto"),
    ]),
    "cosmetics": ("Cosmetics", [
        ep("get_all", "GET", "/cosmetics/all", "v2",
           query=["page", "pageSize", "type", "rarity", "set", "search", "season", "chapter", "lang"],
           ret="CosmeticDtoPaginatedResultDto"),
        ep("get_new", "GET", "/cosmetics/new", "v2", query=["page", "pageSize", "lang"],
           ret="CosmeticDtoPaginatedResultDto"),
        ep("search", "GET", "/cosmetics/search", "v2",
           query=[("q", True, "str"), "page", "pageSize", "type", "rarity", "set", "lang"],
           ret="CosmeticDtoPaginatedResultDto"),
        ep("get_by_id", "GET", "/cosmetics/{id}", "v2", query=["lang"], ret="CosmeticDto"),
    ]),
    "crew": ("Crew", [
        ep("get_current", "GET", "/crew/current", "v1"),
        ep("get_history", "GET", "/crew/history", "v1"),
    ]),
    "events": ("Events", [
        ep("get_player_history", "GET", "/events/players/{accountId}/history", "v2"),
        ep("get_window_leaderboard", "GET", "/events/{eventId}/windows/{eventWindowId}/leaderboard", "v2",
           query=["page", ("leaderboardDef", False, "str")]),
        ep("get_window_leaderboard_player", "GET", "/events/{eventId}/windows/{eventWindowId}/leaderboard/player", "v2",
           query=[("accountId", False, "str")]),
        ep("get_player_window_standing", "GET", "/events/{eventId}/windows/{eventWindowId}/players/{accountId}", "v2"),
    ]),
    "fn": ("FN", [
        ep("get_br_inventory", "GET", "/fn/br-inventory/{accountId}", "v2"),
        ep("get_enabled_features", "GET", "/fn/enabled-features", "v2"),
        ep("get_entitlement", "GET", "/fn/entitlement", "v2"),
        ep("request_entitlement", "POST", "/fn/entitlement/{accountId}", "v2"),
        ep("get_keychain", "GET", "/fn/keychain", "v2"),
        ep("get_privacy", "GET", "/fn/privacy/{accountId}", "v2"),
        ep("update_privacy", "POST", "/fn/privacy/{accountId}", "v2", body="Any"),
        ep("get_receipts", "GET", "/fn/receipts/{accountId}", "v2"),
        ep("get_version", "GET", "/fn/version/{platform}", "v2", query=[("version", False, "str")]),
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
    "map": ("Map", [
        ep("get", "GET", "/map", "v1", query=[("version", False, "str"), "lang"], ret="MapDataDto"),
        ep("get_history", "GET", "/map/history", "v1",
           query=[("chapter", False, "int"), ("season", False, "int")], ret="MapHistoryEntryDto[]"),
        ep("get_image", "GET", "/map/image", "v1", query=[("version", False, "str")], kind="redirect"),
    ]),
    "news": ("News", [
        ep("get_all", "GET", "/news", "v1", query=["lang"]),
        ep("get_br", "GET", "/news/br", "v1", query=["lang"]),
        ep("get_creative", "GET", "/news/creative", "v1", query=["lang"]),
        ep("get_stw", "GET", "/news/stw", "v1", query=["lang"]),
    ]),
    "oauth": ("OAuth", [
        ep("get_authorize_url", "GET", "/oauth/authorize-url", "v1", query=[("redirectUri", False, "str")]),
        ep("complete", "POST", "/oauth/complete", "v1", body="Any"),
        ep("exchange_code", "POST", "/oauth/exchange-code", "v1", body="Any"),
        ep("get_token", "GET", "/oauth/get-token", "v1"),
        ep("link", "POST", "/oauth/link", "v1", body="Any"),
        ep("refresh_device", "POST", "/oauth/refresh-device", "v1", body="Any"),
        ep("refresh_token", "POST", "/oauth/refresh-token", "v1", body="Any"),
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
        ep("parse_multiple", "POST", "/parsing/multiple", "v1", kind="multipart_multi"),
        ep("parse_multiple_stats", "POST", "/parsing/multiple/stats", "v1", kind="multipart_multi"),
        ep("parse_multiple_map", "POST", "/parsing/multiple/map", "v1", kind="multipart_multi"),
        ep("parse_multiple_loot", "POST", "/parsing/multiple/loot", "v1", kind="multipart_multi"),
    ]),
    "playlists": ("Playlists", [
        ep("get_all", "GET", "/playlists", "v2", query=["lang"]),
        ep("get_active", "GET", "/playlists/active", "v2", query=["lang"]),
        ep("get_by_id", "GET", "/playlists/{playlistId}", "v2", query=["lang"]),
    ]),
    "profile": ("Profile", [
        ep("get_leaderboard", "POST", "/profile/leaderboard/{gameId}", "v1",
           query=[("accountId", False, "str"), ("fromIndex", False, "int"), ("findTeams", False, "bool")]),
        ep("get_level", "GET", "/profile/level", "v1", query=[("accountId", False, "str")]),
        ep("get_progress", "GET", "/profile/progress", "v1", query=[("accountId", False, "str")]),
        ep("get_ranked", "GET", "/profile/ranked", "v1",
           query=[("displayName", False, "str"), ("accountId", False, "str")]),
        ep("bulk_track_progress", "POST", "/profile/trackprogress/bulk", "v1", body="Any"),
        ep("get_tracks", "GET", "/profile/tracks", "v1",
           query=[("endsBefore", False, "str"), ("endsAfter", False, "str")]),
    ]),
    "quests": ("Quests", [
        ep("get", "GET", "/quests/{accountId}", "v2"),
    ]),
    "replays": ("Replays", [
        ep("download", "GET", "/replays/{matchId}", "v1", kind="binary"),
        ep("get_metadata", "GET", "/replays/{matchId}/metadata", "v1"),
        ep("parse", "GET", "/replays/{matchId}/parse", "v1"),
        ep("parse_broadcast", "GET", "/replays/{matchId}/parse/broadcast", "v1"),
        ep("parse_lobby", "GET", "/replays/{matchId}/parse/lobby", "v1"),
        ep("parse_loot", "GET", "/replays/{matchId}/parse/loot", "v1"),
        ep("parse_map", "GET", "/replays/{matchId}/parse/map", "v1"),
        ep("parse_stats", "GET", "/replays/{matchId}/parse/stats", "v1"),
        ep("parse_timeline", "GET", "/replays/{matchId}/parse/timeline", "v1"),
        ep("parse_zones", "GET", "/replays/{matchId}/parse/zones", "v1"),
    ]),
    "shop": ("Shop", [
        ep("get_current", "GET", "/shop", "v1",
           query=["type", "section", "rarity", "search", "lang"], ret="ShopResponseDto"),
    ]),
    "battlepass": ("BattlePass", [
        ep("get", "GET", "/shop/battlepass", "v1", query=["lang"]),
    ]),
    "stats": ("Stats", [
        ep("get_bulk", "POST", "/stats/bulk", "v2", body="Any"),
        ep("get_leaderboard", "GET", "/stats/leaderboard/{stat}", "v2",
           query=[("limit", False, "int"), ("offset", False, "int"), ("window", False, "str")]),
        ep("get", "GET", "/stats/{accountId}", "v2",
           query=[("startTime", False, "str"), ("endTime", False, "str"), ("stats", False, "str")]),
    ]),
    "tournaments": ("Tournaments", [
        ep("get_cashprize", "GET", "/events/cashprize/{eventWindowId}", "v1"),
        ep("get_cashprizes", "GET", "/events/cashprizes", "v1"),
        ep("get_current", "GET", "/events/global", "v1", query=["lang"]),
        ep("get_global_history", "GET", "/events/global/history", "v1", query=["lang"]),
        ep("get_leaderboard", "GET", "/events/global/leaderboard", "v1",
           query=[("eventId", False, "str"), ("eventWindowId", False, "str"), ("page", False, "int"),
                  ("leaderboardDef", False, "str"), ("accountId", False, "str")]),
        ep("get_player", "GET", "/events/player", "v1",
           query=[("region", False, "str"), ("platform", False, "str"), ("accountId", False, "str")]),
        ep("get_power_rankings", "GET", "/events/powerrankings", "v1",
           query=[("page", False, "int"), ("accountId", False, "str")]),
        ep("get_power_rankings_player", "GET", "/events/powerrankings/player/{identifier}", "v1"),
        ep("search_power_rankings", "GET", "/events/powerrankings/search", "v1",
           query=[("q", False, "str"), ("limit", False, "int")]),
        ep("get_sessions", "GET", "/events/sessions", "v1", query=[("eventId", False, "str")]),
        ep("get_stat_leaders", "GET", "/events/stats/{eventId}/{eventWindowId}/{statKey}", "v1",
           query=[("top", False, "int")]),
        ep("get_team_stats", "GET", "/events/stats/{eventId}/{eventWindowId}/{statKey}/{teamIdentifier}", "v1",
           query=[("twitter", False, "bool")]),
        ep("get_tokens", "GET", "/events/tokens", "v1",
           query=[("teamAccountIds", True, "csv", "team_account_ids")]),
        ep("get_tracker", "GET", "/events/tracker", "v1",
           query=[("accountId", False, "str"), ("validOnly", False, "bool")]),
        ep("get_tracker_debug", "GET", "/events/tracker/debug", "v1", query=[("accountId", False, "str")]),
        ep("get_tracker_eligibility", "GET", "/events/tracker/eligibility", "v1",
           query=[("accountId", False, "str"), ("days", False, "int"), ("requiredTournaments", False, "int")]),
        ep("check_eligibility", "GET", "/events/tracker/eligibility/{identifier}/{eventId}", "v1",
           query=[("eventWindowId", False, "str")]),
    ]),
    "weapons": ("Weapons", [
        ep("get", "GET", "/weapons", "v2",
           query=[("patch", False, "str"), ("category", False, "str"), ("search", False, "str"),
                  ("rarity", False, "str"), ("type", False, "str"), ("ammoType", False, "str"),
                  ("gamemode", False, "str"), ("itemType", False, "str"), ("lang", False, "str")],
           ret="WeaponListItemDto[]"),
        ep("get_patches", "GET", "/weapons/patches", "v2", ret="PatchInfoDto[]"),
        ep("get_rarities", "GET", "/weapons/rarity", "v2", ret="RarityDefinitionDto[]"),
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
    imports = ", ".join(
        f"{prefix}Resource, Async{prefix}Resource" for prefix, _ in RESOURCES.values()
    )
    lines = [
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "from ._transport import DEFAULT_BASE_URL, AsyncTransport, SyncTransport",
        f"from .resources import {imports}",
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
            body.append('        return await self._t.request("GET", "/health", None, model=None, is_list=False)')
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
            body.append('        return self._t.request("GET", "/health", None, model=None, is_list=False)')
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
        "from __future__ import annotations\n\n\n"
        "class Resource:\n"
        "    def __init__(self, transport: object) -> None:\n"
        "        self._t = transport\n"
    )
    for attr, (prefix, endpoints) in RESOURCES.items():
        (res_dir / f"{attr}.py").write_text(gen_resource_file(prefix, endpoints))
    (res_dir / "__init__.py").write_text(gen_resources_init())
    (PKG / "client.py").write_text(gen_client())

    total = sum(len(v[1]) for v in RESOURCES.values())
    print(f"generated {len(SWAGGER['components']['schemas'])} models, "
          f"{len(RESOURCES)} resources, {total} endpoints")


if __name__ == "__main__":
    main()
