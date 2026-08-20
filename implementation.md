# SupplyChainAI — Master Implementation Plan (V3)

> Based on the finalized STAMPEDE V3 Technical Blueprint. This plan defines the **project structure**, **shared API contracts**, and **hour-by-hour step-by-step instructions** for all 3 team members to work simultaneously without merge conflicts.

---

## User Review Required

> [!IMPORTANT]
> **Naming:** The V3 blueprint still uses "STAMPEDE" internally in the demo script taglines (e.g., "RUN STAMPEDE"). Should all in-product references use "SupplyChainAI" or keep "STAMPEDE" as the product brand name within the UI?

> [!IMPORTANT]
> **Cloud Provider:** The plan assumes **Render** for deployment (free tier, Docker support, public URL). Confirm if the team prefers Railway, Fly.io, or AWS EC2 instead.

> [!IMPORTANT]
> **Python Version:** Standardized on **Python 3.11**. Confirm this works for all team members' local environments.

> [!WARNING]
> **Hackathon Clock:** Based on the V3 timeline (48 hours, Phases 0–4), the current local time is August 20, 15:22 IST. If the hackathon window is Aug 20–25, there is adequate time, but Phase 1 cloud deployment should happen within the first 4 hours.

---

## Open Questions

1. **Data Source for Sentinel NLP:** Will Person 1 use a local mock GDELT JSON fixture, or integrate the live GDELT API? Mock is recommended for demo reliability.
2. **Graph Size:** The blueprint specifies 120 nodes. Is this locked, or should the schema support variable node counts for stress testing?
3. **Authentication:** Is there any auth requirement for the live demo URL, or is it fully public/open?

---

## 1. Project Structure (Conflict-Free Directory Layout)

Each person works exclusively within their own root directory. Shared contracts live in `/shared/`.

