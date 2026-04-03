from ceo_agent import CEOAgent
from pm_agent import PMAgent
from marketing_agent import MarketingAgent

_ceo = CEOAgent()
_pm = PMAgent()
_marketing = MarketingAgent()

def run_cycle():
    _ceo.run()
    _pm.run()
    _marketing.run()
