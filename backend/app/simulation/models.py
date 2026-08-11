from pydantic import BaseModel, Field


class SimulationConfig(BaseModel):
    simulation_hours: int = Field(gt=0)

    orders_per_hour: float = Field(gt=0)

    picking_stations: int = Field(gt=0)
    packing_stations: int = Field(gt=0)

    average_picking_time_minutes: float = Field(gt=0)
    average_packing_time_minutes: float = Field(gt=0)

    random_seed: int = Field(default=42, ge=0)

    picking_station_cost_per_hour: float = Field(default=25, ge=0)
    packing_station_cost_per_hour: float = Field(default=25, ge=0)

class ScenarioComparisonRequest(BaseModel):
    baseline: SimulationConfig
    candidate: SimulationConfig

class SimulationResult(BaseModel):
    completed_orders: int
    throughput_per_hour: float
    average_lead_time_minutes: float
    average_picking_wait_minutes: float
    average_packing_wait_minutes: float
    bottleneck: str
    operating_cost: float

class ScenarioImprovement(BaseModel):
    throughput_per_hour: float
    average_lead_time_minutes: float
    average_picking_wait_minutes: float
    average_packing_wait_minutes: float

class ScenarioComparisonResult(BaseModel):
    baseline: SimulationResult
    candidate: SimulationResult
    improvement: ScenarioImprovement

class ReplicationRequest(BaseModel):
    config: SimulationConfig
    replications: int = Field(default=10, ge=2, le=100)

class ReplicationResult(BaseModel):
    replications: int
    average_throughput_per_hour: float
    average_lead_time_minutes: float
    average_picking_wait_minutes: float
    average_packing_wait_minutes: float
    throughput_std_dev: float
    lead_time_std_dev_minutes: float

class StatisticalComparisonRequest(BaseModel):
    baseline: SimulationConfig
    candidate: SimulationConfig
    replications: int = Field(default=10, ge=2, le=100)

    max_cost_per_additional_order: float = Field(
        default=100,
        gt=0
    )

class OptimizationRequest(BaseModel):
    base_config: SimulationConfig

    min_packing_stations: int = Field(default=1, ge=1)
    max_packing_stations: int = Field(default=6, ge=1)

    replications: int = Field(default=10, ge=2, le=100)

    max_cost_per_additional_order: float = Field(
        default=100,
        gt=0
    )