```
SupplyChainAI/
├── README.md                          # Project overview (already exists)
├── docker-compose.yml                 # [Person 2] Multi-service orchestration
├── .gitignore                         # Shared gitignore
├── .env.example                       # Environment variable template
│
├── shared/                            # ★ SHARED CONTRACT ZONE (all 3 edit, but only schemas)
│   ├── api_schemas/
│   │   ├── disruption_event.json      # Sentinel trigger payload
│   │   ├── triage_report.json         # Triage blast radius response
│   │   ├── reflex_decision.json       # Reflex agent action plan
│   │   ├── stampede_index.json        # Live Stampede Index WebSocket frame
│   │   ├── manifold_frame.json        # Precomputed manifold state frame
│   │   ├── market_impact.json         # Kyle price impact response
│   │   ├── perishable_routing.json    # Rot-aware routing response
│   │   └── simulation_config.json     # Scenario configuration (β, adoption, shock)
│   ├── graph_schema/
│   │   └── supply_network.json        # 120-node graph topology schema
│   └── constants.py                   # Shared constants (weights, thresholds, enums)
│
├── ai_engine/                         # ★ PERSON 1 TERRITORY
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── sentinel.py                # NLP event extraction + decorrelation
│   │   ├── triage.py                  # Buffer-diversity + blast radius
│   │   └── reflex.py                  # Fokker-Planck PDE + de-phasing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── fokker_planck.py           # 2D FP density field solver
│   │   ├── graph_mobility.py          # Contingent-edge GNN embeddings
│   │   ├── buffer_diversity.py        # Buffer-diversity scoring
│   │   └── meta_herd_detector.py      # Cohort decorrelation detector
│   ├── crypto/
│   │   ├── __init__.py
│   │   └── smpc_scaffold.py           # PSI + SMPC mock attestation
│   ├── precompute/
│   │   ├── __init__.py
│   │   ├── manifold_sweep.py          # Offline parameter sweep script
│   │   └── scenario_generator.py      # 120-node synthetic graph builder
│   ├── data/
│   │   ├── scenarios/                 # Pre-built scenario JSONs
│   │   │   └── kaohsiung_typhoon.json
│   │   └── manifold/                  # Generated manifold .npy/.json files
│   │       └── .gitkeep
│   └── tests/
│       ├── test_fokker_planck.py
│       ├── test_buffer_diversity.py
│       └── test_stampede_index.py
│
├── backend/                           # ★ PERSON 2 TERRITORY
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings & env config
│   │   ├── database.py                # PostgreSQL connection
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── simulation.py          # POST /simulate, GET /scenarios
│   │   │   ├── manifold.py            # GET /manifold/frame
│   │   │   ├── market.py              # GET /market/impact, GET /market/volatility
│   │   │   └── health.py              # GET /health (uptime probe)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── manifold_store.py      # In-memory manifold frame server
│   │   │   ├── pricing_engine.py      # Kyle impact + GARCH volatility
│   │   │   ├── perishable_var.py      # Decay VaR + Scope 3 carbon
│   │   │   ├── stampede_index.py      # Real-time index computation
│   │   │   └── option_escrow.py       # Capacity call option escrow mock
│   │   ├── websockets/
│   │   │   ├── __init__.py
│   │   │   └── stream.py             # WebSocket broadcast (index + manifold)
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   └── celery_worker.py       # Celery async task definitions
│   │   └── models/
│   │       ├── __init__.py
│   │       └── db_models.py           # SQLAlchemy ORM models
│   ├── migrations/                    # Alembic migrations
│   │   └── .gitkeep
│   └── tests/
│       ├── test_pricing.py
│       └── test_manifold.py
│
├── frontend/                          # ★ PERSON 3 TERRITORY
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   │   ├── fallback_demo.mp4          # 30-second pre-rendered fallback
│   │   └── favicon.ico
│   ├── src/
│   │   ├── main.jsx                   # React entry point
│   │   ├── App.jsx                    # Root app with routing
│   │   ├── index.css                  # Global design system
│   │   ├── components/
│   │   │   ├── StampedeGauge.jsx      # 0-100 radial gauge dial
│   │   │   ├── KPICards.jsx           # Cost, SLA, Carbon readout cards
│   │   │   ├── PanicSlider.jsx        # β competitor panic slider
│   │   │   ├── AdoptionSlider.jsx     # Market adoption % slider
│   │   │   ├── TelegraphToggle.jsx    # Options vs. spot booking toggle
│   │   │   ├── TradeoffCard.jsx       # +2.3% entropy cost transparency
│   │   │   ├── ActionButton.jsx       # "TYPHOON HITS" / "RUN STAMPEDE"
│   │   │   └── NetworkGraph/
│   │   │       ├── CytoscapeCanvas.jsx    # Main Cytoscape.js renderer
│   │   │       ├── DensityOverlay.jsx     # Fokker-Planck density heatmap
│   │   │       └── ShockLine.jsx          # Critical density threshold line
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js        # WS connection manager
│   │   │   ├── useManifold.js         # Manifold frame interpolator
│   │   │   └── useStampedeIndex.js    # Index state manager
│   │   ├── services/
│   │   │   ├── api.js                 # REST API client
│   │   │   └── manifoldInterpolator.js # Client-side frame interpolation
│   │   ├── data/
│   │   │   └── mockManifold.json      # Mock manifold for offline UI dev
│   │   └── utils/
│   │       └── constants.js           # Shared frontend constants
│   └── tests/
│       └── App.test.jsx
│
└── scripts/                           # DevOps & utility scripts
    ├── init_db.sql                     # PostgreSQL schema init
    ├── seed_manifold.sh               # Load manifold data into Redis
    └── deploy.sh                      # Cloud deployment helper
```

> [!NOTE]
> **Conflict-free guarantee:** Person 1 only touches `ai_engine/`, Person 2 only touches `backend/` + `docker-compose.yml` + `scripts/`, Person 3 only touches `frontend/`. The `shared/` directory is edited collaboratively in Phase 1 only, then frozen.

