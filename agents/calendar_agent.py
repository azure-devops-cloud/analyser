from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.calendar_service import CalendarService


class CalendarAgent(BaseAgent):

    def run(self, context):
        try:
            service = CalendarService()
            result = service.get_result()
            events = result["events"]

            context.add_calendar(events)
            context.add_calendar_status({
                "status": result["status"],
                "providers": result["providers"],
                "errors": result["errors"],
            })

            status = "success" if result["status"] in {"available", "available_empty"} else "degraded"
            return AgentResult(
                agent="calendar_agent",
                status=status,
                data=events,
                count=len(events),
                errors=result["errors"],
            )

        except Exception as ex:
            context.add_calendar_status({
                "status": "degraded",
                "providers": {},
                "errors": [str(ex)],
            })
            return AgentResult(
                agent="calendar_agent",
                status="degraded",
                errors=[str(ex)]
            )
