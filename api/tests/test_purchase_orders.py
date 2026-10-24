import os
import tempfile

import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "test-key"
os.environ["DB_PATH"] = os.path.join(tempfile.gettempdir(), "test_demo.db")

from app.main import app  # noqa: E402
from app.seed import seed  # noqa: E402

H = {"X-API-Key": "test-key"}


@pytest.fixture(scope="module", autouse=True)
def _seed():
    seed(reset=True)


client = TestClient(app, raise_server_exceptions=False)


def test_health_sin_credencial():
    assert client.get("/health").json() == {"status": "ok"}


def test_sin_credencial_401():
    r = client.get("/purchase-orders")
    assert r.status_code == 401 and r.json()["code"] == "UNAUTHORIZED"
    assert client.get("/purchase-orders", headers={"X-API-Key": "mala"}).status_code == 401


def test_c1_abiertas_entre_10_y_25():
    r = client.get("/purchase-orders?limit=50", headers=H).json()
    assert 10 <= r["total"] <= 25
    assert all(i["status"] in ("ABIERTA", "PARCIAL") for i in r["items"])


def test_limite_por_defecto_10_y_total():
    r = client.get("/purchase-orders", headers=H).json()
    assert len(r["items"]) == 10 and r["total"] > 10


def test_c2_por_id_y_por_nombre():
    by_id = client.get("/purchase-orders?status=ABIERTA&supplier=V-1001&limit=50", headers=H).json()
    assert all(i["supplierId"] == "V-1001" for i in by_id["items"])
    by_name = client.get("/purchase-orders?supplier=aceros&status=CERRADA&limit=50", headers=H).json()
    names = {i["supplierName"] for i in by_name["items"]}
    assert names <= {"Aceros Demo S.A.", "Aceros del Norte Demo"} and len(names) == 2  # ambiguo


def test_c3_detalle():
    po = client.get("/purchase-orders", headers=H).json()["items"][0]["poNumber"]
    d = client.get(f"/purchase-orders/{po}", headers=H).json()
    assert d["poNumber"] == po and d["items"]
    total = sum(i["quantity"] * i["netPrice"] for i in d["items"])
    assert abs(total - d["totalAmount"]) < 0.05


def test_c3_inexistente_404_e_invalido_400():
    r = client.get("/purchase-orders/4599999999", headers=H)
    assert r.status_code == 404 and r.json()["code"] == "NOT_FOUND"
    assert client.get("/purchase-orders/abc", headers=H).status_code == 400


def test_estado_invalido_400():
    assert client.get("/purchase-orders?status=xx", headers=H).status_code == 400
    assert client.get("/purchase-orders?limit=0", headers=H).status_code == 400


@pytest.mark.parametrize("m", ["post", "put", "delete", "patch"])
def test_solo_lectura_405(m):
    r = getattr(client, m)("/purchase-orders", headers=H)
    assert r.status_code == 405 and r.json()["code"] == "METHOD_NOT_ALLOWED"


def test_seed_cumple_reglas_hu03():
    from app.db import connect
    c = connect()
    assert c.execute("PRAGMA foreign_key_check").fetchall() == []
    low = c.execute("SELECT COUNT(*) FROM (SELECT material_id FROM stock GROUP BY material_id HAVING SUM(quantity) < 100)").fetchone()[0]
    assert low >= 5
    assert c.execute("SELECT COUNT(*) FROM stock WHERE quantity < 0").fetchone()[0] == 0
