# SupplyChain.AI: Multi-Agent Optimization for Disruption Management

SupplyChain.AI is an advanced, real-time analytics and decision-support platform designed to mitigate cascading failures in global supply chain networks. 

At the core of the platform is an equilibrium simulation engine that models "Meta-Herd" dynamics. In traditional disruption scenarios (e.g., a localized black swan event shutting down a primary logistics hub), human actors exhibit bounded rationality—flocking to the most obvious secondary capacity. This stampede effect inadvertently overloads secondary nodes, leading to severe Service Level Agreement (SLA) degradation, exponential cost inflation, and network collapse. 

SupplyChain.AI utilizes a distributed, least-regret allocation model to calculate optimized routing topologies in real-time, effectively smoothing demand shocks across the network while providing explainable AI (XAI) insights via a conversational interface.

## System Architecture & Capabilities

- **Stochastic Shock Simulation:** Models the divergence between a "Naive Market" equilibrium (where node capacity constraints are breached due to herd behavior) and an "AI-Optimized" topology.
- **Parametric Scenario Modeling:** Dynamic input matrices allow users to manipulate `Beta` (Competitor Panic/Herd Velocity) and `Alpha` (AI Adoption Rate) to instantly compute the impact on multi-dimensional KPIs, including marginal cost variance and carbon footprint delta.
- **LLM-Driven Diagnostic Agent:** An integrated context-aware Natural Language Processing (NLP) agent that parses complex tensor outputs into executive summaries, providing transparent rationale for optimal constraint relaxation and dynamic capacity allocation.
- **High-Fidelity Telemetry Dashboard:** A low-latency, modular React frontend utilizing custom SVG vector mappings to visualize node saturation and flow bottlenecks in real-time.

## Technology Stack

- **Client Layer:** React 18, Vite, Custom CSS Architecture (Zero-dependency layout design for high-performance rendering).
- **Application Layer:** Python 3.11, FastAPI, Uvicorn, ASGI asynchronous processing.
- **Intelligence Layer:** OpenAI GPT-4o-mini integration with a resilient, deterministic fallback heuristic system for sustained operations during rate limits.
- **Deployment Infrastructure:** Vercel (Client Distribution) and Render (API Microservices).

## Core Contributors

This system was architected and implemented with equal, synergistic contributions from our core engineering team:

- **Irudaya Jason J:** *Lead Client Architect & State Management.* Engineered the reactive telemetry dashboard, real-time parametric UI components, and the seamless integration of the asynchronous NLP chat agent into the presentation layer.
- **M Darshan Kumar:** *Infrastructure & Core API Engineering.* Architected the FastAPI backend, managed the asynchronous application layer, orchestrated the Render deployment pipeline, and maintained repository CI/CD infrastructure.
- **Mithun A:** *Simulation Logic & Data Pipeline.* Designed the deterministic fallback models, integrated the core API payload structures, and managed the data harmonization between the simulation engine and the client interface.
- **Mohammed Nahyan Khan:** *Algorithmic Optimization & LLM Integration.* Engineered the conversational XAI logic, defined the prompt orchestration schemas, and developed the edge-case error handling and contextual formatting for the AI module.

## Deployment & Execution

### Environment Instantiation (Backend)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run_chat_server.py
```
*API instantiates on `http://localhost:8000`*

### Environment Instantiation (Frontend)
```bash
cd frontend
npm install
npm run dev
```
*Client instantiates on `http://localhost:5173`*

### Production Topography
- **Backend API:** Hosted via Render.
- **Frontend Client:** Deployed via Vercel Edge Network, dynamically bound to the production API via environment variable injection (`VITE_API_URL`).
