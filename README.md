# TST PM + Marketing Agent

PM + Marketing multi-agent simulation for the AI Enterprise project using a shared JSON message bus.

## Team

- Contact: @Shivam Tyagi
- Contact: @subhas dey
- Contact: @Jay Mukherjee

## Overview

This repository implements:

- **Product Manager Agent** (owns product roadmap and feature prioritization)
- **Marketing Agent** (builds campaigns, content, and metrics tracking)
- **Shared Message Bus** (asynchronous queue + persistent logs)
- **SQLite Storage Layer** for multi-project persistence and project event history
- **JSON Message Schema** for inter-agent communication

## Repository Structure

```text
.
├── README.md
└── src
    ├── main.py
    ├── marketing_agent.py
    ├── marketing_tools.py
    ├── message_bus.py
    ├── message_schema.py
    ├── orchestrator.py
    ├── pm_agent.py
    ├── pm_tools.py
    └── sample_messages.json
```

## Shared Message Envelope

All messages use:

```json
{
  "id": "<uuid>",
  "timestamp": "<iso8601>",
  "sender": "<agent_name>",
  "recipient": "<agent_name | external_team>",
  "task_type": "<string>",
  "context": {},
  "payload": {},
  "status": "<pending|in_progress|done|error>",
  "error": "<optional>"
}
```

## Agent Responsibilities

### Product Manager Agent (`src/pm_agent.py`)

- Gather/analyze customer and sales feedback from incoming payloads
- Prioritize features using MoSCoW
- Build roadmap/backlog outputs
- Prepare product specs for engineering/marketing handoff
- Respond to feature requests from other teams
- Persist outputs (`data/backlog.json`, `data/projects.json`)

### Marketing Agent (`src/marketing_agent.py`)

- Launch campaigns from PM handoff (`LAUNCH_CAMPAIGN`)
- Create channel plan and campaign assets
- Save campaign plans (`data/campaigns.json`)
- Consume PM status updates (`PM_REPORT`)
- Support budget escalation path via JSON scenarios (recipient `CEO`) when budget exceeds 10k

## Supervisor Loop

`src/orchestrator.py` runs one cycle:

1. PM
2. Marketing

`src/main.py` seeds a `DEFINE_Q2_ROADMAP` message to PM, then runs multiple cycles to complete PM→Marketing handoff.

## How to Run

From repository root:

```bash
python3 src/main.py
```

### Optional runtime configuration

The app runs with no extra setup using built-in fallbacks.

Environment variables:

- `APP_DB_PATH` (default: `data/agent_store.db`) — database file path
- `BACKLOG_PATH` (default: `data/backlog.json`) — backlog JSON artifact path
- `OPENAI_BASE_URL` + `OPENAI_API_KEY` (+ optional `OPENAI_MODEL`) — cloud LLM endpoint (OpenAI-compatible)

LLM provider fallback order:
1. Local Ollama (`ollama` Python package + local model)
2. Cloud endpoint using `OPENAI_BASE_URL`/`OPENAI_API_KEY`
3. Deterministic local fallback JSON

This lets the same code run on machines with local models, cloud-only setups, or no model access.

## Expected Output Artifacts

- `data/messages.json` — full message history
- `data/backlog.json` — PM roadmap output
- `data/projects.json` — PM project and request records
- `data/campaigns.json` — saved campaign plans
- `data/agent_store.db` — normalized database for projects, project events, messages, backlog, campaigns
- `logs/app.log` — runtime log

## Database model (multi-project storage)

The SQLite storage captures:

- `projects` — project id, name, goal, description, status, metadata, timestamps
- `project_events` — append-only updates whenever PM/Marketing process project-relevant inputs/outputs
- `messages` — persisted envelope records with project linkage
- `backlog_entries` — normalized PM prioritized feature sets per project
- `campaigns` — marketing campaign records tied to projects

Project matching uses:
- explicit `project_id` in incoming context when present
- otherwise active project by product name

## Sample JSON Scenarios (All PM + Marketing Cases)

See: `src/sample_messages.json`

Included scenarios:

- PM roadmap intake (`DEFINE_Q2_ROADMAP`)
- PM→Marketing campaign handoff (`LAUNCH_CAMPAIGN`)
- PM feature request intake (`REQUEST_FEATURES`)
- PM feature response (`FEATURE_RESPONSE`)
- Marketing direct launch when budget <= 10000
- Marketing budget approval request when budget > 10000
- Marketing qualified leads handoff to Sales
- Marketing campaign metrics report (CAC/LTV/ROI)
- Error envelope example (`status: error`)

## Notes

- Ollama is optional; cloud OpenAI-compatible endpoints are also supported via env vars.
- Current runtime implementation is PM + Marketing only (no CEO agent runtime module).
