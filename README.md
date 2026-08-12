# FlowForge

FlowForge is a full-stack warehouse simulation and capacity optimization platform.

It models warehouse operations, identifies operational bottlenecks, measures queueing performance, and evaluates different packing capacities to find a cost-effective configuration.

## Live Demo

**Frontend:**  
https://flowforge-beta-umber.vercel.app

**Backend API:**  
https://flowforge-api-qe25.onrender.com

> The backend is hosted on Render's free infrastructure and may require a short warm-up after inactivity.

---

## Features

### Warehouse Simulation

Configure operational parameters such as:

- Simulation duration
- Orders per hour
- Number of picking stations
- Number of packing stations
- Average picking time
- Average packing time

FlowForge simulates the warehouse workflow and returns operational KPIs including:

- Throughput
- Lead time
- Picking queue waiting time
- Packing queue waiting time
- Completed orders
- Operating cost
- Bottleneck detection

### Capacity Optimization

FlowForge evaluates multiple packing-capacity scenarios and compares their operational and economic performance.

The optimization engine provides:

- Recommended packing capacity
- Throughput by scenario
- Lead time by scenario
- Packing waiting time
- Operating cost
- Cost per additional order
- Cost vs. performance visualization

This makes it possible to identify where additional capacity creates meaningful operational improvements and where diminishing returns begin.

---

## Architecture

```text
                        FlowForge
                           |
             +-------------+-------------+
             |                           |
        React / Vite                  FastAPI
         Frontend                    Backend
             |                           |
             |       REST API            |
             +-------------------------->+
                                         |
                                  Simulation Engine
                                         |
                                      SimPy
                                         |
                              Warehouse Processes
                               /              \
                          Picking           Packing
                                         |
                                  Optimization Engine
                                         |
                              Capacity Scenarios
```

### Production Architecture

```text
User
 |
 v
Vercel
React / Vite Frontend
 |
 | HTTPS API requests
 v
Render
FastAPI Backend
 |
 v
SimPy Simulation + Optimization Engine
```

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Recharts
- CSS

### Backend

- Python
- FastAPI
- SimPy
- Pydantic
- Uvicorn

### Engineering & Deployment

- Docker
- Docker Compose
- Pytest
- GitHub Actions
- Vercel
- Render
- Git / GitHub

---

## Project Structure

```text
FlowForge/
├── .github/
│   └── workflows/
│
├── backend/
│   ├── app/
│   │   ├── simulation/
│   │   └── ...
│   ├── tests/
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/anis-lahouani/flowforge.git
cd flowforge
```

### 2. Create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

Install the dependencies required by the backend.

```bash
pip install -r backend/requirements.txt
```

### 4. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

The API will be available locally on port `8000`.

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite will display the local frontend address in the terminal.

---

## Environment Variables

The frontend uses an environment variable to determine the backend API URL.

```env
VITE_API_URL=http://127.0.0.1:8000
```

In production, `VITE_API_URL` points to the deployed Render API.

---

## Docker

The full stack can also be started using Docker Compose.

```bash
docker compose up --build
```

To stop the containers:

```bash
docker compose down
```

---

## Tests

Backend simulation logic is tested with Pytest.

Run the test suite from the project root:

```bash
pytest -v
```

---

## Production Build

To verify the frontend production build:

```bash
cd frontend
npm run build
```

Vite generates the optimized production bundle in:

```text
frontend/dist/
```

---

## CI/CD

FlowForge includes a GitHub Actions CI pipeline.

The pipeline validates the application automatically when changes are pushed to the repository.

The deployment architecture is separated into two services:

- **Vercel** hosts the React frontend.
- **Render** hosts the FastAPI backend.

This keeps the frontend and simulation API independently deployable.

---

## API

The FastAPI service exposes endpoints used by the frontend for warehouse simulation and optimization.

Example simulation flow:

```text
React UI
   |
   | POST simulation parameters
   v
FastAPI
   |
   v
Simulation Engine
   |
   v
Operational Metrics
   |
   v
React Dashboard
```

A health endpoint is also available to verify that the production API is running.

Example response:

```json
{
  "status": "ok",
  "service": "flowforge-api"
}
```

---

## Engineering Goals

FlowForge was built to demonstrate the combination of:

- Discrete-event simulation
- Operations research concepts
- Capacity planning
- Backend API design
- Data visualization
- Automated testing
- Containerization
- CI/CD
- Cloud deployment

Rather than displaying static analytics, the dashboard is driven by simulation results generated from user-defined operational parameters.

---

## Future Improvements

Potential extensions include:

- Multiple warehouse process stages
- Worker scheduling
- Inventory constraints
- Order priority classes
- Monte Carlo analysis
- Historical simulation runs
- Database persistence
- Authentication
- Scenario export
- Additional optimization objectives

---

## Author

**Anis Lahouani**

FlowForge — Warehouse Operations Simulation & Optimization
