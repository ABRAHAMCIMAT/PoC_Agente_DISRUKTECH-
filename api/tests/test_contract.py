"""El contrato OpenAPI v1 (inc0) debe coincidir con las rutas reales de la API."""
import json
from pathlib import Path

from app.main import app

SPEC = json.loads((Path(__file__).resolve().parents[2] / "inc0" / "openapi.json").read_text())


def test_rutas_y_metodos_coinciden_con_contrato():
    real = {(r.path, m) for r in app.routes if hasattr(r, "methods")
            for m in r.methods if r.path.startswith(("/health", "/purchase", "/stock"))}
    spec = {(p.replace("{poNumber}", "{po_number}"), m.upper())
            for p, ops in SPEC["paths"].items() for m in ops}
    assert real == spec


def test_solo_get_en_contrato():
    assert all(set(ops) == {"get"} for ops in SPEC["paths"].values())


def test_umbral_obligatorio_en_contrato():
    params = SPEC["paths"]["/stock/below-threshold"]["get"]["parameters"]
    assert next(p for p in params if p["name"] == "threshold")["required"] is True
