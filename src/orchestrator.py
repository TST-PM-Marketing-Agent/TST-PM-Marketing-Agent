from pm_agent import PMAgent
from marketing_agent import MarketingAgent

_pm = PMAgent()
_marketing = MarketingAgent()

def run_cycle():
    _pm.run()
    _marketing.run()
