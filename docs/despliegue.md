# Despliegue gratuito de la API (hosting a elegir)

La API es una imagen Docker (`api/Dockerfile`): genera la BD demo al construir y arranca con `uvicorn` en `$PORT`.
Variable obligatoria: **`API_KEY`** (secreto). Sin ella la API responde 500. Los planes y límites gratuitos cambian: verifíquelos antes de decidir.

| Opción | Archivo | Pasos | Notas |
|---|---|---|---|
| **Render** | `render.yaml` | Dashboard → New → Blueprint → repo → crear. Copiar `API_KEY` generada desde *Environment* | Plan free: el servicio se duerme tras inactividad; la primera llamada puede tardar ~1 min |
| **Fly.io** | `api/fly.toml` | `cd api && fly launch --no-deploy --copy-config && fly secrets set API_KEY=<clave> && fly deploy` | Suele exigir tarjeta; las máquinas se detienen al no tener tráfico (`min_machines_running = 0`) |
| **Azure** | (sin archivo) | App Service for Containers o Container Apps con la imagen del repo; definir `API_KEY` como secreto y `PORT=8000` | Requiere suscripción de Valtre/cliente; el SOW excluye consumo de Azure |

## Después de desplegar
1. `curl https://<host>/health` debe devolver `{"status":"ok"}`.
2. Ensayo: `API_URL=https://<host> API_KEY=<clave> python scripts/smoke_demo.py` (esperado 9/9).
3. Regenerar el contrato de Power Platform con el host real: `python scripts/openapi3_to_swagger2.py --host <host>` (sin `https://`) y actualizar `servers[0].url` en `inc0/openapi.json`.
4. Calentar el servicio unos minutos antes de la demo (arranque en frío).

## Recomendación
Render (Blueprint listo y plan gratuito; confirme sus condiciones vigentes) para la PoC; Azure solo si Valtre ya dispone de suscripción.
No se puede probar la imagen en este entorno (no hay Docker): la primera construcción en el hosting es la prueba.
