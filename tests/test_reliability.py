from services.calendar_service import CalendarService
from services.telegram_service import (
    TELEGRAM_FAILED,
    TELEGRAM_SENT,
    TELEGRAM_SKIPPED,
    send_message_status,
)


def test_telegram_status_is_skipped_below_confidence(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Telegram API must not be called when confidence is below threshold")

    monkeypatch.setattr("services.telegram_service.requests.post", fail_if_called)

    assert send_message_status("low-confidence", confidence_score=40, threshold=80) == TELEGRAM_SKIPPED


def test_telegram_status_is_sent_for_successful_response(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    class Response:
        status_code = 200
        text = "ok"

    monkeypatch.setattr("services.telegram_service.requests.post", lambda *args, **kwargs: Response())

    assert send_message_status("high-confidence", confidence_score=85, threshold=80) == TELEGRAM_SENT


def test_telegram_status_is_failed_for_http_error(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "chat")

    class Response:
        status_code = 500
        text = "server error"

    monkeypatch.setattr("services.telegram_service.requests.post", lambda *args, **kwargs: Response())

    assert send_message_status("message", confidence_score=85, threshold=80) == TELEGRAM_FAILED


def test_calendar_falls_back_when_primary_feed_is_forbidden(monkeypatch):
    service = CalendarService()

    class ForbiddenResponse:
        content = b""
        text = "forbidden"

        def raise_for_status(self):
            raise RuntimeError("403 Client Error: Forbidden")

    class OfficialResponse:
        text = """
        <html><body><table><tr><th>August 12</th><td>Consumer Price Index</td></tr></table></body></html>
        """

        def raise_for_status(self):
            return None

    responses = iter([ForbiddenResponse(), OfficialResponse()])
    monkeypatch.setattr("services.calendar_service.requests.get", lambda *args, **kwargs: next(responses))

    result = service.get_result()

    assert result["status"] == "available"
    assert result["events"]
    assert result["events"][0]["source"] == "bls"
    assert result["providers"]["forexfactory"] == "failed"
    assert result["providers"]["bls"] == "available"
    assert result["errors"]


def test_calendar_reports_degraded_when_all_providers_fail(monkeypatch):
    service = CalendarService()

    class FailedResponse:
        content = b""
        text = "failure"

        def raise_for_status(self):
            raise RuntimeError("provider unavailable")

    monkeypatch.setattr("services.calendar_service.requests.get", lambda *args, **kwargs: FailedResponse())

    result = service.get_result()

    assert result["status"] == "degraded"
    assert result["events"] == []
    assert len(result["errors"]) == 4
