# Incremento 0: Alcance congelado y accesos (borrador para aprobación de Valtre)

Estado: BORRADOR. Pendiente de aprobación escrita de Valtre. Ver el estado de las condiciones de inicio abajo.

## 1. Condiciones de inicio del calendario (SOW §6, §10)

| # | Condición | Responsable | Estado |
|---|---|---|---|
| 1 | Alcance confirmado por escrito (este documento) | Valtre | Pendiente |
| 2 | Autorización comercial y pago USD 1,500 | Valtre | Pendiente |
| 3 | Licencia de Copilot Studio y tenant | Valtre | Pendiente |
| 4 | Entorno Power Platform y permisos de creador | Valtre | Pendiente |
| 5 | Política DLP: conector personalizado / HTTP / Power Automate permitido | Valtre | Pendiente |
| 6 | Hosting gratuito o aportado para la API | Valtre / DISRUKTECH | Pendiente |
| 7 | Validación de las 6 consultas | Valtre | Pendiente |
| 8 | Fecha tentativa de demo (semana 3) | Valtre | Pendiente |

Propuesta vigente hasta el 4/nov/2026 (15 días desde el 20/oct).

## 2. Las 6 consultas (lista cerrada propuesta)

| Id | Consulta | Operación OpenAPI | Parámetros | Si falta un parámetro |
|---|---|---|---|---|
| C1 | Órdenes de compra abiertas | `listPurchaseOrders` | status=open | No aplica |
| C2 | Órdenes por proveedor | `listPurchaseOrders` | supplier | El agente pregunta el proveedor |
| C3 | Detalle y estado de una orden | `getPurchaseOrder` | poNumber | El agente pregunta el número |
| I1 | Existencia por material | `getStock` | material | El agente pregunta el material |
| I2 | Existencia por centro | `getStock` | plant | El agente pregunta el centro |
| I3 | Materiales bajo umbral | `getStockBelowThreshold` | threshold, plant (opcional) | El agente pregunta el umbral |

## 3. Decisiones de diseño tomadas por defecto (a confirmar o cambiar)

| Tema | Decisión por defecto | Pregunta relacionada |
|---|---|---|
| "Orden abierta" | Estado ABIERTA o PARCIAL | Q-13 |
| Umbral I3 | Lo indica el usuario en la conversación, sin valor por defecto | Q-14 |
| Idioma | Español | Q-06 |
| Límite de filas | 10 por respuesta, más el total | n/a |
| Autenticación | API key en cabecera `X-API-Key` | Q-04 |
| Stack API | Python + FastAPI | Q-08 |
| BD | SQLite con script de seed (PostgreSQL si el hosting lo exige) | Q-08 |
| Orquestación del agente | Conector personalizado importado desde OpenAPI | Q-03 |

## 4. Entregables del incremento 0

- `openapi.json`: contrato v1 con 5 operaciones (6 consultas, ya que C1 y C2 comparten operación).
- `schema.sql`: modelo de datos con integridad referencial y reglas de seed.
- Este documento: alcance, condiciones y decisiones.

Cambios posteriores a las 6 consultas se tratan como cambio de alcance (SOW §10).

## 5. Preguntas bloqueantes (responder en los días 1–2)

1. **Q-03:** ¿El tenant permite conectores personalizados, nodo HTTP o Power Automate?
2. **Q-04:** ¿Qué autenticación permite el tenant (API key, OAuth, Entra ID)?
3. **Q-07:** ¿Dónde se aloja la API sin costo y quién provee la suscripción?
4. **Q-09:** ¿La API puede ser pública con HTTPS o debe ser privada?
5. **Q-12:** ¿Se aprueban las 6 consultas de la sección 2?

## 6. Pruebas de verificación de accesos (se ejecutan cuando haya tenant)

1. Crear un agente vacío en el entorno indicado.
2. Importar `openapi.json` como conector personalizado. Debe generar 5 operaciones sin errores.
3. Crear una conexión con la API key de prueba.
4. Llamar `getHealth` desde el panel de prueba del conector.
5. Publicar el agente en el canal de demo y confirmar que los usuarios previstos pueden abrirlo.
