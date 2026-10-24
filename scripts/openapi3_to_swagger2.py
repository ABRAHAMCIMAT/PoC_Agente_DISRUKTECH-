"""Convierte inc0/openapi.json (OpenAPI 3.0) a Swagger 2.0 apto para conectores personalizados de Power Platform.
Uso: python scripts/openapi3_to_swagger2.py --host mi-api.onrender.com [--out docs/powerplatform/apiDefinition.swagger.json]
Restricciones de Power Platform aplicadas: summary <= 80 caracteres, operationId unico, x-ms-summary en parametros,
securityDefinitions de tipo apiKey y esquema https."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_SUMMARY = 80


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


def convert(spec: dict, host: str) -> dict:
    out = {
        "swagger": "2.0",
        "info": {"title": spec["info"]["title"][:80], "description": spec["info"]["description"],
                 "version": spec["info"]["version"]},
        "host": host, "basePath": "/", "schemes": ["https"],
        "consumes": [], "produces": ["application/json"],
        "paths": {}, "definitions": {},
        "securityDefinitions": {"api_key": {"type": "apiKey", "in": "header", "name": "X-API-Key",
                                            "description": "Clave de la API (cabecera X-API-Key)"}},
        "security": [{"api_key": []}],
    }
    comps = spec["components"]
    out["definitions"] = {k: fix_schema(v) for k, v in comps["schemas"].items()}
    resp_defs = comps.get("responses", {})
    for path, ops in spec["paths"].items():
        out["paths"][path] = {}
        for method, op in ops.items():
            desc = op["summary"] if not op.get("description") else f'{op["summary"]} {op["description"]}'
            new = {"operationId": op["operationId"], "summary": short(op["summary"]), "description": desc,
                   "x-ms-visibility": "important", "parameters": [], "responses": {}}
            if op.get("security") == []:
                new["security"] = []
            for p in op.get("parameters", []):
                np = {"name": p["name"], "in": p["in"], "required": p.get("required", False),
                      "description": p.get("description", ""), "x-ms-summary": p["name"]}
                np.update(copy.deepcopy(p["schema"]))
                new["parameters"].append(np)
            for code, r in op["responses"].items():
                if "$ref" in r:
                    r = resp_defs[r["$ref"].split("/")[-1]]
                entry = {"description": r["description"]}
                content = r.get("content", {}).get("application/json")
                if content:
                    entry["schema"] = fix_schema(content["schema"])
                new["responses"][code] = entry
            out["paths"][path][method] = new
    return out


def validate(sw: dict) -> list:
    errs, ids = [], set()
    defs = set(sw["definitions"])

    def refs(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "$ref" and v.split("/")[-1] not in defs:
                    errs.append(f"$ref sin resolver: {v}")
                refs(v)
        elif isinstance(x, list):
            for v in x:
                refs(v)

    for path, ops in sw["paths"].items():
        for m, op in ops.items():
            if len(op["summary"]) > MAX_SUMMARY:
                errs.append(f"summary > {MAX_SUMMARY}: {op['operationId']}")
            if op["operationId"] in ids:
                errs.append(f"operationId repetido: {op['operationId']}")
            ids.add(op["operationId"])
            if m != "get":
                errs.append(f"metodo no GET: {path} {m}")
    refs(sw)
    return errs


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="REEMPLAZAR-HOST-API")
    ap.add_argument("--src", default=str(ROOT / "inc0" / "openapi.json"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "powerplatform" / "apiDefinition.swagger.json"))
    a = ap.parse_args()
    sw = convert(json.loads(Path(a.src).read_text(encoding="utf-8")), a.host)
    problems = validate(sw)
    if problems:
        raise SystemExit("\n".join(problems))
    Path(a.out).write_text(json.dumps(sw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK -> {a.out} ({len(sw['paths'])} rutas)")
