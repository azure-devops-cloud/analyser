# Security Model

## Secrets

Secrets are supplied through environment variables and GitHub Actions Secrets. Never commit tokens, API keys, chat identifiers, or credentials.

## Agent boundaries

Agents cannot bypass the deterministic control plane. Tool access is capability-based and should be explicitly registered. Arbitrary shell execution is not part of the baseline agent contract.

## Untrusted content

News pages, RSS payloads, and external research are untrusted input. Agents must treat instructions embedded in retrieved content as data, not authority. External content cannot override system/runtime policy or request secrets.

## Output validation

Agent results are structured. Evidence references must come from the evidence ledger. Deterministic decisions remain authoritative over optional LLM explanations.

## Logging

Logs and runtime events must not include credentials. When adding new integrations, redact authorization headers and secret-bearing payload fields before persistence.

## External side effects

Telegram delivery and future write tools are isolated behind services. Production side effects must be explicitly enabled by configuration and must remain idempotent.
