# Testing Strategy

## Unit tests

Cover deterministic scoring, evidence, confidence, risk, formatting, configuration, and retry classification.

## Agent tests

Each agent should have tests for success, malformed input, dependency failure, and recovery behavior where applicable.

## Integration tests

Exercise the manager, planner, orchestrator, shared context, evidence ledger, persistence, and delivery boundaries together.

## Failure tests

Explicitly cover transient HTTP errors, rate limits, timeouts, invalid responses, low-quality evidence, contradictory evidence, missing credentials, and database failures.

## Regression gate

The complete pytest suite is the gate for every milestone. A feature branch is not ready to merge until the full CI workflow is green. After merge, the `main` workflow must also be green before the next milestone starts.

## Evaluation

Agent quality should be measured separately from deterministic correctness: evidence coverage, source corroboration, decision consistency, confidence calibration, and hallucination/unsupported-claim rate.
