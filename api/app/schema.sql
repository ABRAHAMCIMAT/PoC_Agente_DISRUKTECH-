-- Modelo de datos DEMO (ficticio). Nombres inspirados en SAP; sin equivalencia certificada.
-- Compatible con SQLite y PostgreSQL (tipos basicos).

CREATE TABLE supplier (          -- LFA1
  supplier_id   TEXT PRIMARY KEY,         -- LIFNR  ej. V-1001
  name          TEXT NOT NULL,
  country       TEXT NOT NULL
);

CREATE TABLE plant (             -- T001W
  plant_id      TEXT PRIMARY KEY,         -- WERKS  ej. C100
  name          TEXT NOT NULL
);

CREATE TABLE material (          -- MARA/MAKT
  material_id   TEXT PRIMARY KEY,         -- MATNR  ej. M-1001
  description   TEXT NOT NULL,
  uom           TEXT NOT NULL             -- UN, KG, M, L
);

CREATE TABLE purchase_order (    -- EKKO
  po_number     TEXT PRIMARY KEY CHECK (po_number GLOB '45[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
  supplier_id   TEXT NOT NULL REFERENCES supplier(supplier_id),
  order_date    DATE NOT NULL,
  status        TEXT NOT NULL CHECK (status IN ('ABIERTA','PARCIAL','CERRADA','BLOQUEADA')),
  currency      TEXT NOT NULL DEFAULT 'USD'
);

CREATE TABLE purchase_order_item (  -- EKPO
  po_number     TEXT NOT NULL REFERENCES purchase_order(po_number),
  line          INTEGER NOT NULL,
  material_id   TEXT NOT NULL REFERENCES material(material_id),
  plant_id      TEXT NOT NULL REFERENCES plant(plant_id),
  quantity      NUMERIC NOT NULL CHECK (quantity > 0),
  received_qty  NUMERIC NOT NULL DEFAULT 0 CHECK (received_qty >= 0 AND received_qty <= quantity),
  net_price     NUMERIC NOT NULL CHECK (net_price >= 0),
  delivery_date DATE NOT NULL,
  PRIMARY KEY (po_number, line)
);

CREATE TABLE stock (             -- MARD
  material_id   TEXT NOT NULL REFERENCES material(material_id),
  plant_id      TEXT NOT NULL REFERENCES plant(plant_id),
  quantity      NUMERIC NOT NULL CHECK (quantity >= 0),
  PRIMARY KEY (material_id, plant_id)
);

CREATE INDEX ix_po_status   ON purchase_order(status);
CREATE INDEX ix_po_supplier ON purchase_order(supplier_id);
CREATE INDEX ix_stock_plant ON stock(plant_id);

-- Regla derivada (RN-HU-04): totalAmount = SUM(quantity * net_price) por orden.
-- Regla derivada: "open" = status IN ('ABIERTA','PARCIAL').
-- Reglas de seed (HU-03): 10-25 ordenes abiertas; >=5 materiales con total < 100; integridad referencial completa.
