# TST PM + Marketing Agent

PM + Marketing multi-agent simulation for the AI Enterprise project, now integrated with a CEO-driven Week 7 message-bus workflow.

## Team

- Contact: @Shivam Tyagi
- Contact: @subhas dey
- Contact: @Jay Mukherjee

## Overview

This repository implements a lightweight enterprise simulation with:

- **CEO Agent** (orchestrates, delegates, approves high-budget actions)
- **Product Manager Agent** (creates roadmap/backlog from business goals)
- **Marketing Agent** (plans and launches campaigns, escalates high budget)
- **Shared Message Bus** (asynchronous queue + persistent logs)
- **Mandatory JSON Message Schema** across all inter-agent communication

The system demonstrates a Week 7 deliverable:

- CEO delegates tasks to **at least two agents (PM + Marketing)**
- PM and Marketing execute role-specific work
- Agents send structured reports back to CEO
- Marketing escalates campaigns with budget `> $10,000` to CEO for approval

## Repository Structure

```text
.
├── README.md
└── src
    ├── ceo_agent.py
    ├── main.py
    ├── marketing_agent.py
    ├── marketing_tools.py
    ├── message_bus.py
    ├── message_schema.py
    ├── orchestrator.py
    ├── pm_agent.py
    └── pm_tools.py
```

## Core Architecture

### 1) Shared Message Envelope (Mandatory)

All agents send/receive this envelope:

```json
{
  "id": "<uuid>",
  "timestamp": "<iso8601>",
  "sender": "<agent_name>",
  "recipient": "<agent_name | broadcast>",
  "task_type": "<enum/string>",
  "context": {},
  "payload": {},
  "status": "<pending|in_progress|done|error>",
  "error": "<optional>"
}
```

- `payload` is role-specific
- envelope fields remain consistent across all agents

### 2) Message Bus

`src/message_bus.py` provides:

- `send_message(msg)` for queueing and persistence
- `get_messages_for(agent_name)` for agent-specific message retrieval
- persistent message log at `data/messages.json`

### 3) Supervisor Loop

`src/orchestrator.py` runs one cycle in this order:

1. CEO
2. PM
3. Marketing

Repeated cycles allow asynchronous handoffs and follow-up messages.

## Agent Responsibilities

### CEO Agent (`src/ceo_agent.py`)

- Handles `START_BUSINESS_CYCLE`
- Delegates:
  - `DEFINE_Q2_ROADMAP` → PM
  - `PREPARE_CAMPAIGN_STRATEGY` → Marketing
- Receives:
  - `PM_REPORT`
  - `MARKETING_REPORT`
- Handles `BUDGET_APPROVAL` and sends `BUDGET_APPROVED` to Marketing
- Persists reports to `data/ceo_reports.json`

### Product Manager Agent (`src/pm_agent.py`)

- Handles `DEFINE_Q2_ROADMAP`
- Uses tools to:
  - generate features (LLM with fallback)
  - prioritize with MoSCoW
  - save backlog and project/request artifacts
- Sends:
  - `LAUNCH_CAMPAIGN` → Marketing
  - `PM_REPORT` → CEO

### Marketing Agent (`src/marketing_agent.py`)

- Handles:
  - `PREPARE_CAMPAIGN_STRATEGY`
  - `LAUNCH_CAMPAIGN`
  - `BUDGET_APPROVED`
- Uses campaign planning tool (LLM with fallback)
- Budget policy:
  - if `budget > 10000`: send `BUDGET_APPROVAL` → CEO
  - else: persist campaign directly
- Sends `MARKETING_REPORT` updates to CEO

## Tools and Persistence

### PM Tools (`src/pm_tools.py`)

- Feature generation via Ollama (`mistral`) with deterministic fallback
- MoSCoW prioritization
- Project/request logging in `data/projects.json`
- Backlog output in `data/backlog.json`

### Marketing Tools (`src/marketing_tools.py`)

- Campaign plan generation via Ollama (`mistral`) with deterministic fallback
- Campaign persistence in `data/campaigns.json`

## Week 7 Deliverables Implemented

- ✅ Shared asynchronous message bus is active
- ✅ CEO-driven delegation to PM and Marketing
- ✅ Multi-agent scenario executed through supervisor cycles
- ✅ Structured inter-agent messaging using the mandatory envelope
- ✅ CEO response collection and reporting log
- ✅ High-budget campaign escalation and approval path

## How to Run

From repository root:

```bash
python3 src/main.py
```

## Expected Output Artifacts

After running:

- `data/messages.json` — full message history
- `data/backlog.json` — PM roadmap output
- `data/projects.json` — PM project and request records
- `data/campaigns.json` — saved campaign plans
- `data/ceo_reports.json` — reports received by CEO
- `logs/app.log` — runtime log

## Current Scenario Flow

1. User sends `START_BUSINESS_CYCLE` to CEO.
2. CEO delegates roadmap task to PM and strategy task to Marketing.
3. PM produces prioritized features and asks Marketing to launch campaign.
4. Marketing plans campaign and either:
   - launches directly (budget <= 10k), or
   - escalates for CEO approval (budget > 10k).
5. PM and Marketing send status reports to CEO.
6. CEO records outcomes.

## Alignment to Enterprise Requirements

- **Communication protocol**: asynchronous queue + JSON envelope
- **Decision hierarchy**: CEO delegates and approves risk/budget decisions
- **Orchestration**: cycle-based supervisor loop
- **Autonomy**: each agent executes role-specific logic with tools
- **Persistence**: files in `data/` keep state across runs

## Notes

- Ollama is optional; tool logic includes fallback outputs if local LLM is unavailable.
- This repo focuses on PM + Marketing scope with CEO integration for Week 7.
