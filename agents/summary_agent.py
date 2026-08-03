from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class SummaryAgent(BaseAgent):

    def run(self, context):
        try:
            news_items = context.news or []
            market_items = context.market or []
            decisions = context.decisions or []
            sentiment = context.news_sentiment or {}
            fact_validation = context.fact_validation or {}
            alerts = context.alerts or []

            positive = sentiment.get("positive", 0)
            negative = sentiment.get("negative", 0)
            neutral = sentiment.get("neutral", 0)
            fact_confidence = int(fact_validation.get("confidence_score", 100))
            fact_status = fact_validation.get("verification_status", "validated")

            top_story = None
            if news_items:
                top_story = max(news_items, key=lambda item: item.get("importance_score", 0))

            market_signal = None
            if market_items:
                market_signal = max(market_items, key=lambda item: abs(item.get("daily_change", 0)))

            top_decision = None
            if decisions:
                top_decision = max(decisions, key=lambda item: item.get("score", 0))

            market_bias = "neutral"
            top_opportunity = "N/A"
            top_score = 0
            market_posture = "Neutral"

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
                risk_caveat = "Risk is moderate and should be managed through confirmation before adding exposure."
            else:
                risk_caveat = "Risk remains contained, though momentum should still be monitored closely."

            if fact_status == "needs_more_sources" or fact_confidence < 50:
                action_recommendation = (
                    f"Hold on {top_opportunity} and wait for more evidence before acting."
                )
            elif market_bias == "bullish":
                action_recommendation = (
                    f"Maintain selective exposure in {top_opportunity} and keep watching for follow-through confirmation."
                )
            elif market_bias == "bearish":
                action_recommendation = (
                    f"Reduce risk in {top_opportunity} and wait for stronger confirmation before increasing exposure."
                )
            else:
                action_recommendation = (
                    f"Stay patient on {top_opportunity} and wait for the next catalyst before acting."
                )

            watchlist = top_opportunity if top_opportunity != "N/A" else "No clear lead"
            risk_watch = risk_caveat

            headline = (
                f"Executive view: {market_posture} posture | Lead: {watchlist} | Action: {action_recommendation}"
            )

            summary = (
                f"{market_posture} posture is in focus, with {watchlist} as the leading opportunity. "
                f"News tone is {positive} positive, {negative} negative, and {neutral} neutral. "
                f"Risk watch: {risk_watch}"
            )

            if top_story:
                summary += (
                    f" Key headline: '{top_story.get('title', 'No headline available')}' with "
                    f"{top_story.get('impact', 'unknown')} impact and a {top_story.get('sentiment', 'neutral').lower()} bias."
                )

            if fact_status != "validated":
                summary += (
                    f" Confidence is limited because only {fact_validation.get('evidence_count', 0)} cross-source signals were confirmed."
                )

            if alerts:
                summary += f" Active alert: {alerts[0]['message']}"

            return AgentResult(
                agent="summary_agent",
                status="success",
                data={
                    "headline": headline,
                    "summary": summary,
                    "market_bias": market_bias,
                    "market_posture": market_posture,
                    "top_opportunity": top_opportunity,
                    "watchlist": watchlist,
                    "top_score": top_score,
                    "risk_caveat": risk_caveat,
                    "risk_watch": risk_watch,
                    "action_recommendation": action_recommendation,
                    "top_story": top_story,
                    "top_decision": top_decision,
                    "market_signal": market_signal,
                    "fact_validation": fact_validation,
                    "alerts": alerts,
                },
                count=1
            )
        except Exception as ex:
            return AgentResult(
                agent="summary_agent",
                status="failed",
                errors=[str(ex)]
            )
