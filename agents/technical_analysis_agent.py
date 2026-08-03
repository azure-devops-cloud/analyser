"""Convert raw technical indicators into explainable asset-level evidence."""

from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class TechnicalAnalysisAgent(BaseAgent):
    """Assess trend, momentum, and volatility for each market observation."""

    def run(self, context):
        try:
            analysis = []
            for market in context.market or []:
                rsi = float(market.get("rsi", 50))
                volatility = float(market.get("volatility", 0))
                trend = market.get("trend", "SIDEWAYS")
                reasons = [f"Trend is {trend.lower()}."]

                if rsi < 30:
                    momentum = "oversold"
                    reasons.append(f"RSI {rsi:.1f} indicates oversold momentum.")
                elif rsi > 70:
                    momentum = "overbought"
                    reasons.append(f"RSI {rsi:.1f} indicates overbought momentum.")
                else:
                    momentum = "neutral"
                    reasons.append(f"RSI {rsi:.1f} is neutral.")

                volatility_risk = "high" if volatility > 40 else "moderate" if volatility > 20 else "low"
                reasons.append(f"Annualized volatility risk is {volatility_risk}.")
                analysis.append(
                    {
                        "name": market["name"],
                        "symbol": market.get("symbol", market["name"]),
                        "trend": trend,
                        "signal": market.get("signal", "HOLD"),
                        "momentum": momentum,
                        "volatility_risk": volatility_risk,
                        "reasons": reasons,
                    }
                )

            context.add_technical_analysis(analysis)
            return AgentResult(
                agent="technical_analysis_agent",
                status="success",
                data={"assets": analysis},
                count=len(analysis),
            )
        except Exception as ex:
            return AgentResult(
                agent="technical_analysis_agent", status="failed", errors=[str(ex)]
            )
