CREATE TABLE IF NOT EXISTS speed_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    adapter_name TEXT NOT NULL,
    download_mbps REAL,
    upload_mbps REAL,
    latency_ms REAL,
    is_physical INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_samples_ts ON speed_samples(ts);
