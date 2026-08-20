# SupplyChainAI — Task Tracker

## Phase 1: Foundation & Project Scaffold

### Root & Shared
- [/] Create `.gitignore`, `.env.example`, `docker-compose.yml`
- [/] Create `shared/api_schemas/` (all 8 JSON schemas)
- [/] Create `shared/graph_schema/supply_network.json`
- [/] Create `shared/constants.py`

### AI Engine (Person 1)
- [x] Scaffold `ai_engine/` directory structure
- [x] Create `Dockerfile`, `requirements.txt`, `pyproject.toml`
- [x] Stub agent modules (sentinel, triage, reflex)
- [x] Stub model modules (fokker_planck, graph_mobility, buffer_diversity, meta_herd_detector)
- [x] Stub crypto module (smpc_scaffold)
- [x] Stub precompute modules (manifold_sweep, scenario_generator)
- [x] Create initial Kaohsiung typhoon scenario data

### Backend (Person 2)
- [x] Scaffold `backend/` directory structure
- [x] Create `Dockerfile`, `requirements.txt`, `pyproject.toml`
- [x] Create FastAPI app with health endpoint
- [x] Stub all routers with mock responses
- [x] Stub all service modules
- [x] Stub WebSocket stream
- [x] Stub Celery worker
- [x] Create DB schema init script

### Frontend (Person 3)
- [x] Initialize Vite + React project in `frontend/`
- [x] Create global CSS design system
- [x] Stub all component files
- [x] Create mock manifold data
- [x] Create hooks and services

### DevOps
- [x] Create deployment scripts
- [ ] Verify `docker-compose up` builds successfully
