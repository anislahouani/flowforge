import { useState } from "react"

function App() {
  const [config, setConfig] = useState({
    simulation_hours: 8,
    orders_per_hour: 20,
    picking_stations: 4,
    packing_stations: 2,
    average_picking_time_minutes: 4,
    average_packing_time_minutes: 5,
  })

  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const runSimulation = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/simulation/run",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...config,
            random_seed: 42,
            picking_station_cost_per_hour: 25,
            packing_station_cost_per_hour: 25,
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Simulation failed")
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div>
          <h2>FlowForge</h2>
          <p className="sidebar-subtitle">Operations Intelligence</p>
        </div>

        <nav>
          <button className="nav-item active">Dashboard</button>
          <button className="nav-item">Simulation</button>
          <button className="nav-item">Optimization</button>
        </nav>
      </aside>

      <main className="dashboard">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">WAREHOUSE OPERATIONS</p>
            <h1>Simulation Dashboard</h1>
            <p>
              Model warehouse capacity, identify bottlenecks,
              and optimize operational performance.
            </p>
          </div>

          <button
            className="run-button"
            onClick={runSimulation}
            disabled={loading}
          >
            {loading ? "Running..." : "Run simulation"}
          </button>
        </header>

        <section className="metrics">
          <div className="metric-card">
            <span>Throughput</span>
            <strong>
              {result ? result.throughput_per_hour : "—"}
            </strong>
            <small>orders / hour</small>
          </div>

          <div className="metric-card">
            <span>Lead time</span>
            <strong>
              {result ? result.average_lead_time_minutes : "—"}
            </strong>
            <small>minutes</small>
          </div>

          <div className="metric-card">
            <span>Packing wait</span>
            <strong>
              {result ? result.average_packing_wait_minutes : "—"}
            </strong>
            <small>minutes</small>
          </div>

          <div className="metric-card">
            <span>Operating cost</span>
            <strong>
              {result ? `€${result.operating_cost}` : "—"}
            </strong>
            <small>per simulation</small>
          </div>
        </section>

        <section className="workspace">
          <div className="panel">
            <h2>Simulation configuration</h2>
            <p>Configure warehouse demand and capacity.</p>

            <div className="config-grid">
              <label>
                Simulation hours
                <input
                  type="number"
                  value={config.simulation_hours}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      simulation_hours: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Orders per hour
                <input
                  type="number"
                  value={config.orders_per_hour}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      orders_per_hour: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Picking stations
                <input
                  type="number"
                  value={config.picking_stations}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      picking_stations: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Packing stations
                <input
                  type="number"
                  value={config.packing_stations}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      packing_stations: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Avg. picking time
                <input
                  type="number"
                  value={config.average_picking_time_minutes}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      average_picking_time_minutes: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Avg. packing time
                <input
                  type="number"
                  value={config.average_packing_time_minutes}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      average_packing_time_minutes: Number(e.target.value),
                    })
                  }
                />
              </label>
            </div>
          </div>

          <div className="panel">
            <h2>Performance overview</h2>

            {error && (
              <p className="error-message">
                {error}
              </p>
            )}

            {!result && !error && (
              <p>
                Run a simulation to generate operational insights.
              </p>
            )}

            {result && (
              <div className="result-summary">
                <div>
                  <span>Status</span>
                  <strong>
                    {result.bottleneck === "none"
                      ? "Balanced"
                      : `${result.bottleneck} bottleneck`}
                  </strong>
                </div>

                <div>
                  <span>Completed orders</span>
                  <strong>{result.completed_orders}</strong>
                </div>

                <div>
                  <span>Picking wait</span>
                  <strong>
                    {result.average_picking_wait_minutes} min
                  </strong>
                </div>

                <div>
                  <span>Packing wait</span>
                  <strong>
                    {result.average_packing_wait_minutes} min
                  </strong>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App