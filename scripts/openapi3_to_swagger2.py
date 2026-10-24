"""Convierte inc0/openapi.json (OpenAPI 3.0) a Swagger 2.0 apto para conectores personalizados de Power Platform.
Uso: python scripts/openapi3_to_swagger2.py --host mi-api.onrender.com
Escribe siempre docs/powerplatform/apiDefinition.swagger.json (las rutas son fijas, no se aceptan por argumento).
Restricciones de Power Platform aplicadas: summary <= 80 caracteres, operationId unico, x-ms-summary en parametros,
securityDefinitions de tipo apiKey y esquema https."""
import argparse
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "inc0" / "openapi.json"
OUT = ROOT / "docs" / "powerplatform" / "apiDefinition.swagger.json"
MAX_SUMMARY = 80
HOST_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?(:[0-9]{1,5})?$")


def short(text: str) -> str:
    first = text.split(". ")[0].rstrip(".")
    if len(first) <= MAX_SUMMARY:
        return first
    return first[: MAX_SUMMARY - 1].rstrip() + "…"


def fix_schema(s):
    if isinstance(s, dict):
        s = {k: fix_schema(v) for k, v in s.items()}
        if "$ref" in s:
            s["$ref"] = s["$ref"].replace("#/components/schemas/", "#/definitions/")
        return s
    if isinstance(s, list):
        return [fix_schema(x) for x in s]
    return s


def convert_parameter(p: dict) -> dict:
    out = {"name": p["name"], "in": p["in"], "required": p.get("required", False),
           "description": p.get("description", ""), "x-ms-summary": p["name"]}
    out.update(copy.deepcopy(p["schema"]))
    return out


def convert_response(r: dict, resp_defs: dict) -> dict:
    if "$ref" in r:
        r = resp_defs[r["$ref"].split("/")[-1]]
    entry = {"description": r["description"]}
    content = r.get("content", {}).get("application/json")
    if content:
        entry["schema"] = fix_schema(content["schema"])
    return entry


def convert_operation(op: dict, resp_defs: dict) -> dict:
    desc = op["summary"]
    if op.get("description"):
        desc = f'{op["summary"]} {op["description"]}'
    new = {"operationId": op["operationId"], "summary": short(op["summary"]), "description": desc,
           "x-ms-visibility": "important",
           "parameters": [convert_parameter(p) for p in op.get("parameters", [])],
           "responses": {code: convert_response(r, resp_defs) for code, r in op["responses"].items()}}
    if op.get("security") == []:
        new["security"] = []
    return new


def convert(spec: dict, host: str) -> dict:
    comps = spec["components"]
    resp_defs = comps.get("responses", {})
    return {
        "swagger": "2.0",
        "info": {"title": spec["info"]["title"][:80], "description": spec["info"]["description"],
                 "version": spec["info"]["version"]},
        "host": host, "basePath": "/", "schemes": ["https"],
        "consumes": [], "produces": ["application/json"],
        "paths": {path: {m: convert_operation(op, resp_defs) for m, op in ops.items()}
                  for path, ops in spec["paths"].items()},
        "definitions": {k: fix_schema(v) for k, v in comps["schemas"].items()},
        "securityDefinitions": {"api_key": {"type": "apiKey", "in": "header", "name": "X-API-Key",
                                            "description": "Clave de la API (cabecera X-API-Key)"}},
        "security": [{"api_key": []}],
    }


def find_bad_refs(node, defs: set) -> list:
    """Referencias $ref que no apuntan a una definicion existente."""
    if isinstance(node, dict):
        bad = [f"$ref sin resolver: {v}" for k, v in node.items()
               if k == "$ref" and v.split("/")[-1] not in defs]
        return bad + [e for v in node.values() for e in find_bad_refs(v, defs)]
    if isinstance(node, list):
        return [e for v in node for e in find_bad_refs(v, defs)]
    return []


def validate_operation(path: str, method: str, op: dict, seen: set) -> list:
    errs = []
    if len(op["summary"]) > MAX_SUMMARY:
        errs.append(f"summary > {MAX_SUMMARY}: {op['operationId']}")
    if op["operationId"] in seen:
        errs.append(f"operationId repetido: {op['operationId']}")
    if method != "get":
        errs.append(f"metodo no GET: {path} {method}")
    seen.add(op["operationId"])
    return errs


def validate(sw: dict) -> list:
    seen: set = set()
    errs = [e for path, ops in sw["paths"].items() for m, op in ops.items()
            for e in validate_operation(path, m, op, seen)]
    return errs + find_bad_refs(sw, set(sw["definitions"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="REEMPLAZAR-HOST-API")
    host = ap.parse_args().host
    if not HOST_RE.match(host):
        raise SystemExit(f"Host invalido: {host!r} (use solo el nombre de host, sin https://)")
    sw = convert(json.loads(SRC.read_text(encoding="utf-8")), host)
    problems = validate(sw)
    if problems:
        raise SystemExit("\n".join(problems))
    OUT.write_text(json.dumps(sw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {OUT.relative_to(ROOT)} ({len(sw['paths'])} rutas)")


if __name__ == "__main__":
    main()
