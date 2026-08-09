from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.news_intelligence_service import NewsIntelligenceService


class NewsIntelligenceAgent(BaseAgent):
    """Produce ranked, evidence-backed news intelligence for the shared context."""

    def __init__(self, fetcher=None, source_trust=None, llm_client=None):
        self.service = NewsIntelligenceService(fetcher=fetcher, llm_client=llm_client)
        self.source_trust = source_trust or {}

    def run(self, context):
        try:
            if isinstance(context, dict):
                articles = context.get("news", [])
            else:
                articles = context.news or []
            intelligence = self.service.analyze(articles, source_trust=self.source_trust)
            if isinstance(context, dict):
                context["news_intelligence"] = intelligence
            else:
                context.news_intelligence = intelligence
            return AgentResult(
                agent="news_intelligence_agent",
                status="success",
                data=intelligence,
                count=len(intelligence),
            )
        except Exception as ex:
            return AgentResult(
                agent="news_intelligence_agent",
                status="failed",
                errors=[str(ex)],
            )
