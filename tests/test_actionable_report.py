from agents.summary_agent import SummaryAgent
from models.context import AgentContext
from models.agent_result import AgentResult
import main


def test_summary_builds_human_actionable_intelligence_brief():
    context = AgentContext()
    context.news_intelligence = [{
        "title": "Fed rate cut boosts growth outlook",
        "link": "https://example.com/fed",
        "impact": "HIGH",
        "importance": 0.9,
        "actionability": 0.95,
        "freshness": 0.9,
        "why_it_matters": "Changes rate expectations for risk assets.",
        "affected_assets": ["GOLD", "BITCOIN"],
        "evidence_id": "news-123",
        "actions": ["Verify the primary source"],
    }]
    context.evidence = [{"evidence_id": "ev-1"}]
    context.market = [{"name": "GOLD", "trend": "BULLISH", "signal": "BUY", "daily_change": 1.2}]
    context.decisions = [{"name": "GOLD", "bias": "BULLISH", "score": 85, "confidence": "HIGH"}]
    context.news_sentiment = {"positive": 3, "negative": 1, "neutral": 0}

    result = SummaryAgent().run(context)

    assert result.status == "success"
    brief = result.data["intelligence_brief"]
    assert brief[0]["what_happened"] == "Fed rate cut boosts growth outlook"
    assert brief[0]["why_it_matters"]
    assert brief[0]["affected_assets"] == ["GOLD", "BITCOIN"]
    assert brief[0]["evidence"] == ["news-123"]
    assert brief[0]["next_step"] == "Verify the primary source"


def test_text_report_prefers_structured_actionable_intelligence():
    results = [AgentResult(
        agent="summary_agent",
        status="success",
        data={
            "headline": "Bullish posture",
            "top_opportunity": "GOLD",
            "market_posture": "Bullish",
            "risk_watch": "Risk contained",
            "action_recommendation": "Verify before acting",
            "evidence_count": 4,
            "intelligence_brief": [{
                "impact": "HIGH",
                "what_happened": "CPI surprises lower",
                "why_it_matters": "Rate expectations may shift",
                "affected_assets": ["GOLD"],
                "evidence": ["ev-1"],
                "next_step": "Check the primary release",
            }],
            "alerts": [],
        },
    )]

    report = main.build_report(results, 3)

    assert "Actionable Intelligence" in report
    assert "What happened" not in report
    assert "CPI surprises lower" in report
    assert "Why: Rate expectations may shift" in report
    assert "Affected: GOLD" in report
    assert "Evidence: ev-1" in report
    assert "Next: Check the primary release" in report
