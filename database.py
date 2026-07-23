import sqlite3
import json
import os
from models import Plant, PlantPhase, GerminationPlant, asdict


DB_PATH = os.path.join(os.path.dirname(__file__), "plants.db")


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = _dict_factory
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                plant_group TEXT DEFAULT '',
                month_plant_min INTEGER,
                month_plant_max INTEGER,
                siembra_semillero INTEGER DEFAULT 0,
                siembra_directa INTEGER DEFAULT 0,
                tiempo_cosechar INTEGER,
                clima_templado INTEGER DEFAULT 0,
                clima_frio INTEGER DEFAULT 0,
                fase_cosechar TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS plant_phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                name TEXT NOT NULL DEFAULT '',
                phase_order INTEGER DEFAULT 0,
                duration_min_days INTEGER,
                duration_max_days INTEGER,
                light_indoor TEXT DEFAULT '',
                light_outdoor TEXT DEFAULT '',
                water TEXT DEFAULT '',
                water_ph_min REAL,
                water_ph_max REAL,
                temp_day_min REAL,
                temp_day_max REAL,
                temp_night_min REAL,
                temp_night_max REAL,
                humidity_min REAL,
                humidity_max REAL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS germination_plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL,
                name TEXT NOT NULL DEFAULT '',
                germination_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            );
        """)
        self.conn.commit()

    # ---------- Plant CRUD ----------

    def save_plant(self, plant: Plant) -> int:
        if plant.id is None:
            cur = self.conn.execute(
                """INSERT INTO plants (name, plant_group, month_plant_min, month_plant_max,
                   siembra_semillero, siembra_directa, tiempo_cosechar,
                   clima_templado, clima_frio, fase_cosechar)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (plant.name, plant.plant_group, plant.month_plant_min,
                 plant.month_plant_max, int(plant.siembra_semillero),
                 int(plant.siembra_directa), plant.tiempo_cosechar,
                 int(plant.clima_templado), int(plant.clima_frio),
                 plant.fase_cosechar)
            )
            plant.id = cur.lastrowid
        else:
            self.conn.execute(
                """UPDATE plants SET name=?, plant_group=?, month_plant_min=?,
                   month_plant_max=?, siembra_semillero=?, siembra_directa=?,
                   tiempo_cosechar=?, clima_templado=?, clima_frio=?,
                   fase_cosechar=? WHERE id=?""",
                (plant.name, plant.plant_group, plant.month_plant_min,
                 plant.month_plant_max, int(plant.siembra_semillero),
                 int(plant.siembra_directa), plant.tiempo_cosechar,
                 int(plant.clima_templado), int(plant.clima_frio),
                 plant.fase_cosechar, plant.id)
            )
            self.conn.execute("DELETE FROM plant_phases WHERE plant_id=?", (plant.id,))
        for ph in plant.phases:
            self.conn.execute(
                """INSERT INTO plant_phases (plant_id, name, phase_order,
                   duration_min_days, duration_max_days, light_indoor, light_outdoor,
                   water, water_ph_min, water_ph_max, temp_day_min, temp_day_max,
                   temp_night_min, temp_night_max, humidity_min, humidity_max, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (plant.id, ph.name, ph.phase_order,
                 ph.duration_min_days, ph.duration_max_days,
                 ph.light_indoor, ph.light_outdoor, ph.water,
                 ph.water_ph_min, ph.water_ph_max,
                 ph.temp_day_min, ph.temp_day_max,
                 ph.temp_night_min, ph.temp_night_max,
                 ph.humidity_min, ph.humidity_max, ph.notes)
            )
        self.conn.commit()
        return plant.id

    def delete_plant(self, plant_id: int):
        self.conn.execute("DELETE FROM plants WHERE id=?", (plant_id,))
        self.conn.commit()

    def get_plant(self, plant_id: int) -> Plant | None:
        row = self.conn.execute("SELECT * FROM plants WHERE id=?", (plant_id,)).fetchone()
        if not row:
            return None
        return self._row_to_plant(row)

    def get_all_plants(self) -> list[Plant]:
        rows = self.conn.execute("SELECT * FROM plants ORDER BY name").fetchall()
        return [self._row_to_plant(r) for r in rows]

    def _row_to_plant(self, row: dict) -> Plant:
        phases = [
            PlantPhase(**ph) for ph in self.conn.execute(
                "SELECT * FROM plant_phases WHERE plant_id=? ORDER BY phase_order",
                (row["id"],)
            ).fetchall()
        ]
        row = dict(row)
        return Plant(
            id=row["id"],
            name=row["name"],
            plant_group=row["plant_group"] or "",
            month_plant_min=row["month_plant_min"],
            month_plant_max=row["month_plant_max"],
            siembra_semillero=bool(row["siembra_semillero"]),
            siembra_directa=bool(row["siembra_directa"]),
            tiempo_cosechar=row["tiempo_cosechar"],
            clima_templado=bool(row["clima_templado"]),
            clima_frio=bool(row["clima_frio"]),
            fase_cosechar=row["fase_cosechar"] or "",
            phases=phases,
        )

    # ---------- GerminationPlant CRUD ----------

    def save_germination_plant(self, gp: GerminationPlant) -> int:
        if gp.id is None:
            cur = self.conn.execute(
                "INSERT INTO germination_plants (plant_id, name, germination_date, notes) VALUES (?, ?, ?, ?)",
                (gp.plant_id, gp.name, gp.germination_date, gp.notes)
            )
            gp.id = cur.lastrowid
        else:
            self.conn.execute(
                "UPDATE germination_plants SET plant_id=?, name=?, germination_date=?, notes=? WHERE id=?",
                (gp.plant_id, gp.name, gp.germination_date, gp.notes, gp.id)
            )
        self.conn.commit()
        return gp.id

    def delete_germination_plant(self, gp_id: int):
        self.conn.execute("DELETE FROM germination_plants WHERE id=?", (gp_id,))
        self.conn.commit()

    def get_all_germination_plants(self) -> list[GerminationPlant]:
        rows = self.conn.execute(
            """SELECT g.*, p.name as plant_name
               FROM germination_plants g
               JOIN plants p ON p.id = g.plant_id
               ORDER BY g.germination_date"""
        ).fetchall()
        return [GerminationPlant(**r) for r in rows]

    # ---------- JSON Import/Export ----------

    def export_to_json(self, filepath: str):
        plants = self.get_all_plants()
        data = []
        for p in plants:
            d = asdict(p)
            d.pop("id", None)
            for ph in d.get("phases", []):
                ph.pop("id", None)
                ph.pop("plant_id", None)
            data.append(d)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filepath: str) -> int:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            phases_data = item.pop("phases", [])
            plant = Plant(**item)
            plant.phases = [PlantPhase(**ph) for ph in phases_data]
            try:
                self.save_plant(plant)
                count += 1
            except sqlite3.IntegrityError:
                pass
        return count

    def close(self):
        self.conn.close()
