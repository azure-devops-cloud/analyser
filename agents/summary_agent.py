from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class SummaryAgent(BaseAgent):
    """Produce a human-oriented, evidence-backed executive intelligence brief."""

    @staticmethod
    def _news_brief(news_items, evidence):
        evidence_ids = {
            item.get("evidence_id")
            for item in evidence or []
            if isinstance(item, dict) and item.get("evidence_id")
        }
        brief = []
        for item in sorted(
            news_items or [],
            key=lambda value: (
                value.get("actionability", 0),
                value.get("importance", value.get("importance_score", 0)),
                value.get("freshness", 0),
            ),
            reverse=True,
        )[:5]:
            cited = []
            if item.get("evidence_id"):
                cited.append(item["evidence_id"])
            cited.extend(item.get("cited_evidence_ids", []) or [])
            cited = [value for value in dict.fromkeys(cited) if value in evidence_ids or value.startswith("news-")]
            actions = item.get("actions") or ["Monitor for confirmation"]
            brief.append({
                "what_happened": item.get("title", "Untitled"),
                "why_it_matters": item.get("why_it_matters", "Impact requires confirmation."),
                "affected_assets": item.get("affected_assets", []) or [],
                "impact": item.get("impact", "LOW"),
                "importance": item.get("importance", item.get("importance_score", 0)),
                "actionability": item.get("actionability", 0),
                "evidence": cited,
                "next_step": actions[0],
                "source": item.get("source", item.get("link", "")),
                "link": item.get("link", ""),
            })
        return brief

    def run(self, context):
        try:
            news_items = context.news_intelligence or context.news or []
            market_items = context.market or []
            decisions = context.decisions or []
            sentiment = context.news_sentiment or {}
            fact_validation = context.fact_validation or {}
            alerts = context.alerts or []
            confidence = context.confidence or {}
            risk = context.risk or {}
            evidence = context.evidence or []

            positive = sentiment.get("positive", 0)
            negative = sentiment.get("negative", 0)
            neutral = sentiment.get("neutral", 0)
            fact_confidence = float(fact_validation.get("confidence_score", 100))
            fact_status = fact_validation.get("verification_status", "validated")

            top_story = max(
                news_items,
                key=lambda item: item.get("actionability", item.get("importance_score", 0)),
                default=None,
            )
            market_signal = max(market_items, key=lambda item: abs(item.get("daily_change", 0)), default=None)
            top_decision = max(decisions, key=lambda item: item.get("score", 0), default=None)

            market_bias = "neutral"
            top_opportunity = "N/A"
            top_score = 0
            if top_decision:
                market_bias = top_decision.get("bias", "NEUTRAL").lower()
                top_opportunity = top_decision.get("name", "N/A")
                top_score = top_decision.get("score", 0)
            elif market_signal:
                market_bias = market_signal.get("trend", "NEUTRAL").lower()
                top_opportunity = market_signal.get("name", "N/A")

            market_posture = market_bias.capitalize()
            if negative >= positive:
                risk_caveat = "Risk remains elevated because the news flow is leaning negative."
            elif top_score < 70:
                risk_caveat = "Risk is moderate and confirmation is required before adding exposure."
            else:
                risk_caveat = "Risk remains contained, though momentum should still be monitored closely."

            if fact_status == "needs_more_sources" or fact_confidence < 50:
                action_recommendation = f"Hold on {top_opportunity} and wait for more evidence before acting."
            elif market_bias == "bullish":
                action_recommendation = f"Maintain selective exposure in {top_opportunity} and watch for follow-through."
            elif market_bias == "bearish":
                action_recommendation = f"Reduce risk in {top_opportunity} and wait for stronger confirmation."
            else:
                action_recommendation = f"Stay patient on {top_opportunity} and wait for the next catalyst."

            intelligence_brief = self._news_brief(news_items, evidence)
            headline = f"Executive view: {market_posture} posture | Lead: {top_opportunity} | Action: {action_recommendation}"
            summary = (
                f"{market_posture} posture is in focus, with {top_opportunity} as the leading opportunity. "
                f"News tone is {positive} positive, {negative} negative, and {neutral} neutral. "
                f"Risk watch: {risk_caveat}"
            )
            if top_story:
                summary += f" Lead intelligence: '{top_story.get('title', 'No headline available')}' ({top_story.get('impact', 'unknown')} impact)."
            if fact_status != "validated":
                summary += f" Verification is limited to {fact_validation.get('evidence_count', 0)} confirmed signals."
            if alerts:
                summary += f" Active alert: {alerts[0].get('message', 'Actionable alert available.')}"

            return AgentResult(
                agent="summary_agent",
                status="success",
                data={
                    "headline": headline,
                    "summary": summary,
                    "market_bias": market_bias,
                    "market_posture": market_posture,
                    "top_opportunity": top_opportunity,
                    "watchlist": top_opportunity if top_opportunity != "N/A" else "No clear lead",
                    "top_score": top_score,
                    "risk_caveat": risk_caveat,
                    "risk_watch": risk.get("level", "unknown").capitalize() + " risk: " + (risk.get("reasons", [risk_caveat])[0] if risk else risk_caveat),
                    "action_recommendation": action_recommendation,
                    "top_story": top_story,
                    "top_decision": top_decision,
                    "market_signal": market_signal,
                    "fact_validation": fact_validation,
                    "alerts": alerts,
                    "confidence": confidence,
                    "risk": risk,
                    "intelligence_brief": intelligence_brief,
                    "evidence_count": len(evidence),
                },
                count=1,
            )
        except Exception as ex:
            return AgentResult(agent="summary_agent", status="failed", errors=[str(ex)])
