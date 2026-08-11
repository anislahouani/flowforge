import random
import simpy
import statistics

from backend.app.simulation.models import SimulationConfig


def run_simulation(config: SimulationConfig):
    random.seed(config.random_seed)

    env = simpy.Environment()

    picking = simpy.Resource(
        env,
        capacity=config.picking_stations
    )

    packing = simpy.Resource(
        env,
        capacity=config.packing_stations
    )

    completed_orders = []

    def process_order(order_id: int):
        created_at = env.now

        # Picking
        picking_queue_entered_at = env.now

        with picking.request() as request:
            yield request

            picking_wait = env.now - picking_queue_entered_at

            picking_time = random.expovariate(
                1 / config.average_picking_time_minutes
            )

            yield env.timeout(picking_time)

        # Packing
        packing_queue_entered_at = env.now

        with packing.request() as request:
            yield request

            packing_wait = env.now - packing_queue_entered_at

            packing_time = random.expovariate(
                1 / config.average_packing_time_minutes
            )

            yield env.timeout(packing_time)

        completed_orders.append({
            "order_id": order_id,
            "lead_time_minutes": env.now - created_at,
            "picking_wait_minutes": picking_wait,
            "packing_wait_minutes": packing_wait
        })



    def generate_orders():
        order_id = 1

        while True:
            env.process(process_order(order_id))
            order_id += 1

            average_interarrival_time = 60 / config.orders_per_hour

            interarrival_time = random.expovariate(
                1 / average_interarrival_time
            )

            yield env.timeout(interarrival_time)

    env.process(generate_orders())

    simulation_duration_minutes = config.simulation_hours * 60

    env.run(until=simulation_duration_minutes)

    if completed_orders:
        average_lead_time = sum(
            order["lead_time_minutes"] for order in completed_orders
        ) / len(completed_orders)

        average_picking_wait = sum(
            order["picking_wait_minutes"] for order in completed_orders
        ) / len(completed_orders)

        average_packing_wait = sum(
            order["packing_wait_minutes"] for order in completed_orders
        ) / len(completed_orders)
    else:
        average_lead_time = 0
        average_picking_wait = 0
        average_packing_wait = 0

    throughput_per_hour = (
        len(completed_orders) / config.simulation_hours
    )

    bottleneck_threshold_minutes = 1.0

    if (
        average_picking_wait < bottleneck_threshold_minutes
        and average_packing_wait < bottleneck_threshold_minutes
    ):
        bottleneck = "none"
    elif average_picking_wait > average_packing_wait:
        bottleneck = "picking"
    else:
        bottleneck = "packing"

    operating_cost = config.simulation_hours * (
    config.picking_stations * config.picking_station_cost_per_hour
    + config.packing_stations * config.packing_station_cost_per_hour
    )

    return {
        "completed_orders": len(completed_orders),
        "throughput_per_hour": round(throughput_per_hour, 2),
        "average_lead_time_minutes": round(average_lead_time, 2),
        "average_picking_wait_minutes": round(average_picking_wait, 2),
        "average_packing_wait_minutes": round(average_packing_wait, 2),
        "bottleneck": bottleneck,
        "operating_cost": round(operating_cost, 2),
    }

def run_replications(
    config: SimulationConfig,
    replications: int,
):
    results = []

    for replication in range(replications):
        replication_config = config.model_copy(
            update={
                "random_seed": config.random_seed + replication
            }
        )

        results.append(
            run_simulation(replication_config)
        )

    average_throughput = sum(
        result["throughput_per_hour"] for result in results
    ) / replications

    average_lead_time = sum(
        result["average_lead_time_minutes"] for result in results
    ) / replications

    average_picking_wait = sum(
        result["average_picking_wait_minutes"] for result in results
    ) / replications

    average_packing_wait = sum(
        result["average_packing_wait_minutes"] for result in results
    ) / replications

    throughputs = [
    result["throughput_per_hour"] for result in results
    ]

    lead_times = [
        result["average_lead_time_minutes"] for result in results
    ]

    throughput_std_dev = statistics.stdev(throughputs)
    lead_time_std_dev = statistics.stdev(lead_times)

    return {
        "replications": replications,
        "average_throughput_per_hour": round(
            average_throughput, 2
        ),
        "average_lead_time_minutes": round(
            average_lead_time, 2
        ),
        "average_picking_wait_minutes": round(
            average_picking_wait, 2
        ),
        "average_packing_wait_minutes": round(
            average_packing_wait, 2
        ),
        "throughput_std_dev": round(
            throughput_std_dev, 2
        ),
        "lead_time_std_dev_minutes": round(
            lead_time_std_dev, 2
        ),
    }

