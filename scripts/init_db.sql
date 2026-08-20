-- SupplyChainAI — PostgreSQL Schema Initialization
-- Run via: psql -U supplychainai -d supplychainai -f init_db.sql

CREATE TABLE IF NOT EXISTS scenarios (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    node_count INTEGER DEFAULT 120,
    graph_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id SERIAL PRIMARY KEY,
    scenario_id VARCHAR(100) NOT NULL REFERENCES scenarios(id),
    beta FLOAT DEFAULT 0.6,
    adoption_pct FLOAT DEFAULT 0.0,
    shock_intensity FLOAT DEFAULT 0.85,
    naive_index_peak FLOAT,
    ai_index_peak FLOAT,
    cost_naive FLOAT,
    cost_ai FLOAT,
    result_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS manifold_frames (
    id SERIAL PRIMARY KEY,
    frame_id INTEGER UNIQUE,
    beta FLOAT NOT NULL,
    adoption_pct FLOAT NOT NULL,
    shock_intensity FLOAT NOT NULL,
    frame_data JSONB NOT NULL
);

-- Index for fast manifold lookups
CREATE INDEX IF NOT EXISTS idx_manifold_params ON manifold_frames (beta, adoption_pct, shock_intensity);

-- Seed the default scenario
INSERT INTO scenarios (id, name, node_count) VALUES
    ('kaohsiung_typhoon', 'Typhoon Hits Port Kaohsiung', 120)
ON CONFLICT (id) DO NOTHING;
