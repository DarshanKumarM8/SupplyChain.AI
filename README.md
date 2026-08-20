# SupplyChainAI Project Overview

## Problem Statement
**PROBLEM STATEMENT 7: SupplyChain.AI – Resilience & Sustainability in Global Supply Chains**
**Domain:** Logistics & Supply Chain
**Problem Statement:** Global supply chains remain brittle and environmentally unsustainable:
- Single-point-of-failure dependencies cause widespread disruptions (seen in 2020-2023)
- 90% of supply chain carbon emissions are hidden in Tier 2+ suppliers
- Counterfeit products infiltrate legitimate supply networks
- Small suppliers lack visibility into procurement forecasts
- Waste and inefficiency lead to 30-40% product spoilage in perishables

**SDG Alignment:** SDG 8 (Decent Work), SDG 9 (Industry Innovation), SDG 12 (Responsible Consumption), SDG 13 (Climate Action), SDG 17 (Partnerships)

---

## SupplyChainAI: Advanced Execution Plan (V2)

### 1. Strategic Pipeline Upgrades (The Vulnerability Fixes)
The architecture addresses market impact and prevents self-fulfilling feedback loops:
* **Self-Influence Decorrelation Wrapper:** The Sentinel and Triage agents track decisions deployed by SupplyChainAI. Market signals causally linked to those decisions are down-weighted in confidence scoring to prevent the platform from chasing its own tail.
* **Contingent-Edge Graph & Mobility Scoring:** The static GraphSAGE embedding is augmented with a contingent-edge model that learns from past substitution events. Triage will report blast radii as an ensemble over dynamic topologies, accompanied by a "Graph Mobility Score."
* **Temporal De-Phasing & Entropy Budget:** The Reflex Agent shifts from spatial de-phasing ("which lane") to temporal de-phasing ("which week"). It maintains a belief distribution over competitor deployments and spends an entropy budget on deliberately randomized exploration to prevent telegraphing private signals.
* **Quiet Coalitions (PSI + SMPC):** The system uses Private Set Intersection and Secure Multi-Party Computation to allow firms to attest binary capacity availability without revealing proprietary bills of materials, injecting differential privacy noise into aggregates.
* **Rot-Aware Routing & Options Escrow:** Routing optimizes for the quantile of decay (Value-at-Risk) and Scope 3 replacement carbon. Instead of booking capacity outright, the system purchases Call Options on Capacity priced off a lane-volatility index.

### 2. Division of Labor (3-Person Architecture)
* **Person 1: AI/ML Engineer (Game Theory & Modeling) - `ai_engine`**
  * Fokker-Planck & Entropy: Density field over rerouting strategies, tipping-point detector.
  * Contingent-Edge GNN: Upgrades PyTorch Geometric model for dynamic edges.
  * Decorrelation Wrapper: Instrument validity loop into Sentinel agent.
  * SMPC Scaffolding: Mocks Private Set Intersection logic.

* **Person 2: Backend & DevOps Engineer (Financial Engineering & Orchestration) - `backend`**
  * Core Infrastructure: Python 3.10/3.11, FastAPI server, PostgreSQL, Redis/Celery asynchronous workers.
  * Options Pricing Engine: GARCH-style lane-volatility index and mock smart-contract escrow.
  * Rot-Aware Routing API: Probabilistic VaR + Scope-3 carbon penalty.
  * SupplyChainAI Index Endpoint: WebSocket stream for 0-100 SupplyChainAI Index.

* **Person 3: Frontend Engineer (Interactive Demo & Visualization) - `frontend`**
  * The Panic Dashboard: React dashboard with SupplyChainAI Index dial, panic slider, manual override.
  * Density Field Cytoscape: Graph visualization with Fokker-Planck density field overlays.
  * Options vs. Telegraph Toggle: Visual state switch for pre-booking vs. option-based execution.
  * Demo Choreography: 3-minute flow script.

### 3. Setup & Prerequisites
* **Repository:** Public GitHub repository (under NahyanKhan account).
* **Directories:** `/frontend`, `/backend`, `/ai_engine`.
* **API Contracts:** Strict JSON schemas drafted before logic.
* **Infrastructure:** Public cloud platform with Docker Compose container deployment.
