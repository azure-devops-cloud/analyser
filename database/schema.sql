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

    sent INTEGER DEFAULT 0

);
