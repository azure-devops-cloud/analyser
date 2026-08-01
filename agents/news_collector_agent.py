from agents.base_agent import BaseAgent
from agents.news_agent import NewsAgent
from models.agent_result import AgentResult


class NewsCollectorAgent(BaseAgent):

    def run(self, context):
        try:
            result = NewsAgent().run(context)

            if result.status != "success":
                return AgentResult(
                    agent="news_collector_agent",
                    status="failed",
                    errors=result.errors
                )

            return AgentResult(
                agent="news_collector_agent",
                status="success",
                data=result.data,
                count=result.count,
                errors=result.errors,
            )
        except Exception as ex:
            return AgentResult(
                agent="news_collector_agent",
                status="failed",
                errors=[str(ex)]
            )
