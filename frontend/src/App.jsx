import { useState } from "react"
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts"

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

function App() {
  const [activeView, setActiveView] = useState("dashboard")

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

  const [optimizationConfig, setOptimizationConfig] = useState({
    min_packing_stations: 1,
    max_packing_stations: 6,
    replications: 10,
    max_cost_per_additional_order: 100,
  })

  const [optimizationResult, setOptimizationResult] = useState(null)
  const [optimizationLoading, setOptimizationLoading] = useState(false)
  const [optimizationError, setOptimizationError] = useState("")

  const buildSimulationConfig = () => ({
    ...config,
    random_seed: 42,
    picking_station_cost_per_hour: 25,
    packing_station_cost_per_hour: 25,
  })

  const runSimulation = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_URL}/simulation/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(buildSimulationConfig()),
      })

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

  const runOptimization = async () => {
    setOptimizationLoading(true)
    setOptimizationError("")

    try {
      const response = await fetch(
        `${API_URL}/simulation/optimize-packing`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            base_config: buildSimulationConfig(),
            ...optimizationConfig,
          }),
        }
      )

      if (!response.ok) {
        throw new Error("Optimization failed")
      }

      const data = await response.json()
      setOptimizationResult(data)
    } catch (err) {
      setOptimizationError(err.message)
    } finally {
      setOptimizationLoading(false)
    }
  }

  const waitTimeData = result
    ? [
        {
          stage: "Picking",
          minutes: result.average_picking_wait_minutes,
        },
        {
          stage: "Packing",
          minutes: result.average_packing_wait_minutes,
        },
      ]
    : []

  const optimizationChartData = optimizationResult
    ? optimizationResult.scenarios.map((scenario) => ({
        stations: scenario.packing_stations,
        throughput: scenario.average_throughput_per_hour,
        leadTime: scenario.average_lead_time_minutes,
        cost: scenario.operating_cost,
      }))
    : []

  return (
    <div className="app">
      <aside className="sidebar">
        <div>
          <h2>FlowForge</h2>
          <p className="sidebar-subtitle">Operations Intelligence</p>
        </div>

        <nav>
          <button
            className={`nav-item ${
              activeView === "dashboard" ? "active" : ""
            }`}
            onClick={() => setActiveView("dashboard")}
          >
            Dashboard
          </button>

          <button
            className={`nav-item ${
              activeView === "simulation" ? "active" : ""
            }`}
            onClick={() => setActiveView("simulation")}
          >
            Simulation
          </button>

          <button
            className={`nav-item ${
              activeView === "optimization" ? "active" : ""
            }`}
            onClick={() => setActiveView("optimization")}
          >
            Optimization
          </button>
        </nav>
      </aside>

      <main className="dashboard">
        {activeView !== "optimization" ? (
          <>
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
                  {result
                    ? result.average_packing_wait_minutes
                    : "—"}
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
                          average_picking_time_minutes: Number(
                            e.target.value
                          ),
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
                          average_packing_time_minutes: Number(
                            e.target.value
                          ),
                        })
                      }
                    />
                  </label>
                </div>
              </div>

              <div className="panel">
                <h2>Performance overview</h2>

                {error && (
                  <p className="error-message">{error}</p>
                )}

                {!result && !error && (
                  <p>
                    Run a simulation to generate operational insights.
                  </p>
                )}

                {result && (
                  <>
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

                    <div className="chart-section">
                      <div className="chart-header">
                        <h3>Queue waiting time</h3>
                        <p>
                          Average waiting time by warehouse stage.
                        </p>
                      </div>

                      <div className="chart-container">
                        <ResponsiveContainer width="100%" height={240}>
                          <BarChart data={waitTimeData}>
                            <CartesianGrid
                              strokeDasharray="3 3"
                              vertical={false}
                            />
                            <XAxis dataKey="stage" />
                            <YAxis />
                            <Tooltip />
                            <Bar
                              dataKey="minutes"
                              fill="#111827"
                              radius={[6, 6, 0, 0]}
                            />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </section>
          </>
        ) : (
          <>
            <header className="dashboard-header">
              <div>
                <p className="eyebrow">CAPACITY PLANNING</p>
                <h1>Packing Optimization</h1>
                <p>
                  Explore packing capacity scenarios and identify
                  the best performance-cost tradeoff.
                </p>
              </div>

              <button
                className="run-button"
                onClick={runOptimization}
                disabled={optimizationLoading}
              >
                {optimizationLoading
                  ? "Optimizing..."
                  : "Run optimization"}
              </button>
            </header>

            <section className="optimization-layout">
              <div className="panel">
                <h2>Optimization parameters</h2>
                <p>
                  Define the capacity search range and economic
                  threshold.
                </p>

                <div className="config-grid">
                  <label>
                    Minimum packing stations
                    <input
                      type="number"
                      value={
                        optimizationConfig.min_packing_stations
                      }
                      onChange={(e) =>
                        setOptimizationConfig({
                          ...optimizationConfig,
                          min_packing_stations: Number(
                            e.target.value
                          ),
                        })
                      }
                    />
                  </label>

                  <label>
                    Maximum packing stations
                    <input
                      type="number"
                      value={
                        optimizationConfig.max_packing_stations
                      }
                      onChange={(e) =>
                        setOptimizationConfig({
                          ...optimizationConfig,
                          max_packing_stations: Number(
                            e.target.value
                          ),
                        })
                      }
                    />
                  </label>

                  <label>
                    Replications
                    <input
                      type="number"
                      value={optimizationConfig.replications}
                      onChange={(e) =>
                        setOptimizationConfig({
                          ...optimizationConfig,
                          replications: Number(e.target.value),
                        })
                      }
                    />
                  </label>

                  <label>
                    Max cost / additional order
                    <input
                      type="number"
                      value={
                        optimizationConfig.max_cost_per_additional_order
                      }
                      onChange={(e) =>
                        setOptimizationConfig({
                          ...optimizationConfig,
                          max_cost_per_additional_order: Number(
                            e.target.value
                          ),
                        })
                      }
                    />
                  </label>
                </div>
              </div>

              <div className="panel">
                <h2>Recommendation</h2>

                {optimizationError && (
                  <p className="error-message">
                    {optimizationError}
                  </p>
                )}

                {!optimizationResult &&
                  !optimizationError && (
                    <p>
                      Run the optimizer to generate a capacity
                      recommendation.
                    </p>
                  )}

                {optimizationResult?.recommended && (
                  <div className="recommendation-card">
                    <span>RECOMMENDED CAPACITY</span>

                    <strong>
                      {
                        optimizationResult.recommended
                          .packing_stations
                      }{" "}
                      packing stations
                    </strong>

                    <p>
                      Near-optimal operational performance while
                      controlling additional capacity cost.
                    </p>

                    <div className="recommendation-metrics">
                      <div>
                        <span>Throughput</span>
                        <strong>
                          {
                            optimizationResult.recommended
                              .average_throughput_per_hour
                          }
                          /h
                        </strong>
                      </div>

                      <div>
                        <span>Lead time</span>
                        <strong>
                          {
                            optimizationResult.recommended
                              .average_lead_time_minutes
                          }{" "}
                          min
                        </strong>
                      </div>

                      <div>
                        <span>Operating cost</span>
                        <strong>
                          €
                          {
                            optimizationResult.recommended
                              .operating_cost
                          }
                        </strong>
                      </div>

                      <div>
                        <span>Cost / extra order</span>
                        <strong>
                          €
                          {
                            optimizationResult.recommended
                              .cost_per_additional_order
                          }
                        </strong>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {optimizationResult && (
              <>
                <section className="panel optimization-chart-panel">
                  <h2>Cost vs performance</h2>
                  <p>
                    Compare capacity cost, throughput and lead time
                    across tested scenarios.
                  </p>

                  <div className="optimization-chart">
                    <ResponsiveContainer width="100%" height={320}>
                      <LineChart data={optimizationChartData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          vertical={false}
                        />

                        <XAxis
                          dataKey="stations"
                          label={{
                            value: "Packing stations",
                            position: "insideBottom",
                            offset: -4,
                          }}
                        />

                        <YAxis
                          yAxisId="left"
                          label={{
                            value: "Performance",
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />

                        <YAxis
                          yAxisId="right"
                          orientation="right"
                          label={{
                            value: "Cost (€)",
                            angle: 90,
                            position: "insideRight",
                          }}
                        />

                        <Tooltip />
                        <Legend />

                        <Line
                          yAxisId="left"
                          type="monotone"
                          dataKey="throughput"
                          name="Throughput"
                          stroke="#111827"
                          strokeWidth={3}
                          dot={{ r: 4 }}
                        />

                        <Line
                          yAxisId="left"
                          type="monotone"
                          dataKey="leadTime"
                          name="Lead time"
                          stroke="#6b7280"
                          strokeWidth={2}
                          dot={{ r: 4 }}
                        />

                        <Line
                          yAxisId="right"
                          type="monotone"
                          dataKey="cost"
                          name="Operating cost"
                          stroke="#9ca3af"
                          strokeWidth={2}
                          strokeDasharray="6 4"
                          dot={{ r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </section>

                <section className="panel scenarios-panel">
                  <h2>Capacity scenarios</h2>
                  <p>
                    Performance and cost across tested packing
                    capacities.
                  </p>

                  <div className="scenario-table-wrapper">
                    <table className="scenario-table">
                      <thead>
                        <tr>
                          <th>Stations</th>
                          <th>Throughput</th>
                          <th>Lead time</th>
                          <th>Packing wait</th>
                          <th>Operating cost</th>
                          <th>Cost / extra order</th>
                        </tr>
                      </thead>

                      <tbody>
                        {optimizationResult.scenarios.map(
                          (scenario) => (
                            <tr
                              key={scenario.packing_stations}
                              className={
                                optimizationResult.recommended
                                  ?.packing_stations ===
                                scenario.packing_stations
                                  ? "recommended-row"
                                  : ""
                              }
                            >
                              <td>{scenario.packing_stations}</td>

                              <td>
                                {
                                  scenario.average_throughput_per_hour
                                }
                                /h
                              </td>

                              <td>
                                {
                                  scenario.average_lead_time_minutes
                                }{" "}
                                min
                              </td>

                              <td>
                                {
                                  scenario.average_packing_wait_minutes
                                }{" "}
                                min
                              </td>

                              <td>
                                €{scenario.operating_cost}
                              </td>

                              <td>
                                {scenario.cost_per_additional_order ===
                                null
                                  ? "Baseline"
                                  : `€${scenario.cost_per_additional_order}`}
                              </td>
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                </section>
              </>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App