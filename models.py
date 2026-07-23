from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PlantPhase:
    id: Optional[int] = None
    plant_id: Optional[int] = None
    name: str = ""
    phase_order: int = 0
    duration_min_days: Optional[int] = None
    duration_max_days: Optional[int] = None
    light_indoor: str = ""
    light_outdoor: str = ""
    water: str = ""
    water_ph_min: Optional[float] = None
    water_ph_max: Optional[float] = None
    temp_day_min: Optional[float] = None
    temp_day_max: Optional[float] = None
    temp_night_min: Optional[float] = None
    temp_night_max: Optional[float] = None
    humidity_min: Optional[float] = None
    humidity_max: Optional[float] = None
    notes: str = ""


@dataclass
class Plant:
    id: Optional[int] = None
    name: str = ""
    plant_group: str = ""
    month_plant_min: Optional[int] = None
    month_plant_max: Optional[int] = None
    siembra_semillero: bool = False
    siembra_directa: bool = False
    tiempo_cosechar: Optional[int] = None
    clima_templado: bool = False
    clima_frio: bool = False
    fase_cosechar: str = ""
    phases: list[PlantPhase] = field(default_factory=list)


@dataclass
class GerminationPlant:
    id: Optional[int] = None
    plant_id: int = 0
    plant_name: str = ""
    name: str = ""
    germination_date: str = ""
    notes: str = ""


PHASE_COLORS = {
    "germinación": "#4CAF50",
    "germinacion": "#4CAF50",
    "plántula": "#81C784",
    "plantula": "#81C784",
    "vegetativa": "#2E7D32",
    "floración": "#FF9800",
    "floracion": "#FF9800",
    "cosecha": "#795548",
}
