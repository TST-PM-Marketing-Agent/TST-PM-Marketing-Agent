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

## Expected Output Artifacts

- `data/messages.json` — full message history
- `data/backlog.json` — PM roadmap output
- `data/projects.json` — PM project and request records
- `data/campaigns.json` — saved campaign plans
- `logs/app.log` — runtime log

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

- Ollama is optional; fallback outputs are used if local LLM is unavailable.
- Current runtime implementation is PM + Marketing only (no CEO agent runtime module).
