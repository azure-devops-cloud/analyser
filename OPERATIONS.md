# Operations Runbook

## Runtime lifecycle

A normal run is:

`Trigger -> plan -> execute -> recover -> validate -> summarize -> deliver -> persist`

Every run has a `run_id`. Every planned agent step has a `task_id`. Lifecycle events are retained in `AgentContext` and copied into the execution snapshot.

## Failure handling

The orchestrator retries only errors matching the configured transient-failure policy. Invalid input, schema errors, and other non-transient failures terminate that agent without consuming the full retry budget.

Critical-agent fail-fast behavior is configurable. The default is continuation so downstream monitoring and reporting can expose a degraded run instead of hiding the failure.

## Operator diagnosis

Inspect, in order:

1. GitHub Actions job result.
2. Agent execution graph.
3. Agent lifecycle events.
4. Failed agent errors and retry metadata.
5. Evidence verification status.
6. Telegram delivery status.
7. Database health.

## Recovery

Normal transient failures are autonomous. Human intervention is reserved for missing credentials, persistent external outages, destructive repository operations, security incidents, and business decisions that cannot be inferred safely.
