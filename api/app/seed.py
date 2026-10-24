"""Carga datos sinteticos (DEMO) y reproducibles. Uso: python -m app.seed [--reset]"""
import random
import sys
from datetime import date, timedelta

from .db import SCHEMA, connect, db_path
import os

SUPPLIERS = [
    ("V-1001", "Aceros Demo S.A.", "MX"), ("V-1002", "Aceros del Norte Demo", "MX"),
    ("V-1003", "Plasticos Andina Demo", "CO"), ("V-1004", "Electro Pacifico Demo", "CL"),
    ("V-1005", "Quimicos Sur Demo", "AR"), ("V-1006", "Empaques Globo Demo", "PE"),
    ("V-1007", "Tornillos y Mas Demo", "MX"), ("V-1008", "Lubricantes Alfa Demo", "CO"),
    ("V-1009", "Maderas Tropicales Demo", "EC"), ("V-1010", "Cables Centro Demo", "PA"),
    ("V-1011", "Logistica Rapida Demo", "MX"), ("V-1012", "Vidrios Cristal Demo", "CL"),
    ("V-1013", "Pinturas Arcoiris Demo", "CO"), ("V-1014", "Textiles Valle Demo", "PE"),
    ("V-1015", "Herramientas Titan Demo", "AR"),
]
PLANTS = [("C100", "Centro Planta Norte"), ("C200", "Centro Planta Sur"),
          ("C300", "Centro Distribucion Este"), ("C400", "Centro Distribucion Oeste")]
MATERIALS = [
    ("Lamina acero 2mm", "KG"), ("Barra acero 12mm", "M"), ("Tornillo M8", "UN"), ("Tuerca M8", "UN"),
    ("Arandela 8mm", "UN"), ("Resina PE", "KG"), ("Pellet PP", "KG"), ("Cable cobre 2.5mm", "M"),
    ("Interruptor 15A", "UN"), ("Tablero electrico", "UN"), ("Solvente industrial", "L"),
    ("Aceite hidraulico", "L"), ("Grasa litio", "KG"), ("Caja carton 40x40", "UN"), ("Film estirable", "UN"),
    ("Pallet madera", "UN"), ("Tabla pino", "M"), ("Vidrio templado 6mm", "UN"), ("Pintura epoxica", "L"),
    ("Barniz", "L"), ("Tela algodon", "M"), ("Hilo poliester", "UN"), ("Llave inglesa", "UN"),
    ("Taladro industrial", "UN"), ("Broca 10mm", "UN"), ("Guante nitrilo", "UN"), ("Casco seguridad", "UN"),
    ("Rodamiento 6204", "UN"), ("Correa trapezoidal", "UN"), ("Filtro de aire", "UN"),
    ("Filtro de aceite", "UN"), ("Valvula bola 1in", "UN"), ("Tubo PVC 2in", "M"), ("Codo PVC 2in", "UN"),
    ("Sellador silicona", "UN"), ("Cinta aislante", "UN"), ("Bateria 12V", "UN"), ("Lampara LED", "UN"),
    ("Motor 1HP", "UN"), ("Reductor 1:10", "UN"),
]


def seed(reset: bool = False) -> dict:
    path = db_path()
    if reset and os.path.exists(path):
        os.remove(path)
    conn = connect()
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    rnd = random.Random(42)
    base = date(2026, 9, 1)

    conn.executemany("INSERT INTO supplier VALUES (?,?,?)", SUPPLIERS)
    conn.executemany("INSERT INTO plant VALUES (?,?)", PLANTS)
    mats = [(f"M-{1001 + i}", d, u) for i, (d, u) in enumerate(MATERIALS)]
    conn.executemany("INSERT INTO material VALUES (?,?,?)", mats)

    # Existencias: cada material en 1-3 centros; 8 materiales con total < 100 (para I3).
    low = {m[0] for m in mats[::5]}  # 8 materiales
    for mid, _, _ in mats:
        for pid in rnd.sample([p[0] for p in PLANTS], rnd.randint(1, 3)):
            qty = rnd.randint(2, 30) if mid in low else rnd.randint(120, 2000)
            conn.execute("INSERT INTO stock VALUES (?,?,?)", (mid, pid, qty))
    # Un caso "trampa": existencia en cero.
    conn.execute("INSERT OR REPLACE INTO stock VALUES (?,?,?)", ("M-1040", "C400", 0))

    # Ordenes: 60 en total; estados con distribucion controlada (18 abiertas = 12 ABIERTA + 6 PARCIAL).
    statuses = ["ABIERTA"] * 12 + ["PARCIAL"] * 6 + ["CERRADA"] * 36 + ["BLOQUEADA"] * 6
    rnd.shuffle(statuses)
    for n, status in enumerate(statuses):
        po = f"45{1001 + n:08d}"
        sup = SUPPLIERS[n % len(SUPPLIERS)][0]
        odate = base + timedelta(days=rnd.randint(0, 45))
        conn.execute("INSERT INTO purchase_order VALUES (?,?,?,?,?)", (po, sup, odate.isoformat(), status, "USD"))
        for line in range(1, rnd.randint(1, 4) + 1):
            mid = rnd.choice(mats)[0]
            qty = rnd.randint(10, 500)
            recv = {"CERRADA": qty, "PARCIAL": rnd.randint(1, qty - 1)}.get(status, 0)
            conn.execute(
                "INSERT INTO purchase_order_item VALUES (?,?,?,?,?,?,?,?)",
                (po, line * 10, mid, rnd.choice(PLANTS)[0], qty, recv,
                 round(rnd.uniform(1.5, 250), 2), (odate + timedelta(days=rnd.randint(7, 30))).isoformat()),
            )
    conn.commit()
    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("supplier", "plant", "material", "purchase_order", "purchase_order_item", "stock")}
    conn.close()
    return counts


if __name__ == "__main__":
    print(seed(reset="--reset" in sys.argv))
