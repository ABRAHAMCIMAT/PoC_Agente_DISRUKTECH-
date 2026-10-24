"""La variante Swagger 2.0 para Power Platform debe estar sincronizada con el contrato y cumplir sus restricciones."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("conv", ROOT / "scripts" / "openapi3_to_swagger2.py")
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)

OPENAPI = json.loads((ROOT / "inc0" / "openapi.json").read_text(encoding="utf-8"))
COMMITTED = json.loads((ROOT / "docs" / "powerplatform" / "apiDefinition.swagger.json").read_text(encoding="utf-8"))


def test_swagger_comitido_esta_sincronizado_con_openapi():
    assert COMMITTED == conv.convert(OPENAPI, "REEMPLAZAR-HOST-API"), \
        "Regenerar con: python scripts/openapi3_to_swagger2.py"


def test_restricciones_power_platform():
    assert conv.validate(COMMITTED) == []
    assert COMMITTED["swagger"] == "2.0"
    assert COMMITTED["schemes"] == ["https"]
    assert COMMITTED["securityDefinitions"]["api_key"]["name"] == "X-API-Key"
    ids = {o["operationId"] for p in COMMITTED["paths"].values() for o in p.values()}
    assert ids == {"getHealth", "listPurchaseOrders", "getPurchaseOrder", "getStock", "getStockBelowThreshold"}


def test_host_invalido_se_rechaza():
    for bad in ("https://x.com", "../x", "a b", ""):
        assert not conv.HOST_RE.match(bad), bad
    assert conv.HOST_RE.match("mi-api.onrender.com")
    assert conv.HOST_RE.match("localhost:8000")


def test_apiproperties_coincide_con_security_definition():
    props = json.loads((ROOT / "docs" / "powerplatform" / "apiProperties.json").read_text(encoding="utf-8"))
    assert set(props["properties"]["connectionParameters"]) == set(COMMITTED["securityDefinitions"])
