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

    return {
        "completed_orders": len(completed_orders),
        "throughput_per_hour": round(throughput_per_hour, 2),
        "average_lead_time_minutes": round(average_lead_time, 2),
        "average_picking_wait_minutes": round(average_picking_wait, 2),
        "average_packing_wait_minutes": round(average_packing_wait, 2),
        "bottleneck": bottleneck
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