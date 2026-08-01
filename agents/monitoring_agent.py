from agents.base_agent import BaseAgent
from models.agent_result import AgentResult


class MonitoringAgent(BaseAgent):

    def run(self, context):
        try:
            return AgentResult(
                agent="monitoring_agent",
                status="success",
                data={
                    "news_count": len(context.news or []),
                    "market_count": len(context.market or []),
                    "decision_count": len(context.decisions or []),
                    "health": "healthy",
                    "sentiment": context.news_sentiment or {},
                },
                count=1
            )
        except Exception as ex:
            return AgentResult(
                agent="monitoring_agent",
                status="failed",
                errors=[str(ex)]
            )
