from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.decision_service import DecisionService


class DecisionAgent(BaseAgent):

    def run(self, context):

        try:

            market_data = context.market
            sentiment = context.news_sentiment
            calendar = context.calendar

            service = DecisionService()

            analysis = []

            bullish = 0
            bearish = 0

            for item in market_data:

                result = service.analyze(
                    item,
                    sentiment,
                    calendar
                )

                analysis.append(result)

                if result["bias"] == "BULLISH":
                    bullish += 1

                elif result["bias"] == "BEARISH":
                    bearish += 1

            context.add_decisions(analysis)

            if bullish > bearish:
                mood = "BULLISH"
            elif bearish > bullish:
                mood = "BEARISH"
            else:
                mood = "NEUTRAL"

            best = None

            if analysis:
                best = max(
                    analysis,
                    key=lambda x: x["score"]
                )

            summary = {

                "market_mood": mood,

                "bullish_assets": bullish,

                "bearish_assets": bearish,

                "top_opportunity": best["name"] if best else "N/A",

                "top_score": best["score"] if best else 0

            }

            return AgentResult(

                agent="decision_agent",

                status="success",

                data={

                    "analysis": analysis,

                    "summary": summary

                },

                count=len(analysis)

            )

        except Exception as ex:

            return AgentResult(

                agent="decision_agent",

                status="failed",

                errors=[str(ex)]

            )
