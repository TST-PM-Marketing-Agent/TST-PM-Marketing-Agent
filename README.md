# 🚕 Tesla Robotaxi Ride-Sharing: Multi-Agent System Dashboard

Welcome to the **Tesla Robotaxi Ride-Sharing Multi-Agent System Demo**. This is a premium, hierarchy-aware multi-agent simulation that integrates strategic planning, product backlog management, advertising campaigns, and software synthesis under a single unified dashboard interface.

---

## 🐳 Quick Start: Running with Docker (Recommended)

Running inside a Docker container is the fastest and easiest way to experience the entire demo with **zero local configuration**. No python setup, pip package installations, or local MongoDB instances are required!

### Prerequisites
* Ensure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed and running on your laptop.

### 1. Build and Start the Container
From the root of the workspace directory, run:
```bash
docker compose up --build
```

### 2. Access the Dashboard
Once the container starts, open your web browser and navigate to:
👉 **[http://localhost:8765/](http://localhost:8765/)**

### 3. Stop the Container
To stop and clean up the container, simply press `Ctrl+C` in your terminal or run:
```bash
docker compose down
```

---

## 💻 Manual Running (Local Python)

If you prefer to run the system directly on your local Python environment:

### Prerequisites
* Python 3.9+ installed.

### 1. Install Dependencies
```bash
pip3 install fastapi uvicorn pymongo requests eval_type_backport pydantic
```

### 2. Launch the Router Server
```bash
PYTHONPATH=ui-team ROUTER_API_PORT=8765 ROUTER_API_HOST=127.0.0.1 python3 -m enterprise_router.api
```

### 3. Access Dashboard
👉 **[http://127.0.0.1:8765/](http://127.0.0.1:8765/)**

---

## 🏗️ Multi-Agent Interaction Flow
When you click **"Start Multi-Agent Simulation"** on the dashboard, the following thread-based lifecycle executes:
1. **Central Bank Initialization**: The CEO Agent mints standard/broadcast tokens and transfers operational budgets to standard agents.
2. **Strategic Directives**: CEO submits `DRAFT_SPECS` to the PM Agent.
3. **MoSCoW Prioritization**: PM Agent fetches the spec and creates a structured development backlog (Must Have, Should Have, Could Have).
4. **Campaign Designing**: Marketing Agent designs the advertising copy and requests a `$15,000` budget.
5. **Executive Governance Gate**: Since the budget exceeds `$10,000`, the request goes to the CEO for a strategic ROI check (>20% required).
6. **Executive Decision (GO)**: The CEO broadcasts a project approval (`GO`) decision to all departments.
7. **Code & Test Synthesis**: The Engineering Agent fetches the PM features, synthesizes premium Streamlit dashboard code, runs test validations, and reports completion back to the CEO.

---

## 🛠️ Troubleshooting
* **Port Conflict:** If port `8765` is already in use, you can map the host port to another port in `docker-compose.yml` (e.g. `"8080:8765"`).
* **Reset Database:** You can wipe all state, logs, and token ledger values by clicking the **Reset DB** button on the UI dashboard or hitting `http://localhost:8765/demo/reset`.
