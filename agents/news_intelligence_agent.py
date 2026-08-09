from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.news_intelligence_service import NewsIntelligenceService
from services.source_trust_service import SourceTrustService


class NewsIntelligenceAgent(BaseAgent):
    """Produce ranked, evidence-backed news intelligence for the shared context."""

    def __init__(self, fetcher=None, source_trust=None, llm_client=None):
        self.service = NewsIntelligenceService(fetcher=fetcher, llm_client=llm_client)
        self.source_trust = source_trust

    def run(self, context):
        try:
            if isinstance(context, dict):
                articles = context.get("news", [])
                trust_map = context.get("source_trust_map") or self.source_trust
            else:
                articles = context.news or []
                trust_map = context.source_trust_map or self.source_trust

            if not trust_map:
                trust_map = SourceTrustService().as_dict()

            intelligence = self.service.analyze(articles, source_trust=trust_map)
            if isinstance(context, dict):
                context["news_intelligence"] = intelligence
                context["source_trust_map"] = trust_map
            else:
                context.add_news_intelligence(intelligence)
                context.add_source_trust_map(trust_map)
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
