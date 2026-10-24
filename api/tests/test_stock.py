import os

import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "test-key"
os.environ["DB_PATH"] = "/tmp/opencode/test_demo_stock.db"

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

H = {"X-API-Key": "test-key"}
client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module", autouse=True)
def _seed():
    seed(reset=True)


def test_sin_credencial_401():
    assert client.get("/stock?plant=C100").status_code == 401
    assert client.get("/stock/below-threshold?threshold=10").status_code == 401


def test_i1_por_material_id_con_total_por_centro():
    r = client.get("/stock?material=M-1001", headers=H).json()
    assert r["total"] >= 1
    assert all(i["materialId"] == "M-1001" and i["uom"] for i in r["items"])


def test_i1_por_descripcion_parcial():
    r = client.get("/stock?material=acero&limit=50", headers=H).json()
    assert {i["materialId"] for i in r["items"]} == {"M-1001", "M-1002"}


def test_i1_material_inexistente_404():
    r = client.get("/stock?material=M-9999", headers=H)
    assert r.status_code == 404 and r.json()["code"] == "NOT_FOUND"


def test_i2_por_centro_ordenado_y_limitado():
    r = client.get("/stock?plant=C100", headers=H).json()
    assert len(r["items"]) <= 10 and r["total"] >= len(r["items"])
    q = [i["quantity"] for i in r["items"]]
    assert q == sorted(q, reverse=True)
    assert all(i["plantId"] == "C100" for i in r["items"])


def test_i2_centro_inexistente_404_y_case_insensitive():
    assert client.get("/stock?plant=ZZZ", headers=H).status_code == 404
    assert client.get("/stock?plant=c100", headers=H).status_code == 200


def test_stock_sin_filtros_400():
    r = client.get("/stock", headers=H)
    assert r.status_code == 400 and r.json()["code"] == "BAD_REQUEST"


def test_caso_existencia_cero_se_devuelve():
    r = client.get("/stock?material=M-1040&plant=C400", headers=H).json()
    assert r["total"] == 1 and r["items"][0]["quantity"] == 0


def test_i3_umbral_100_al_menos_3_materiales():
    r = client.get("/stock/below-threshold?threshold=100&limit=50", headers=H).json()
    assert r["total"] >= 3 and r["threshold"] == 100
    assert all(i["totalQuantity"] < 100 for i in r["items"])
    q = [i["totalQuantity"] for i in r["items"]]
    assert q == sorted(q)


def test_i3_umbral_obligatorio_400():
    r = client.get("/stock/below-threshold", headers=H)
    assert r.status_code == 400 and "threshold" in r.json()["message"]
    assert client.get("/stock/below-threshold?threshold=-1", headers=H).status_code == 400
    assert client.get("/stock/below-threshold?threshold=abc", headers=H).status_code == 400


def test_i3_umbral_cero_lista_vacia_200():
    r = client.get("/stock/below-threshold?threshold=0", headers=H)
    assert r.status_code == 200 and r.json() == {"total": 0, "threshold": 0.0, "items": []}


def test_i3_por_centro():
    r = client.get("/stock/below-threshold?threshold=100&plant=C100&limit=50", headers=H).json()
    assert client.get("/stock?plant=C100&limit=50", headers=H).status_code == 200
    assert all(i["totalQuantity"] < 100 for i in r["items"])
    assert client.get("/stock/below-threshold?threshold=100&plant=ZZZ", headers=H).status_code == 404


@pytest.mark.parametrize("m", ["post", "put", "delete", "patch"])
def test_solo_lectura_405(m):
    for path in ("/stock", "/stock/below-threshold"):
        r = getattr(client, m)(path, headers=H)
        assert r.status_code == 405 and r.json()["code"] == "METHOD_NOT_ALLOWED"