---

## 2. Shared API Contracts (JSON Schemas)

These contracts are the **handshake** between all three tracks. They are finalized in Phase 1 (Hours 0–4) and frozen before parallel development begins.

### 2.1 Disruption Event (Sentinel → Backend)
```json
{
  "event_id": "evt_001",
  "timestamp": "2025-08-20T10:00:00Z",
  "event_type": "port_closure",
  "source": "GDELT_corroborated",
  "confidence": 0.91,
  "corroboration_latency_ms": 400,
  "affected_nodes": ["node_kaohsiung_port", "node_tw_semi_hub"],
  "self_influence_filtered": true,
  "raw_signal_count": 14,
  "filtered_signal_count": 11
}
```

### 2.2 Triage Report (Triage → Backend → Frontend)
```json
{
  "event_id": "evt_001",
  "blast_radius": {
    "direct_affected": 8,
    "tier2_cascade": 34,
    "total_exposed": 42
  },
  "graph_mobility_score": 0.67,
  "buffer_diversity_scores": [
    { "firm_id": "firm_A", "d_buffer": 0.82 },
    { "firm_id": "firm_B", "d_buffer": 0.31 }
  ],
  "phased_release_schedule": {
    "W1": ["firm_A", "firm_C"],
    "W3": ["firm_B", "firm_D"],
    "W5": ["firm_E"]
  },
  "contingent_edges_activated": 12,
  "topology_ensemble_count": 5
}
```

### 2.3 Reflex Decision (Reflex → Backend → Frontend)
```json
{
  "event_id": "evt_001",
  "strategy": "temporal_dephasing",
  "stampede_index_before": 87,
  "stampede_index_after": 21,
  "density_field": {
    "lanes": 10,
    "weeks": 6,
    "grid": [[0.12, 0.08], [0.45, 0.22]]
  },
  "dephasing_schedule": {
    "W1": { "lane_ids": ["lane_3", "lane_7"], "allocation_pct": 0.35 },
    "W3": { "lane_ids": ["lane_1", "lane_9"], "allocation_pct": 0.40 },
    "W5": { "lane_ids": ["lane_5"],           "allocation_pct": 0.25 }
  },
  "entropy_budget": {
    "total_budget": 0.023,
    "spent": 0.019,
    "randomized_routes": 4
  },
  "options_exercised": [
    { "lane_id": "lane_3", "capacity_units": 50, "strike_price": 1200, "spot_price": 1608 }
  ],
  "cost_summary": {
    "total_cost_usd": 3100000,
    "sla_miss_pct": 4.0,
    "carbon_delta_pct": 6.0
  }
}
```

### 2.4 Stampede Index Frame (WebSocket — Backend → Frontend)
```json
{
  "timestamp": "2025-08-20T10:00:30Z",
  "tick": 42,
  "stampede_index": 21.4,
  "components": {
    "spearman_rho": 0.18,
    "depletion_velocity": 0.12,
    "rate_volatility": 0.34
  },
  "naive_index": 87.2,
  "naive_components": {
    "spearman_rho": 0.89,
    "depletion_velocity": 0.78,
    "rate_volatility": 0.91
  },
  "market_impact": {
    "naive_price_delta_pct": 34.2,
    "option_price_delta_pct": 4.1
  },
  "kpi": {
    "cost_usd": 3100000,
    "sla_miss_pct": 4.0,
    "carbon_delta_pct": 6.0
  },
  "naive_kpi": {
    "cost_usd": 12400000,
    "sla_miss_pct": 23.0,
    "carbon_delta_pct": 19.0
  }
}
```

