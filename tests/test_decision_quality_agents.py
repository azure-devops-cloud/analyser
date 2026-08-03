from agents.confidence_agent import ConfidenceAgent
from agents.risk_agent import RiskAgent
from agents.technical_analysis_agent import TechnicalAnalysisAgent
from models.context import AgentContext


def test_decision_quality_agents_produce_explainable_outputs():
    context = AgentContext()
    context.market = [
        {
            "name": "BITCOIN",
            "symbol": "BTC-USD",
            "trend": "BULLISH",
            "signal": "BUY WATCH",
            "rsi": 28,
            "volatility": 45,
        }
    ]
    context.news = [{"title": "Market update"}]
    context.calendar = [{"title": "Fed meeting"}]
    context.fact_validation = {"verification_status": "validated"}

    assert TechnicalAnalysisAgent().run(context).status == "success"
    confidence = ConfidenceAgent().run(context)
    risk = RiskAgent().run(context)

    assert confidence.data["score"] == 95
    assert risk.data["level"] == "high"
    assert context.technical_analysis[0]["momentum"] == "oversold"
