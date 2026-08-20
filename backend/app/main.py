"""
SupplyChainAI — FastAPI Application Entry Point
=================================================

Main application with CORS, routers, WebSocket, and startup events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, simulation, manifold, market

app = FastAPI(
    title="SupplyChainAI API",
    description="Resilience & Sustainability in Global Supply Chains — Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow all for hackathon; restrict in production) ────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(simulation.router, prefix="/api", tags=["Simulation"])
app.include_router(manifold.router, prefix="/api", tags=["Manifold"])
app.include_router(market.router, prefix="/api", tags=["Market"])

# ── WebSocket endpoint ───────────────────────────────────────────
from app.websockets.stream import websocket_simulation
app.add_api_websocket_route("/ws/simulation", websocket_simulation)


@app.on_event("startup")
async def startup():
    """Load precomputed manifold data into memory on startup."""
    # TODO: Load manifold frames from ai_engine/data/manifold/ into RAM
    print("SupplyChainAI Backend starting...")
    print("Manifold data: awaiting precompute from Person 1")


@app.on_event("shutdown")
async def shutdown():
    print("SupplyChainAI Backend shutting down.")
