CREATE TABLE IF NOT EXISTS news (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    url TEXT UNIQUE,

    source TEXT,

    category TEXT,

    summary TEXT,

    published_at TEXT,

    hash TEXT UNIQUE,

    impact_score INTEGER,

    impact TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS market_snapshot (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    gold REAL,

    silver REAL,

    bitcoin REAL,

    ethereum REAL,

    nifty REAL,

    sensex REAL,

    sp500 REAL,

    nasdaq REAL,

    dxy REAL,

    oil REAL

);

CREATE TABLE IF NOT EXISTS alerts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    category TEXT,

    message TEXT,

    fingerprint TEXT UNIQUE,

    sent INTEGER DEFAULT 0

);

CREATE TABLE IF NOT EXISTS market_history (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    captured_at TEXT NOT NULL,

    name TEXT NOT NULL,

    symbol TEXT NOT NULL,

    price REAL NOT NULL,

    daily_change REAL,

    trend TEXT,

    signal TEXT,

    rsi REAL,

    volatility REAL

);

CREATE INDEX IF NOT EXISTS idx_market_history_symbol_captured_at
ON market_history (symbol, captured_at DESC);

CREATE TABLE IF NOT EXISTS schema_migrations (

    version TEXT PRIMARY KEY,

    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE IF NOT EXISTS execution_metrics (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT NOT NULL,

    agent TEXT NOT NULL,

    status TEXT NOT NULL,

    started_at TEXT NOT NULL,

    duration_ms REAL NOT NULL,

    item_count INTEGER NOT NULL DEFAULT 0,

    error_count INTEGER NOT NULL DEFAULT 0,

    metadata TEXT NOT NULL DEFAULT '{}'

);

CREATE INDEX IF NOT EXISTS idx_execution_metrics_run_id
ON execution_metrics (run_id);
