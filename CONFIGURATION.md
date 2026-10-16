# Configuration

Configuration is environment-driven and safe to use in GitHub Actions.

## Model

- `MODEL_PROVIDER`: provider selector; default `ollama`.
- `MODEL_NAME`: model identifier; default `qwen3:4b`.
- `MODEL_TEMPERATURE`: default `0.0` for deterministic reasoning.
- `MODEL_MAX_TOKENS`: default `2048`.
- `MODEL_TIMEOUT`: request timeout in seconds.

## Recovery

- `AGENT_MAX_RETRIES`: bounded retry budget.
- `AGENT_BACKOFF_SECONDS`: linear backoff between retry attempts.
- `AGENT_STOP_ON_CRITICAL_FAILURE`: fail-fast switch for critical agents; default is false so non-critical work can continue and the final report can expose degradation.

## Delivery

`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are required only for live Telegram delivery. Tests and dry runs must not require them.

## Telemetry

`TELEMETRY_ENABLED` is reserved for the OpenTelemetry exporter integration. The current runtime remains fully functional when it is false.
