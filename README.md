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

## 🤖 Running with Production Ollama & Mistral (Model Calls)

If you want to experience the system using the actual agent brains via local LLMs rather than hardcoded mock simulations, follow these steps to set up Ollama and the Mistral/Llama models.

> [!IMPORTANT]
> Running **Live Production Agents** requires Ollama running on your host machine with the appropriate models pulled. Without this, the live agents will not be able to process strategic decisions, priorities, or code generation.

### 1. Install & Start Ollama
* Download and install [Ollama](https://ollama.com/) for your operating system.
* Launch the Ollama application or start the server (typically runs on `http://localhost:11434`).

### 2. Pull the Required Models
Open your terminal and pull the models used by the agents:
```bash
# Pull Mistral (used by CEO, PM, Marketing, and HR agents)
ollama pull mistral

# Pull Llama 3.1 (used by default for the Engineering agent's code generation)
ollama pull llama3.1
```

> [!TIP]
> If you want to use **Mistral** for the Engineering agent as well (to keep memory/resource usage lower), you can override the engineering model using an environment variable before launching:
> ```bash
> export OLLAMA_MODEL="mistral"
> ```

### 3. Connection Configuration
* **Docker Mode:** The docker container is configured to automatically communicate with Ollama on your host machine via the URL `http://host.docker.internal:11434` (pre-configured in `docker-compose.yml`). No extra setup is required!
* **Local Python Mode:** By default, the agents will search for Ollama at `http://localhost:11434`. Make sure you have installed the python package with `pip3 install ollama`.

### 4. Triggering Live Agents in the UI
Once your models are pulled and Ollama is running:
1. Open the dashboard at **[http://localhost:8765/](http://localhost:8765/)**.
2. Click the shiny **"Run Live Production Agents"** button in the header.
3. Watch the logs stream in as real agents execute the reasoning loops, prioritize backlog features, plan campaigns, and synthesize code using your local Ollama models!

---

## 💻 Manual Running (Local Python)

If you prefer to run the system directly on your local Python environment:

### Prerequisites
* Python 3.9+ installed.

### 1. Install Dependencies
```bash
pip3 install fastapi uvicorn pymongo requests eval_type_backport pydantic ollama
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
