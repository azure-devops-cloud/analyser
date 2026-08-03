# MarketMind AI

A lightweight market intelligence pipeline that collects RSS news, market data, and economic calendar signals, then generates a consolidated report.

## Features

- Collects and ranks news from official regulators, economic institutions, and market sources.
- Persists all processed news plus each market observation in SQLite for historical analysis.
- Creates one daily actionable `BUY_WATCH` or `SELL_WATCH` alert per asset when decision thresholds are met.
- Emits either a readable brief or structured JSON for automation.

The curated no-key sources include Federal Reserve, IMF, ECB, RBI, BLS, SEC, CISA, and technology/security publishers. Sources are intentionally curated for relevance and reliability; this is not an unfiltered claim to ingest every public feed.

## Open-source-only setup

This project uses Python 3.12 and common open-source packages only.

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

4. Fill in your Telegram settings in `.env` if you want live delivery.
5. Run a dry test of the report generation path:

   ```powershell
   python -m main --dry-run
   ```

   For a machine-readable report containing alert, history, and agent-health data:

   ```powershell
   python -m main --dry-run --format json
   ```

6. Run the full report pipeline:

   ```powershell
   python -m main
   ```

## Notes

- The Telegram bot token and chat ID are optional for local dry-run validation.
- The project will skip Telegram delivery when credentials are missing.
- The repository uses SQLite storage in the `data/` directory.
