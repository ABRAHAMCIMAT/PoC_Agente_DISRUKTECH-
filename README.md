# PoC Agente DISRUKTECH (DEMO)

Asistente de compras e inventarios en Microsoft Copilot Studio sobre una API REST de solo lectura con datos ficticios.
Basado en el SOW v1.0 (20/oct/2026). Sin SAP real, sin escritura, sin produccion.

## Estructura
- `render.yaml`, `api/fly.toml`, `docs/despliegue.md` despliegue gratuito (Render / Fly / Azure)
- `.github/workflows/ci.yml` CI: pruebas + ensayo de demo en cada PR
- `docs/powerplatform/` conector personalizado (Swagger 2.0 generado + propiedades)
- `docs/` configuración del agente de Copilot Studio y guion de demo
- `scripts/smoke_demo.py` ensayo automático de las 6 consultas + 2 errores
- `api/Dockerfile` imagen lista para hosting (inyectar `API_KEY` como secreto)
- `inc0/` alcance, condiciones de inicio, contrato `openapi.json` y `schema.sql` (incremento 0)
- `api/` API FastAPI + seed SQLite + pruebas (incremento 1: compras C1-C3; incremento 2: inventarios I1-I3)

## Ejecucion local
```bash
cd api
pip install --require-hashes --only-binary :all: -r requirements.lock   # o: pip install -r requirements.txt
python -m app.seed --reset          # crea demo.db con datos sinteticos reproducibles
API_KEY=cambia-esto uvicorn app.main:app --port 8000
curl -H "X-API-Key: cambia-esto" "localhost:8000/purchase-orders?status=open"
curl -H "X-API-Key: cambia-esto" "localhost:8000/stock/below-threshold?threshold=100"
python -m pytest -q
```
`API_KEY` es obligatoria (sin ella la API responde 500). Nunca la suba al repositorio.

## Estado por incremento
| Inc | Contenido | Estado |
|---|---|---|
| 0 | Alcance, OpenAPI v1, esquema | Hecho (pendiente aprobacion de Valtre) |
| 1 | Seed completo + API compras (C1-C3) + API key + pruebas | Hecho en local; falta agente (requiere tenant) |
| 2 | API inventarios (I1-I3) con pruebas (29 en total) | Hecho en local; falta agente (requiere tenant) |
| 3 | Contrato, Dockerfile, ensayo automatico, guion y config del agente | Hecho; falta ejecutar en el tenant |
| 4 | Despliegue gratuito, CI y conector Power Platform | Hecho; sin validar en tenant ni hosting reales |

Dependencias: `requirements.in` / `requirements-runtime.in` son las fuentes; los `.lock` llevan versiones y hashes (regenerar con `pip-compile --generate-hashes`).
