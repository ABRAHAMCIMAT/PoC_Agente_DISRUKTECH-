# Guion de demo (SOW §7: conformidad por ejecución observable)

Datos 100 % ficticios. Duración sugerida: 15 min. Antes de empezar, ejecutar `scripts/smoke_demo.py` contra la API desplegada (calienta el hosting y confirma 9/9).

| # | Consulta | Frase de ejemplo | Resultado esperado |
|---|---|---|---|
| C1 | Órdenes abiertas | "¿Qué órdenes de compra están abiertas?" | 10 de 18 con proveedor, estado e importe |
| C2 | Por proveedor | "Muéstrame las órdenes del proveedor Aceros" | Dos proveedores coinciden: el agente ofrece elegir |
| C3 | Detalle | "Dame el estado de la orden 4500001010" | Estado y posiciones con cantidades y recibido |
| I1 | Por material | "¿Cuánto hay del material M-1001?" | Existencia por centro, con unidad |
| I2 | Por centro | "Existencias del centro C100" | Hasta 10 materiales, con el total |
| I3 | Bajo umbral | "Materiales con menos de 100 unidades" | Lista de materiales; sin número, el agente pregunta el umbral |
| E1 | Error: no existe | "Estado de la orden 4599999999" | "No encontré la orden…" |
| E2 | Fuera de alcance | "Crea una orden de compra" | "Esta demo es solo de consulta…" |

Cierre: Valtre confirma por escrito que las 6 consultas se ejecutaron en vivo.
