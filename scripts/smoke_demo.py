"""Ensayo automatico del guion de demo (6 consultas + 2 casos de error) contra una API en ejecucion.
Uso: API_URL=http://localhost:8000 API_KEY=... python scripts/smoke_demo.py
Sale con codigo 1 si algun paso falla."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
KEY = os.environ.get("API_KEY", "")


def call(path):
    req = urllib.request.Request(URL + path, headers={"X-API-Key": KEY})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.load(r), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, json.load(e), time.time() - t


def main():
    results = []

    def step(name, path, ok):
        status, body, dt = call(path)
        good = bool(ok(status, body))
        results.append(good)
        print(f"{'OK  ' if good else 'FAIL'} {name:<38} {status} {dt*1000:5.0f} ms")
        return body

    step("health", "/health", lambda s, b: s == 200)
    o = step("C1 ordenes abiertas", "/purchase-orders?status=open",
             lambda s, b: s == 200 and b["total"] > 0 and len(b["items"]) <= 10)
    step("C2 ordenes por proveedor", "/purchase-orders?supplier=V-1001",
         lambda s, b: s == 200 and all(i["supplierId"] == "V-1001" for i in b["items"]))
    po = o["items"][0]["poNumber"] if o.get("items") else "4500001001"
    step("C3 detalle de orden", f"/purchase-orders/{po}", lambda s, b: s == 200 and b["items"])
    step("I1 existencia por material", "/stock?material=M-1001", lambda s, b: s == 200 and b["total"] > 0)
    step("I2 existencia por centro", "/stock?plant=C100", lambda s, b: s == 200 and b["total"] > 0)
    step("I3 materiales bajo umbral 100", "/stock/below-threshold?threshold=100",
         lambda s, b: s == 200 and b["total"] >= 3)
    step("ERR orden inexistente", "/purchase-orders/4599999999", lambda s, b: s == 404 and b["code"] == "NOT_FOUND")
    step("ERR umbral faltante", "/stock/below-threshold", lambda s, b: s == 400 and b["code"] == "BAD_REQUEST")
    print(f"\n{sum(results)}/{len(results)} pasos correctos")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
