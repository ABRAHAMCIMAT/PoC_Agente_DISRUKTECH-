# Agente de Copilot Studio: configuración (lista para aplicar cuando haya tenant)

Pasos de HU-07 a HU-10. No se pudieron ejecutar: requieren tenant, licencia y permisos de Valtre.

## 1. Conector personalizado
1. Power Apps / Power Automate → Datos → Conectores personalizados → Importar OpenAPI → `inc0/openapi.json`.
2. Reemplazar `servers[0].url` por el host real de la API (HTTPS).
3. Seguridad: clave de API, parámetro `X-API-Key`, ubicación *Header*.
4. Probar `getHealth` y luego `listPurchaseOrders`. Deben generarse 5 operaciones.
5. Si la política DLP bloquea conectores personalizados: usar nodo HTTP con la misma URL y cabecera, o Power Automate.

## 2. Instrucciones del agente (pegar en "Instrucciones")
```
Eres el asistente de consultas de compras e inventarios de la demo DISRUKTECH. Todos los datos son ficticios.
Responde siempre en español, con tono profesional y breve.

Solo puedes resolver estas 6 consultas, usando exclusivamente las acciones disponibles:
1. Órdenes de compra abiertas.            (listPurchaseOrders, status=open)
2. Órdenes de un proveedor.               (listPurchaseOrders, supplier)
3. Detalle y estado de una orden.         (getPurchaseOrder, poNumber)
4. Existencia de un material.             (getStock, material)
5. Existencia de un centro.               (getStock, plant)
6. Materiales bajo un umbral.             (getStockBelowThreshold, threshold)

Reglas:
- Nunca inventes datos. Si la acción no devuelve resultados o falla, dilo con claridad.
- Si falta un parámetro (proveedor, número de orden, material, centro o umbral), pregúntalo una sola vez. Nunca asumas el umbral.
- Muestra como máximo 10 filas y menciona el total ("Mostrando 10 de 18").
- Muestra siempre la unidad de medida de las cantidades y la moneda de los importes.
- Si la consulta es ambigua (varios proveedores o materiales coinciden), muestra las opciones y pide elegir.
- Si te piden crear, modificar, aprobar o borrar algo, responde que esta demo es solo de consulta.
- Si la pregunta está fuera de las 6 consultas, indica qué sí puedes consultar y ofrece ejemplos.
- No muestres errores técnicos, códigos HTTP ni claves.
```

## 3. Temas y acciones
| Tema | Frases de activación (ejemplos) | Acción | Parámetros |
|---|---|---|---|
| Órdenes abiertas | "órdenes abiertas", "qué compras están pendientes" | listPurchaseOrders | status=open |
| Órdenes por proveedor | "órdenes del proveedor Aceros", "compras a V-1003" | listPurchaseOrders | supplier (pregunta si falta) |
| Detalle de orden | "estado de la orden 4500001013" | getPurchaseOrder | poNumber (pregunta si falta) |
| Existencia por material | "cuánto hay del material M-1001", "stock de tornillos" | getStock | material |
| Existencia por centro | "existencias del centro C100" | getStock | plant |
| Bajo umbral | "materiales bajo 50 unidades", "qué está por agotarse" | getStockBelowThreshold | threshold (pregunta si falta), plant opcional |
| Fuera de alcance | (alternativa / fallback) | ninguna | mensaje de capacidades |

## 4. Mensajes de error (HU-10)
| Situación | Respuesta del agente |
|---|---|
| 404 | "No encontré {dato}. Verifique el valor e intente de nuevo." |
| 400 | "Me falta o es inválido {parámetro}. ¿Me lo indica?" |
| 401 / 500 / sin respuesta | "No puedo consultar la información en este momento. Intente más tarde." |
| Lista vacía | "No hay resultados para esa consulta." |
| Escritura solicitada | "Esta demo es solo de consulta; no puedo crear ni modificar datos." |

## 5. Verificación de accesos (incremento 0, sección 6)
Crear agente → importar OpenAPI → crear conexión con la API key → probar `getHealth` → publicar en el canal de demo.
