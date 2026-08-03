from agents.base_agent import BaseAgent
from models.agent_result import AgentResult
from services.alert_service import AlertService


class AlertAgent(BaseAgent):
    def run(self, context):
        service = AlertService()
        try:
            alerts = service.create_actionable_alerts(context.decisions or [])
            context.add_alerts(alerts)
            return AgentResult(
                agent="alert_agent",
                status="success",
                data={"alerts": alerts},
                count=len(alerts),
            )
        except Exception as ex:
            return AgentResult(agent="alert_agent", status="failed", errors=[str(ex)])
        finally:
            service.close()
