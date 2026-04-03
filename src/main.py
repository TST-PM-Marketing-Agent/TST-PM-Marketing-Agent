from message_schema import Message
from message_bus import send_message
from orchestrator import run_cycle

msg = Message.create(
    sender="User",
    recipient="CEO",
    task_type="START_BUSINESS_CYCLE",
    context={"quarter": "Q2", "year": 2026},
    payload={
        "business_goal": "Increase SaaS revenue by 15%",
        "constraints": ["Focus on SMB customers", "3-engineer capacity"],
        "product_name": "AI-Enterprise-Suite"
    }
)
send_message(msg)

run_cycle()
run_cycle()
run_cycle()
run_cycle()

print("Simulation complete. Check data/backlog.json, data/campaigns.json, and data/ceo_reports.json.")
