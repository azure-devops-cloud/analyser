# Agent Responsibilities

## Control-plane agents

### ManagerAgent
Owns the run lifecycle, registry, planning, orchestration, and final runtime snapshot. It does not perform market reasoning itself.

### MonitoringAgent
Observes pipeline health and records degraded execution signals.

## Intelligence agents

- `NewsCollectorAgent`: discover and ingest source material.
- `NewsIntelligenceAgent`: classify, rank relevance, extract market impact and affected assets.
- `NewsSentimentAgent`: derive directional news tone.
- `MarketAgent`: collect market observations.
- `CalendarAgent`: collect macro-event context.
- `TechnicalAnalysisAgent`: derive deterministic technical signals.
- `Research/verification agents`: validate facts, evidence quality, source trust, and corroboration.

## Decision agents

- `RankingAgent`: prioritize actionable intelligence.
- `DecisionAgent`: produce deterministic market bias, score, and decision fields.
- `RiskAgent`: assess risk posture.
- `ConfidenceAgent`: calculate structured confidence from validated signals.
- `ReasonerAgent`: explain decisions from the evidence ledger without changing authoritative decisions.

## Delivery agents

- `AlertAgent`: identify actionable alerts.
- `SummaryAgent`: produce a human-oriented evidence-backed brief.
- Telegram delivery remains an external side-effect service and is guarded by configuration and delivery status.

## Agent contract

Every agent must:

1. Accept `AgentContext`.
2. Return `AgentResult`.
3. Avoid hidden global state.
4. Use deterministic services for persistence, security, and side effects.
5. Fail with structured errors instead of raising across the orchestration boundary.
6. Declare capabilities when it owns a capability that the planner may discover.

## Autonomy boundary

Agents may observe, reason, plan, delegate, and adapt. They must not bypass deterministic safety controls, mutate database schemas at runtime, expose secrets, or execute arbitrary operating-system commands.
