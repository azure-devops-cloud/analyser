from config.settings import Settings


def test_settings_reports_missing_telegram_credentials(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    settings = Settings.from_environment(tmp_path)

    assert settings.missing_telegram_credentials() == [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]
    assert settings.debug is False
