from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.market_history_service import MarketHistoryService
from services.news_history_service import NewsHistoryService


class HistoryAgent(BaseAgent):
    def run(self, context):
        service = MarketHistoryService()
        news_service = NewsHistoryService()
        try:
            recent_market = service.recent()
            data = {
                "live_news_count": len(context.news or []),
                "news_history": news_service.summary(),
                "recent_market_snapshots": recent_market,
            }
            context.add_history(data)
            return AgentResult(
                agent="history_agent",
                status="success",
                data=data,
                count=len(recent_market),
            )
        except Exception as ex:
            return AgentResult(agent="history_agent", status="failed", errors=[str(ex)])
        finally:
            service.close()
            news_service.close()
