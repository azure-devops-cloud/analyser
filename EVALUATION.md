# Agent Evaluation

Evaluation is separated from deterministic unit tests.

## Core dimensions

- **Evidence coverage:** percentage of conclusions linked to valid evidence IDs.
- **Source diversity:** number of independent sources supporting important claims.
- **Freshness:** age of evidence at decision time.
- **Conflict handling:** contradictory evidence is surfaced instead of silently averaged away.
- **Decision consistency:** deterministic inputs produce stable decisions.
- **Confidence calibration:** high confidence requires stronger evidence and successful verification.
- **Unsupported claims:** LLM explanations must not introduce facts or evidence IDs absent from the packet.
- **Operational reliability:** retry success rate, terminal failure rate, and delivery success rate.

## Evaluation data

Use historical, anonymized market/news cases and deterministic fixtures. Store evaluation outcomes separately from production decisions so evaluation cannot mutate live state.

## Promotion gate

A new model, prompt, tool, or routing strategy should pass regression and evaluation checks before becoming the default runtime configuration.
