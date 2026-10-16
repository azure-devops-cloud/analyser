# Tools and Framework Strategy

## Current stack

The current runtime intentionally uses small, standard Python components:

- `requests` for HTTP integrations.
- `feedparser` for RSS ingestion.
- `yfinance` for market observations.
- SQLite for the baseline local persistence model.
- Custom typed contracts for the agent control plane.

## Framework decisions

### LangGraph
LangGraph is a mature open-source framework for stateful agent orchestration. It is not a dependency yet because the current workflow is deterministic and sequential, and the repository's control plane already provides the required state, retry, and lifecycle semantics. Re-evaluate when dynamic branching, durable checkpoints, or approval checkpoints become materially more complex.

### MCP
The official Model Context Protocol Python SDK provides standardized tool/resource interfaces. It is not a dependency yet because MarketMind currently owns its deterministic tools locally. Add an MCP adapter when external tool interoperability is required; do not make MCP a prerequisite for the core workflow.

### OpenTelemetry
OpenTelemetry is the preferred future telemetry export layer. The current `MetricsService` and lifecycle event model remain provider-neutral so an OpenTelemetry exporter can be added without changing agents.

### Model runtime
The model layer is provider-neutral and free-first. Ollama/local open-weight inference is the default. Agents must not depend directly on one model SDK.

## Dependency policy

Before adding a dependency, verify:

1. open-source license;
2. active maintenance;
3. Python 3.12 compatibility;
4. GitHub Actions compatibility;
5. no mandatory paid service;
6. meaningful capability gain over the existing implementation.

Avoid installing multiple overlapping agent frameworks for the same responsibility.
