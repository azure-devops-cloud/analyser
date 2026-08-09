from services.telegram_service import send_message

def test_send_message_accepts_simple_success_response(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN","token"); monkeypatch.setenv("TELEGRAM_CHAT_ID","chat")
    class Response: status_code=200; text="ok"
    monkeypatch.setattr("services.telegram_service.requests.post",lambda *args,**kwargs: Response())
    assert send_message("hello",confidence_score=85,threshold=80) is True

def test_send_message_rejects_http_error_response(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN","token"); monkeypatch.setenv("TELEGRAM_CHAT_ID","chat")
    class Response: status_code=500; text="telegram unavailable"
    monkeypatch.setattr("services.telegram_service.requests.post",lambda *args,**kwargs: Response())
    assert send_message("hello",confidence_score=85,threshold=80) is False
