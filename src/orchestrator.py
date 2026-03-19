from pm_agent import PMAgent
from marketing_agent import MarketingAgent

pm = PMAgent()
marketing = MarketingAgent()

def run_cycle():
    pm.run()
    marketing.run()
    # add other agents later
