# PoC Agente DISRUKTECH (DEMO)

Asistente de compras e inventarios en Microsoft Copilot Studio sobre una API REST de solo lectura con datos ficticios.
Basado en el SOW v1.0 (20/oct/2026). Sin SAP real, sin escritura, sin produccion.

## Estructura
- `inc0/` alcance, condiciones de inicio, contrato `openapi.json` y `schema.sql` (incremento 0)
- `api/` API FastAPI + seed SQLite + pruebas (incremento 1: compras C1-C3)

## Ejecucion local
```bash
cd api
pip install -r requirements.txt
python -m app.seed --reset          # crea demo.db con datos sinteticos reproducibles
API_KEY=cambia-esto uvicorn app.main:app --port 8000
curl -H "X-API-Key: cambia-esto" "localhost:8000/purchase-orders?status=open"
python -m pytest -q
```
`API_KEY` es obligatoria (sin ella la API responde 500). Nunca la suba al repositorio.

## Estado por incremento
| Inc | Contenido | Estado |
|---|---|---|
| 0 | Alcance, OpenAPI v1, esquema | Hecho (pendiente aprobacion de Valtre) |
| 1 | Seed completo + API compras (C1-C3) + API key + pruebas | Hecho en local; falta agente (requiere tenant) |
| 2 | API inventarios (I1-I3) + agente | Pendiente |
| 3 | Errores, guion y ensayo | Pendiente |
