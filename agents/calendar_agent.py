from agents.base_agent import BaseAgent
from models.agent_result import AgentResult

from services.calendar_service import CalendarService


class CalendarAgent(BaseAgent):

    def run(self, context):

        try:

            service = CalendarService()

            events = service.get_events()

            context.add_calendar(events)

            return AgentResult(
                agent="calendar_agent",
                status="success",
                data=events,
                count=len(events)
            )

        except Exception as ex:

            return AgentResult(
                agent="calendar_agent",
                status="failed",
                errors=[str(ex)]
            )