def compare_replications(
    baseline_config: SimulationConfig,
    candidate_config: SimulationConfig,
    replications: int,
    max_cost_per_additional_order: float,
):
    baseline_result = run_replications(
        baseline_config,
        replications,
    )

    candidate_result = run_replications(
        candidate_config,
        replications,
    )

    throughput_gain = (
    candidate_result["average_throughput_per_hour"]
    - baseline_result["average_throughput_per_hour"]
    )

    lead_time_reduction = (
        baseline_result["average_lead_time_minutes"]
        - candidate_result["average_lead_time_minutes"]
    )

    packing_wait_reduction = (
        baseline_result["average_packing_wait_minutes"]
        - candidate_result["average_packing_wait_minutes"]
    )

    

    baseline_operating_cost = (
    baseline_config.simulation_hours
    * (
        baseline_config.picking_stations
        * baseline_config.picking_station_cost_per_hour
        + baseline_config.packing_stations
        * baseline_config.packing_station_cost_per_hour
    )
)

    candidate_operating_cost = (
        candidate_config.simulation_hours
        * (
            candidate_config.picking_stations
            * candidate_config.picking_station_cost_per_hour
            + candidate_config.packing_stations
            * candidate_config.packing_station_cost_per_hour
        )
    )

    additional_cost = (
        candidate_operating_cost - baseline_operating_cost
    )

    additional_completed_orders = (
        candidate_result["average_throughput_per_hour"]
        - baseline_result["average_throughput_per_hour"]
    ) * baseline_config.simulation_hours

    if additional_completed_orders > 0:
        cost_per_additional_order = (
            additional_cost / additional_completed_orders
        )
    else:
        cost_per_additional_order = None

    if cost_per_additional_order is None:
        recommendation = "baseline"
    elif (
        throughput_gain > 0
        and lead_time_reduction > 0
        and cost_per_additional_order <= max_cost_per_additional_order
    ):
        recommendation = "candidate"
    elif (
        throughput_gain > 0
        or lead_time_reduction > 0
    ):
        recommendation = "tradeoff"
    else:
        recommendation = "baseline"

    return {
        "baseline": baseline_result,
        "candidate": candidate_result,
        "improvement": {
            "average_throughput_per_hour": round(
                candidate_result["average_throughput_per_hour"]
                - baseline_result["average_throughput_per_hour"],
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
        "recommendation": recommendation,
        "summary": {
            "throughput_gain_per_hour": round(throughput_gain, 2),
            "lead_time_reduction_minutes": round(lead_time_reduction, 2),
            "packing_wait_reduction_minutes": round(
                packing_wait_reduction,
                2,
            ),
            "baseline_operating_cost": round(
                baseline_operating_cost, 2
            ),
            "candidate_operating_cost": round(
                candidate_operating_cost, 2
            ),
            "additional_cost": round(additional_cost, 2),
            "cost_per_additional_order": (
                round(cost_per_additional_order, 2)
                if cost_per_additional_order is not None
                else None
            ),
            "max_cost_per_additional_order": round(
                max_cost_per_additional_order,
                2,
            ),
        },
    }

def optimize_packing_capacity(
    base_config: SimulationConfig,
    min_packing_stations: int,
    max_packing_stations: int,
    replications: int,
    max_cost_per_additional_order: float,
):
    scenarios = []

    baseline_config = base_config.model_copy(
        update={
            "packing_stations": min_packing_stations
        }
    )

    baseline_result = run_replications(
        baseline_config,
        replications,
    )

    baseline_cost = baseline_config.simulation_hours * (
        baseline_config.picking_stations
        * baseline_config.picking_station_cost_per_hour
        + baseline_config.packing_stations
        * baseline_config.packing_station_cost_per_hour
    )

    best_scenario = None

    for packing_stations in range(
        min_packing_stations,
        max_packing_stations + 1,
    ):
        scenario_config = base_config.model_copy(
            update={
                "packing_stations": packing_stations
            }
        )

        result = run_replications(
            scenario_config,
            replications,
        )

        operating_cost = scenario_config.simulation_hours * (
            scenario_config.picking_stations
            * scenario_config.picking_station_cost_per_hour
            + scenario_config.packing_stations
            * scenario_config.packing_station_cost_per_hour
        )

        throughput_gain = (
            result["average_throughput_per_hour"]
            - baseline_result["average_throughput_per_hour"]
        )

        additional_cost = operating_cost - baseline_cost

        additional_completed_orders = (
            throughput_gain
            * scenario_config.simulation_hours
        )

        if additional_completed_orders > 0:
            cost_per_additional_order = (
                additional_cost
                / additional_completed_orders
            )
        else:
            cost_per_additional_order = None

        scenario = {
            "packing_stations": packing_stations,
            "average_throughput_per_hour": result[
                "average_throughput_per_hour"
            ],
            "average_lead_time_minutes": result[
                "average_lead_time_minutes"
            ],
            "average_packing_wait_minutes": result[
                "average_packing_wait_minutes"
            ],
            "operating_cost": round(
                operating_cost,
                2,
            ),
            "cost_per_additional_order": (
                round(cost_per_additional_order, 2)
                if cost_per_additional_order is not None
                else None
            ),
        }

        scenarios.append(scenario)

    economically_acceptable_scenarios = [
    scenario
    for scenario in scenarios
    if (
        scenario["cost_per_additional_order"] is not None
        and scenario["cost_per_additional_order"]
        <= max_cost_per_additional_order
    )
    ]

    if economically_acceptable_scenarios:
        best_lead_time = min(
            scenario["average_lead_time_minutes"]
            for scenario in economically_acceptable_scenarios
        )

        performance_tolerance = 0.5

        near_optimal_scenarios = [
            scenario
            for scenario in economically_acceptable_scenarios
            if (
                scenario["average_lead_time_minutes"]
                <= best_lead_time + performance_tolerance
            )
        ]

        best_scenario = min(
            near_optimal_scenarios,
            key=lambda scenario: scenario["operating_cost"],
        )
    else:
        best_scenario = None

    return {
        "baseline_packing_stations": min_packing_stations,
        "recommended": best_scenario,
        "scenarios": scenarios,
    }