### 2.5 Manifold Frame (Precomputed — Backend → Frontend)
```json
{
  "params": {
    "beta": 0.6,
    "adoption_pct": 0.40,
    "shock_intensity": 0.85
  },
  "frame_id": 142,
  "stampede_index_trajectory": [12, 14, 87, 92, 88, 85],
  "ai_index_trajectory":      [12, 14, 19, 21, 20, 19],
  "node_states": [
    { "id": "node_01", "capacity_pct": 0.45, "is_bottleneck": true, "lane_price_delta": 0.34 },
    { "id": "node_02", "capacity_pct": 0.92, "is_bottleneck": false, "lane_price_delta": 0.02 }
  ],
  "density_field_snapshot": [[0.1, 0.2], [0.4, 0.8]],
  "meta_herd_detected": false,
  "entropy_budget_active": false
}
```

### 2.6 Simulation Config (Frontend → Backend)
```json
{
  "scenario_id": "kaohsiung_typhoon",
  "beta": 0.6,
  "market_adoption_pct": 0.40,
  "shock_intensity": 0.85,
  "mode": "ai_vs_naive",
  "manual_override": null
}
```

---

## 3. REST API Endpoints (Person 2 implements, Person 3 consumes)

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/health` | Uptime probe | — | `{ "status": "ok", "uptime_s": 3600 }` |
| `GET` | `/api/scenarios` | List available scenarios | — | `[{ "id": "kaohsiung_typhoon", "name": "..." }]` |
| `POST` | `/api/simulate` | Trigger a simulation run | `simulation_config.json` | `reflex_decision.json` |
| `GET` | `/api/manifold/frame?beta=0.6&adoption=0.4&shock=0.85` | Fetch precomputed manifold frame | Query params | `manifold_frame.json` |
| `GET` | `/api/market/impact?q=500&d=2000` | Compute Kyle price impact | Query params | `market_impact.json` |
| `GET` | `/api/market/volatility` | Current GARCH lane volatility | — | `{ "sigma": 0.12, "index": 45.2 }` |
| `WS` | `/ws/simulation` | Live Stampede Index stream | `simulation_config.json` on connect | Continuous `stampede_index.json` frames |

---

## 4. Step-by-Step Work Breakdown Per Person

---

### 🔬 Person 1: AI/ML Engineer — Step-by-Step

#### Phase 1 (Hours 0–8): Foundation & Scenario Data

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 1.1 | Set up `ai_engine/` Python project | `pyproject.toml`, `requirements.txt` | Dependencies: `numpy`, `scipy`, `networkx`, `torch`, `torch-geometric`, `lightgbm`, `shap`, `pydantic` |
| 1.2 | Write the 120-node synthetic graph generator | `precompute/scenario_generator.py` | Generate nodes (ports, hubs, factories), edges (shipping lanes), contingent substitution edges. Output: `data/scenarios/kaohsiung_typhoon.json` |
| 1.3 | Define contingent edge schema | `shared/graph_schema/supply_network.json` | Node attrs: `id`, `type`, `capacity`, `lat/lon`. Edge attrs: `lane_id`, `cost`, `transit_days`, `is_contingent`, `activation_condition` |
| 1.4 | Review and sign off on all `shared/api_schemas/` | — | Ensure AI output shapes match backend expectations |
| 1.5 | Write `shared/constants.py` | `shared/constants.py` | `W1=0.45`, `W2=0.35`, `W3=0.20`, `LAMBDA=0.5`, `GAMMA=1.5`, `ALPHA_QUANTILE=0.05` |

#### Phase 1.5 (Hours 8–16): Fokker-Planck Solver & Manifold Sweep ★ CRITICAL PATH

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 1.6 | Implement 2D Fokker-Planck finite-difference solver | `models/fokker_planck.py` | Discretize lanes × weeks grid. Use explicit Euler stepping. Input: initial agent density, drift (herd signal), diffusion (entropy). Output: density field `ρ(lane, week, t)` |
| 1.7 | Build the temporal de-phasing optimizer | `agents/reflex.py` | Given FP density field, compute optimal phased allocation schedule (W1/W3/W5) that minimizes peak density at any single node |
| 1.8 | Implement entropy budget allocator | `agents/reflex.py` | Budget = 2.3% of total cost. Randomly perturb `N` route assignments weighted by inverse density. Track spend vs. budget |
| 1.9 | Write the offline manifold sweep script | `precompute/manifold_sweep.py` | Sweep: β ∈ [0.1, 0.9] (5 steps), adoption ∈ [0, 0.8] (5 steps), shock ∈ [0.3, 1.0] (4 steps) → 100+ states. For each: run FP solver, compute Stampede Index, record trajectories. Save to `data/manifold/` as JSON |
| 1.10 | Generate the manifold dataset | `data/manifold/*.json` | Run `manifold_sweep.py`. Verify output frames match `manifold_frame.json` schema. Hand off to Person 2 |

#### Phase 2 (Hours 16–28): Agent Pipeline

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 1.11 | Build Sentinel agent (NLP extraction) | `agents/sentinel.py` | Parse mock GDELT events → extract affected nodes, confidence score. Apply self-influence decorrelation: tag decisions from prior STAMPEDE actions, down-weight correlated signals |
| 1.12 | Build buffer-diversity scorer | `models/buffer_diversity.py` | Implement: `D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))`. Input: SKU-level buffer vectors per firm |
| 1.13 | Build Triage agent | `agents/triage.py` | Combine: blast radius (BFS over contingent graph), buffer-diversity scores, phased release schedule. Output: `triage_report.json` |
| 1.14 | Build graph mobility scorer | `models/graph_mobility.py` | Compute ensemble of topologies by activating/deactivating contingent edges. Mobility = variance of shortest-path distributions across ensemble |
| 1.15 | Implement Stampede Index computation | (function in `agents/reflex.py` or standalone) | Exact formula: `S_t = 100 * [w1 * (1+ρ)/2 + w2 * v_deplete + w3 * σ_rate]`. Must produce identical output for naive and AI panels |

#### Phase 3 (Hours 28–38): Advanced Features

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 1.16 | Implement meta-herd cohort detector | `models/meta_herd_detector.py` | Detect when ≥3 firms adopt identical de-phasing patterns (cosine similarity > 0.85). Trigger entropy budget reallocation |
| 1.17 | Scaffold PSI/SMPC mock | `crypto/smpc_scaffold.py` | Binary intersection: each firm submits hashed set of bottleneck node IDs. Compute intersection cardinality + ε-DP noise. No actual cryptographic protocol needed for MVP |
| 1.18 | Write invariant validation tests | `tests/` | Test: Stampede Index ∈ [0,100]. Test: FP density field sums to 1.0 ± ε. Test: entropy budget never overspent |

#### Phase 4 (Hours 38–48): Defense Prep

| Step | Task | Output | Details |
|------|------|--------|---------|
| 1.19 | Write formula reference sheet | Markdown doc | All equations with variable definitions for Q&A defense |
| 1.20 | Verify mathematical invariants end-to-end | Test results | Run full Kaohsiung scenario: assert 87→21 index transition, $12.4M→$3.1M cost reduction |

---

### ⚙️ Person 2: Backend & Infrastructure Engineer — Step-by-Step

#### Phase 1 (Hours 0–8): Cloud Deployment & API Skeleton

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 2.1 | Initialize `backend/` Python project | `pyproject.toml`, `requirements.txt` | Dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `redis`, `celery`, `websockets`, `pydantic`, `numpy` |
| 2.2 | Write FastAPI skeleton with health endpoint | `app/main.py`, `app/routers/health.py` | `GET /health` → `{"status": "ok"}`. Include CORS middleware for `*` origins |
| 2.3 | Write `docker-compose.yml` | Root `docker-compose.yml` | Services: `backend` (FastAPI), `frontend` (Vite/Nginx), `redis`, `postgres`, `celery_worker`. Expose ports 8000 (API), 3000 (UI), 5432 (DB) |
| 2.4 | Write all Dockerfiles | `backend/Dockerfile`, `frontend/Dockerfile`, `ai_engine/Dockerfile` | Backend: Python 3.11 slim. Frontend: Node 20 + nginx. AI engine: Python 3.11 + numpy |
| 2.5 | Deploy to Render/Railway | Live URL | Push `docker-compose.yml`, verify `/health` returns 200 from public URL. **This is the critical compliance checkpoint.** |
| 2.6 | Set up PostgreSQL schema | `scripts/init_db.sql`, `app/database.py` | Tables: `scenarios`, `simulation_runs`, `manifold_frames`. Keep minimal for MVP |
| 2.7 | Stub all API endpoints with mock responses | `app/routers/*.py` | Every endpoint from the API table returns hardcoded JSON matching the schema. Person 3 can immediately code against these |
| 2.8 | Set up Git branches | — | Create `dev-ai`, `dev-backend`, `dev-frontend` branches. Push initial structure |

#### Phase 1.5 (Hours 8–16): Manifold Store & Frame Server ★ CRITICAL PATH

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 2.9 | Build manifold ingestion pipeline | `app/services/manifold_store.py` | Load Person 1's manifold JSON files into a Python dict keyed by `(β, adoption, shock)` tuple. Hold in-memory (RAM) for instant lookup |
| 2.10 | Implement `GET /api/manifold/frame` | `app/routers/manifold.py` | Accept query params `beta`, `adoption`, `shock`. Snap to nearest precomputed grid point. Return frame in <5ms |
| 2.11 | Implement WebSocket `/ws/simulation` | `app/websockets/stream.py` | On connect: receive `simulation_config.json`. Stream `stampede_index.json` frames at 30fps by iterating through manifold trajectory. Support pause/resume |
| 2.12 | Write `scripts/seed_manifold.sh` | `scripts/seed_manifold.sh` | Copy Person 1's manifold output to backend data directory. Validate schema compliance |

#### Phase 2 (Hours 16–28): Financial Engines

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 2.13 | Implement Kyle price impact function | `app/services/pricing_engine.py` | `P_lane(t) = P0 * (1 + λ * (Q/D)^γ)`. Default: `λ=0.5`, `γ=1.5`. Expose via `GET /api/market/impact` |
| 2.14 | Implement GARCH(1,1) volatility index | `app/services/pricing_engine.py` | Simulate realized lane-rate volatility using GARCH. Update every tick. Expose via `GET /api/market/volatility` |
| 2.15 | Implement Stampede Index server-side | `app/services/stampede_index.py` | Mirror Person 1's formula exactly. Compute both naive and AI panels per tick. Feed into WebSocket stream |
| 2.16 | Set up Celery worker | `app/tasks/celery_worker.py` | Redis broker. Define `run_simulation` task that loads scenario, runs through manifold, broadcasts via WS |

#### Phase 3 (Hours 28–38): Escrow & Perishable Logic

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 2.17 | Implement capacity option escrow mock | `app/services/option_escrow.py` | Track: option holder, strike price, expiry, lane_id. On exercise: deduct from lane capacity without spot market impact |
| 2.18 | Implement perishable VaR routing | `app/services/perishable_var.py` | Arrhenius decay: `k(T) = A * exp(-Ea/RT)`. Compute α-quantile of spoilage probability. Add Scope 3 CO2e penalty for re-production |
| 2.19 | Wire WebSocket state broadcasts for all panels | `app/websockets/stream.py` | Broadcast: index frame, node states, density field, market impact — all in single JSON frame per tick |
| 2.20 | Implement manual override endpoint | `app/routers/simulation.py` | `POST /api/simulate/override` — accepts `{ "lane_id": "lane_3", "action": "grab" }`. Updates simulation state mid-stream |

#### Phase 4 (Hours 38–48): Hardening

| Step | Task | Output | Details |
|------|------|--------|---------|
| 2.21 | Freeze Docker image & re-deploy | Live URL | Final build. Verify CORS, WebSocket connectivity, and `/health` from external browser |
| 2.22 | Set up uptime monitoring | — | Simple cron or external ping to `/health` every 60s |
| 2.23 | Write deployment runbook | Markdown doc | Exact steps to redeploy from scratch in case of cloud provider issues |

---

### 🎨 Person 3: Frontend Engineer — Step-by-Step

#### Phase 1 (Hours 0–8): UI Scaffold & Design System

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 3.1 | Initialize Vite + React project | `frontend/` | `npx -y create-vite@latest ./ --template react`. Install: `cytoscape`, `cytoscape-fcose`, `react-cytoscapejs`, `recharts` |
| 3.2 | Design and implement global CSS | `src/index.css` | Dark theme. Color palette: Deep navy `#0a0e27` bg, Electric blue `#00d4ff` accents, Warning red `#ff3366`, Safe green `#00ff88`. Use Inter font. Glass morphism panels |
| 3.3 | Build Stampede Index gauge component | `src/components/StampedeGauge.jsx` | SVG radial gauge, 0–100, with color gradient (green→yellow→red). Animated needle. Dual display: Naive (left) vs AI (right) |
| 3.4 | Build KPI readout cards | `src/components/KPICards.jsx` | 3 cards: Cost ($), SLA Miss (%), Carbon Delta (%). Show naive vs AI side-by-side with animated counters |
| 3.5 | Build Panic Slider (β) | `src/components/PanicSlider.jsx` | Range 0.1–0.9 with real-time value label. Styled as premium glass slider. Emits `onChange` to parent |
| 3.6 | Build Adoption Slider | `src/components/AdoptionSlider.jsx` | Range 0%–80%. Similar style. Shows "Meta-Herd Active" badge when >60% |
| 3.7 | Build action buttons | `src/components/ActionButton.jsx` | Two states: "TYPHOON HITS PORT K" (red pulse) and "RUN SUPPLYCHAINAI" (blue pulse). Click handlers |
| 3.8 | Wire mock data for all components | `src/data/mockManifold.json` | Hardcode one full manifold frame from the schema. All components render with mock data immediately |

#### Phase 1.5 (Hours 8–16): Manifold Interpolation ★ CRITICAL PATH

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 3.9 | Build WebSocket connection hook | `src/hooks/useWebSocket.js` | Connect to `ws://backend:8000/ws/simulation`. Handle reconnect. Parse incoming JSON frames |
| 3.10 | Build manifold frame interpolator | `src/services/manifoldInterpolator.js` | Given two adjacent precomputed frames, linearly interpolate node states, index values, and density fields for smooth 60fps animation |
| 3.11 | Build `useManifold` hook | `src/hooks/useManifold.js` | Manages slider state → fetches manifold frame → feeds interpolator → outputs smooth animation state |
| 3.12 | Wire sliders to manifold lookups | `src/App.jsx` | β slider + adoption slider changes trigger manifold frame fetch. Verify <16ms render latency |

#### Phase 2 (Hours 16–28): Cytoscape Network Visualization

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 3.13 | Build Cytoscape canvas component | `src/components/NetworkGraph/CytoscapeCanvas.jsx` | Render 120-node supply network. Use `fcose` layout. Nodes colored by capacity % (green→red). Edges weighted by flow |
| 3.14 | Build density field overlay | `src/components/NetworkGraph/DensityOverlay.jsx` | Canvas overlay rendering the Fokker-Planck density as a heatmap gradient behind the graph nodes |
| 3.15 | Build shock line indicator | `src/components/NetworkGraph/ShockLine.jsx` | Animated dashed line showing the critical density threshold. Pulses red when density crosses it |
| 3.16 | Implement split-screen layout | `src/App.jsx` | Left panel: Naive market (no AI). Right panel: SupplyChainAI active. Both driven by same scenario but different computation paths |
| 3.17 | Implement click-to-act on graph nodes | `CytoscapeCanvas.jsx` | Judge clicks a node → sends override to backend → density solver reacts. Visual: clicked node flashes, surrounding allocations shift |

#### Phase 3 (Hours 28–38): Telegraph Toggle & Trade-off Cards

| Step | Task | Output File | Details |
|------|------|-------------|---------|
| 3.18 | Build Telegraph Toggle component | `src/components/TelegraphToggle.jsx` | Flip switch: "Spot Booking" (red aura, +34% price animation) vs "Option Exercise" (green calm, +4% tag). Side-by-side price impact bars |
| 3.19 | Build Transparency Trade-off card | `src/components/TradeoffCard.jsx` | Glass card: "+2.3% deliberate entropy cost → 61% reduction in systemic disruption". Animated reveal on demo close |
| 3.20 | Build meta-herd visual indicator | In gauge/graph components | When adoption >60%: gray route pulses appear on graph, entropy budget meter activates, "Meta-Herd Detected" badge |
| 3.21 | Implement demo flow state machine | `src/App.jsx` | Sequential states: `IDLE` → `SHOCK_FIRED` → `NAIVE_COLLAPSE` → `AI_ACTIVE` → `JURY_INTERACTIVE` → `TELEGRAPH_COMPARE` → `META_HERD` → `CLOSE`. Button clicks advance state |

#### Phase 4 (Hours 38–48): Polish & Rehearsal

| Step | Task | Output | Details |
|------|------|--------|---------|
| 3.22 | Record 30-second fallback MP4 | `public/fallback_demo.mp4` | Screen-record the full demo flow. Embed in frontend container as emergency backup |
| 3.23 | Optimize animations for 60fps | All components | Profile with Chrome DevTools. Reduce Cytoscape re-renders. Use `requestAnimationFrame` for gauge |
| 3.24 | Rehearse 3-minute pitch | — | Run through the exact click sequence from the demo script. Time each segment. Adjust transitions |
| 3.25 | Build presentation mode toggle | `src/App.jsx` | Hidden keyboard shortcut (e.g., `Ctrl+Shift+P`) to enter full-screen presentation mode, hiding dev controls |

---

## 5. Git Branching & Merge Strategy

```
main (protected)
  ├── dev-ai       ← Person 1 works here (ai_engine/ + shared/)
  ├── dev-backend  ← Person 2 works here (backend/ + docker-compose.yml + scripts/)
  └── dev-frontend ← Person 3 works here (frontend/)
```

**Rules:**
1. `shared/` is edited only in Phase 1. After Phase 1, it is frozen on `main` and all branches rebase.
2. Each person merges to `main` via PR at Phase 3 integration point (Hour 28).
3. Final freeze: No commits after Hour 44 (4-hour buffer before deadline).

---

## 6. Verification Plan

### Automated Tests
```bash
# Person 1: AI engine tests
cd ai_engine && python -m pytest tests/ -v

# Person 2: Backend tests
cd backend && python -m pytest tests/ -v

# Person 3: Frontend tests  
cd frontend && npm test

# Integration: Full stack via Docker
docker-compose up --build
curl http://localhost:8000/health
# Open http://localhost:3000 and run through demo flow
```

### Manual Verification
- **Cloud URL:** Verify `/health` returns 200 from an external browser (not localhost)
- **WebSocket:** Open browser console, confirm WS frames arrive at 30fps
- **Demo Script:** Full 3-minute run-through with timer, targeting the exact click sequence from Section 4 of the V3 blueprint
- **Fallback Video:** Verify MP4 plays from the frontend container without network dependency
- **Mathematical Invariants:** Stampede Index always ∈ [0, 100]; naive index > AI index for all scenarios; cost reduction ≈ 75% ($12.4M → $3.1M)
