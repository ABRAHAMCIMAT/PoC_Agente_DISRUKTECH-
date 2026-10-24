"""API REST DEMO de solo lectura: Compras (incremento 1). Datos ficticios."""
import hmac
import os
import re

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .db import connect

app = FastAPI(title="DISRUKTECH PoC - API de Compras e Inventarios (DEMO)", version="1.0.0")

OPEN = ("ABIERTA", "PARCIAL")
STATUSES = ("ABIERTA", "PARCIAL", "CERRADA", "BLOQUEADA")
PO_RE = re.compile(r"^45[0-9]{8}$")


# ---------- errores uniformes {code, message} ----------
def err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"code": code, "message": message})


@app.exception_handler(StarletteHTTPException)
async def http_exc(_: Request, exc: StarletteHTTPException):
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        return err(exc.status_code, exc.detail["code"], exc.detail["message"])
    mapping = {404: ("NOT_FOUND", "Recurso no encontrado."),
               405: ("METHOD_NOT_ALLOWED", "Metodo no permitido: la API es de solo lectura.")}
    code, msg = mapping.get(exc.status_code, ("INTERNAL", "Error inesperado."))
    return err(exc.status_code, code, msg)


@app.exception_handler(RequestValidationError)
async def validation_exc(_: Request, exc: RequestValidationError):
    fields = ", ".join(str(e["loc"][-1]) for e in exc.errors())
    return err(400, "BAD_REQUEST", f"Parametros invalidos o faltantes: {fields}.")


@app.exception_handler(Exception)
async def unhandled(_: Request, exc: Exception):
    return err(500, "INTERNAL", "Error interno del servicio.")


def fail(status: int, code: str, message: str):
    raise HTTPException(status_code=status, detail={"code": code, "message": message})


# ---------- seguridad: API key (HU-06) ----------
def require_key(x_api_key: str | None = Header(default=None)):
    expected = os.environ.get("API_KEY", "")
    if not expected:
        fail(500, "INTERNAL", "API_KEY no configurada en el servidor.")
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        fail(401, "UNAUTHORIZED", "Credencial invalida o ausente.")


# ---------- endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}


SUMMARY_SQL = """
SELECT po.po_number AS poNumber, po.supplier_id AS supplierId, s.name AS supplierName,
       po.order_date AS orderDate, po.status AS status, po.currency AS currency,
       ROUND(COALESCE(SUM(i.quantity * i.net_price), 0), 2) AS totalAmount
FROM purchase_order po
JOIN supplier s ON s.supplier_id = po.supplier_id
LEFT JOIN purchase_order_item i ON i.po_number = po.po_number
{where}
GROUP BY po.po_number
ORDER BY po.order_date DESC, po.po_number
"""


@app.get("/purchase-orders", dependencies=[Depends(require_key)])
def list_purchase_orders(
    status: str = Query("open"),
    supplier: str | None = Query(None, min_length=1),
    limit: int = Query(10, ge=1, le=50),
):
    if status != "open" and status.upper() not in STATUSES:
        fail(400, "BAD_REQUEST", "Estado invalido. Use open, ABIERTA, PARCIAL, CERRADA o BLOQUEADA.")
    where, params = [], []
    if status == "open":
        where.append("po.status IN (?,?)")
        params += OPEN
    else:
        where.append("po.status = ?")
        params.append(status.upper())
    if supplier:
        where.append("(UPPER(po.supplier_id) = UPPER(?) OR UPPER(s.name) LIKE UPPER(?))")
        params += [supplier, f"%{supplier}%"]
    sql = SUMMARY_SQL.format(where="WHERE " + " AND ".join(where))
    conn = connect()
    try:
        rows = [dict(r) for r in conn.execute(sql, params)]
    finally:
        conn.close()
    return {"total": len(rows), "items": rows[:limit]}


@app.get("/purchase-orders/{po_number}", dependencies=[Depends(require_key)])
def get_purchase_order(po_number: str):
    if not PO_RE.match(po_number):
        fail(400, "BAD_REQUEST", "Numero de orden invalido: debe tener 10 digitos y empezar por 45.")
    conn = connect()
    try:
        head = conn.execute(SUMMARY_SQL.format(where="WHERE po.po_number = ?"), (po_number,)).fetchone()
        if not head:
            fail(404, "NOT_FOUND", f"No encontre la orden {po_number}.")
        items = conn.execute(
            """SELECT i.line, i.material_id AS materialId, m.description AS materialDescription,
                      i.plant_id AS plantId, i.quantity, i.received_qty AS receivedQuantity,
                      m.uom AS uom, i.net_price AS netPrice, i.delivery_date AS deliveryDate
               FROM purchase_order_item i JOIN material m ON m.material_id = i.material_id
               WHERE i.po_number = ? ORDER BY i.line""", (po_number,)).fetchall()
    finally:
        conn.close()
    return {**dict(head), "items": [dict(r) for r in items]}
