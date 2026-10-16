# MarketMind AI

MarketMind is a free-first, autonomous market-intelligence platform. It combines deterministic market/news infrastructure with specialized agents for discovery, interpretation, evidence validation, reasoning, decisioning, risk, reporting, and operational monitoring.

## Autonomous workflow

`Observe -> Understand -> Plan -> Delegate -> Execute -> Validate -> Recover -> Learn -> Report`

The deterministic control plane owns run identity, capability discovery, task planning, retries, safety boundaries, persistence, and lifecycle observability. Agents own intelligence and domain reasoning.

## Current capabilities

- RSS/news discovery, normalization, deduplication, relevance, impact, sentiment, and actionable ranking.
- Market and macro observations with deterministic technical analysis.
- Evidence ledger with source trust, verification, contradiction detection, and structured confidence.
- Evidence-grounded reasoning that cannot mutate the authoritative decision.
- Autonomous orchestration with bounded retry and failure classification.
- Capability-based agent registry and auditable run plans.
- Stable `run_id` and per-step `task_id` for traceability.
- Human-oriented executive and actionable-news reporting.
- Optional Telegram delivery through a guarded external service.
- Free-first model abstraction with local/open-weight defaults.

## Architecture and operations

- [ARCHITECTURE.md](ARCHITECTURE.md) — control-plane and agent architecture.
- [AGENTS.md](AGENTS.md) — agent responsibilities and autonomy boundaries.
- [TOOLS.md](TOOLS.md) — open-source framework and dependency decisions.
- [CONFIGURATION.md](CONFIGURATION.md) — runtime configuration.
- [OPERATIONS.md](OPERATIONS.md) — recovery and operational runbook.
- [SECURITY.md](SECURITY.md) — security model and tool boundaries.
- [TESTING.md](TESTING.md) — test and CI gate strategy.
- [EVALUATION.md](EVALUATION.md) — agent quality and model evaluation.

## Open-source-only setup

The baseline uses Python 3.12 and open-source/free components. No paid API is required for deterministic operation. Local/open-weight model execution is optional and configured independently from agent code.

## Quick start

1. Install Python 3.12.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt pytest
   ```

3. Copy the sample environment file:

   ```powershell
   copy .env.example .env
   ```

4. Fill in Telegram settings only if live delivery is required.
5. Run a dry test of the report generation path:

   ```powershell
   python -m main --dry-run
   ```

   For machine-readable output:

   ```powershell
   python -m main --dry-run --format json
   ```

6. Run the full pipeline:

   ```powershell
   python -m main
   ```

## CI gate

The full pytest suite is the milestone gate. A feature branch must be green before merge, and the merged `main` workflow must be green before the next milestone starts.

## Security notes

- Secrets come from environment variables/GitHub Actions Secrets.
- Retrieved web/news content is treated as untrusted data.
- Agents cannot bypass deterministic control-plane safety boundaries.
- External side effects are isolated behind explicit services.
