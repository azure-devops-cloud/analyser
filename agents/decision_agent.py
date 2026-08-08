from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.decision_service import DecisionService
from services.evidence_service import EvidenceService


class DecisionAgent(BaseAgent):
    def run(self, context):
        try:
            market_data = context.market
            sentiment = context.news_sentiment
            calendar = context.calendar
            service = DecisionService()
            evidence_service = EvidenceService()
            analysis = []
            bullish = 0
            bearish = 0
            all_evidence = []

            for item in market_data:
                evidence = evidence_service.build(
                    item,
                    sentiment=sentiment,
                    calendar_events=calendar,
                    fact_validation=context.fact_validation,
                )
                all_evidence.extend(evidence)
                result = service.analyze(item, sentiment, calendar, evidence=evidence)
                analysis.append(result)

                if result["bias"] == "BULLISH":
                    bullish += 1
                elif result["bias"] == "BEARISH":
                    bearish += 1

            context.add_evidence(all_evidence)
            context.add_decisions(analysis)

            if bullish > bearish:
                mood = "BULLISH"
            elif bearish > bullish:
                mood = "BEARISH"
            else:
                mood = "NEUTRAL"

            best = max(analysis, key=lambda x: x["score"]) if analysis else None
            summary = {
                "market_mood": mood,
                "bullish_assets": bullish,
                "bearish_assets": bearish,
                "top_opportunity": best["name"] if best else "N/A",
                "top_score": best["score"] if best else 0,
                "evidence_count": len(all_evidence),
            }

            return AgentResult(
                agent="decision_agent",
                status="success",
                data={"analysis": analysis, "summary": summary},
                count=len(analysis),
            )
        except Exception as ex:
            return AgentResult(
                agent="decision_agent",
                status="failed",
                errors=[str(ex)],
            )
