from fastapi import FastAPI
from backend.app.simulation.models import (
    ReplicationRequest,
    ReplicationResult,
    ScenarioComparisonRequest,
    ScenarioComparisonResult,
    SimulationConfig,
    SimulationResult,
    StatisticalComparisonRequest,
)
from backend.app.simulation.engine import (
    compare_replications,
    run_replications,
    run_simulation,
)

app = FastAPI(title="FlowForge API", version="0.1.0")

@app.get("/health")

def health_check():
    return { "status": "ok", "service": "flowforge-api" } 

@app.post("/simulation/validate")
def validate_simulation(config: SimulationConfig):
    return {
        "valid": True,
        "config": config
    }

@app.post(
    "/simulation/run",
    response_model=SimulationResult,
)
def run(config: SimulationConfig):
    return run_simulation(config)

@app.post(
    "/simulation/compare",
    response_model=ScenarioComparisonResult,
)
def compare_simulations(request: ScenarioComparisonRequest):
    baseline_result = run_simulation(request.baseline)
    candidate_result = run_simulation(request.candidate)

    return {
        "baseline": baseline_result,
        "candidate": candidate_result,
        "improvement": {
            "throughput_per_hour": round(
                candidate_result["throughput_per_hour"]
                - baseline_result["throughput_per_hour"],
                2,
            ),
            "average_lead_time_minutes": round(
                baseline_result["average_lead_time_minutes"]
                - candidate_result["average_lead_time_minutes"],
                2,
            ),
            "average_picking_wait_minutes": round(
                baseline_result["average_picking_wait_minutes"]
                - candidate_result["average_picking_wait_minutes"],
                2,
            ),
            "average_packing_wait_minutes": round(
                baseline_result["average_packing_wait_minutes"]
                - candidate_result["average_packing_wait_minutes"],
                2,
            ),
        },
    }

@app.post(
    "/simulation/replications",
    response_model=ReplicationResult,
)
def run_multiple_replications(request: ReplicationRequest):
    return run_replications(
        request.config,
        request.replications,
    )

@app.post("/simulation/compare-replications")
def compare_multiple_replications(
    request: StatisticalComparisonRequest,
):
    return compare_replications(
        request.baseline,
        request.candidate,
        request.replications,
        request.max_cost_per_additional_order,
    )
