# Conector personalizado para Power Platform (Copilot Studio)

Archivos:
- `apiDefinition.swagger.json`: Swagger 2.0 generado con `scripts/openapi3_to_swagger2.py` (no editar a mano).
- `apiProperties.json`: propiedades del conector (clave de API en la cabecera `X-API-Key`).

Restricciones de Power Platform aplicadas: resúmenes ≤ 80 caracteres, `operationId` únicos, `x-ms-summary` en parámetros, esquema https.

## Importar
**Portal:** Power Apps → Datos → Conectores personalizados → Nuevo → Importar un archivo OpenAPI → `apiDefinition.swagger.json`. En *Seguridad*: clave de API, etiqueta `API Key`, parámetro `X-API-Key`, ubicación *Header*. Probar `getHealth`.

**CLI (`paconn`):** `paconn create --api-prop apiProperties.json --api-def apiDefinition.swagger.json`.

## Estado de validación
- Validado estructuralmente con `openapi-spec-validator` y por pruebas automáticas (sincronía con el contrato y restricciones).
- **No validado en un tenant real**: la importación, la política DLP y el uso desde el agente quedan pendientes de Valtre.
- Con el host real: `python scripts/openapi3_to_swagger2.py --host <host>`.
