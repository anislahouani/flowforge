from pydantic import BaseModel, Field


class SimulationConfig(BaseModel):
    simulation_hours: int = Field(gt=0)

    orders_per_hour: float = Field(gt=0)

    picking_stations: int = Field(gt=0)
    packing_stations: int = Field(gt=0)

    average_picking_time_minutes: float = Field(gt=0)
    average_packing_time_minutes: float = Field(gt=0)

    random_seed: int = Field(default=42, ge=0)

class ScenarioComparisonRequest(BaseModel):
    baseline: SimulationConfig
    candidate: SimulationConfig