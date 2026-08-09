# MarketMind Autonomous Agent Architecture

## Current production baseline

MarketMind uses a deterministic control plane around a fleet of specialized agents. The control plane owns safety, state, execution identity, retry policy, and observability; agents own market intelligence and reasoning.

```text
Trigger
  |
  v
ManagerAgent
  |
  +--> AgentRegistry ---- capabilities / phase / criticality
  |
  +--> RunPlanner ------- auditable plan + task IDs
  |
  +--> AgentOrchestrator
         |
         +--> Observe: news / market / calendar
         +--> Understand: intelligence / sentiment / technicals
         +--> Verify: facts / evidence / confidence
         +--> Decide: ranking / decisions / risk
         +--> Reason: evidence-grounded reasoning
         +--> Execute: alerts / summary
         +--> Learn: history
         +--> Observe: monitoring
         |
         +--> lifecycle events + bounded recovery
         |
         v
      AgentContext
         |
         +--> evidence ledger
         +--> decisions
         +--> reasoning
         +--> execution graph
         +--> lifecycle events
         +--> tool results
```

## Architectural rules

1. Agents are replaceable domain workers, not the safety boundary.
2. Deterministic infrastructure controls execution order, retries, state integrity, and critical-failure behavior.
3. Every run has a stable `run_id`; every planned step has a `task_id`.
4. Agent outcomes use a structured `AgentResult` contract.
5. Runtime events are retained in context so an operator can reconstruct what happened.
6. Evidence remains authoritative for market conclusions; optional LLM synthesis cannot change deterministic decisions.
7. External side effects must be isolated behind explicit services and configuration.

## Why we are not adding LangGraph or MCP yet

LangGraph is a mature open-source low-level orchestration framework for stateful agents, while MCP standardizes tool/resource context between AI applications and tools. Both are strong future integration points. At this stage the repository already has a small deterministic orchestration layer that directly matches its sequential market workflow. Adding either framework now would increase dependency and operational complexity without solving a current capability gap.

The runtime therefore exposes typed contracts and capability discovery first. A future migration to LangGraph or an MCP tool boundary can consume those contracts without rewriting agent business logic.

References: LangGraph and MCP are documented as open-source projects; MCP's official Python SDK is MIT licensed. See the project links in `TOOLS.md`.

## Planned evolution

- Durable checkpointed execution when runs become long-lived.
- MCP-backed external tools when multiple tool providers need interoperability.
- Optional LangGraph adapter if dynamic branching or human approval checkpoints become materially more complex.
- OpenTelemetry export when an external collector is configured.
- Persistent episodic/semantic memory after retention and privacy rules are defined.
