from backend.app.simulation.engine import (
    compare_replications,
    optimize_packing_capacity,
    run_simulation,
)
from backend.app.simulation.models import SimulationConfig


def test_simulation_is_reproducible():
    config = SimulationConfig(
        simulation_hours=8,
        orders_per_hour=20,
        picking_stations=4,
        packing_stations=4,
        average_picking_time_minutes=4,
        average_packing_time_minutes=5,
        random_seed=42,
        picking_station_cost_per_hour=25,
        packing_station_cost_per_hour=25,
    )

    first_result = run_simulation(config)
    second_result = run_simulation(config)

    assert first_result == second_result

def test_operating_cost_is_calculated_correctly():
    config = SimulationConfig(
        simulation_hours=8,
        orders_per_hour=20,
        picking_stations=4,
        packing_stations=4,
        average_picking_time_minutes=4,
        average_packing_time_minutes=5,
        random_seed=42,
        picking_station_cost_per_hour=25,
        packing_station_cost_per_hour=25,
    )

    result = run_simulation(config)

    assert result["operating_cost"] == 1600

def test_packing_bottleneck_is_detected():
    config = SimulationConfig(
        simulation_hours=8,
        orders_per_hour=20,
        picking_stations=4,
        packing_stations=1,
        average_picking_time_minutes=4,
        average_packing_time_minutes=5,
        random_seed=42,
        picking_station_cost_per_hour=25,
        packing_station_cost_per_hour=25,
    )

    result = run_simulation(config)

    assert result["bottleneck"] == "packing"

def test_optimizer_recommends_four_packing_stations():
    config = SimulationConfig(
        simulation_hours=8,
        orders_per_hour=20,
        picking_stations=4,
        packing_stations=2,
        average_picking_time_minutes=4,
        average_packing_time_minutes=5,
        random_seed=42,
        picking_station_cost_per_hour=25,
        packing_station_cost_per_hour=25,
    )

    result = optimize_packing_capacity(
        base_config=config,
        min_packing_stations=1,
        max_packing_stations=6,
        replications=10,
        max_cost_per_additional_order=100,
    )

    assert result["recommended"] is not None
    assert result["recommended"]["packing_stations"] == 4

def test_cost_threshold_changes_recommendation():
    baseline = SimulationConfig(
        simulation_hours=8,
        orders_per_hour=20,
        picking_stations=4,
        packing_stations=2,
        average_picking_time_minutes=4,
        average_packing_time_minutes=5,
        random_seed=42,
        picking_station_cost_per_hour=25,
        packing_station_cost_per_hour=25,
    )

    candidate = baseline.model_copy(
        update={"packing_stations": 4}
    )

    permissive_result = compare_replications(
        baseline,
        candidate,
        replications=10,
        max_cost_per_additional_order=100,
    )

    strict_result = compare_replications(
        baseline,
        candidate,
        replications=10,
        max_cost_per_additional_order=50,
    )

    assert permissive_result["recommendation"] == "candidate"
    assert strict_result["recommendation"] == "tradeoff"