"""
SupplyChainAI — Shared Constants
================================
Canonical values used across ai_engine, backend, and frontend.
Any change here MUST be reflected in frontend/src/utils/constants.js.
"""

# ── SupplyChainAI Index Weights ──────────────────────────────────
# S_t = 100 * [W1*(1+ρ)/2 + W2*v_deplete + W3*σ_rate]
INDEX_W1_SPEARMAN = 0.45
INDEX_W2_DEPLETION = 0.35
INDEX_W3_VOLATILITY = 0.20
INDEX_ROLLING_WINDOW_SECONDS = 30

# ── Kyle Market Impact Parameters ────────────────────────────────
# P_lane(t) = P0 * (1 + LAMBDA * (Q/D)^GAMMA)
KYLE_LAMBDA = 0.5
KYLE_GAMMA = 1.5

# ── Buffer-Diversity ─────────────────────────────────────────────
# D_buffer(i) = 1 - cos_sim(b_i, mean(b_{-i}))
BUFFER_DIVERSITY_THRESHOLD = 0.4  # Firms below this get priority phased release

# ── Phased Release Windows ───────────────────────────────────────
PHASED_RELEASE_WEEKS = ["W1", "W3", "W5"]

# ── Entropy Budget ───────────────────────────────────────────────
ENTROPY_BUDGET_PCT = 0.023   # 2.3% of total cost allocated to deliberate randomization
META_HERD_COSINE_THRESHOLD = 0.85  # Trigger meta-herd detector above this similarity

# ── Rot-Aware Routing ────────────────────────────────────────────
# Arrhenius decay: k(T) = A * exp(-Ea / (R * T))
ARRHENIUS_A = 1e10            # Pre-exponential factor (1/s), commodity-dependent
ARRHENIUS_EA = 50000.0        # Activation energy (J/mol), typical for fresh produce
GAS_CONSTANT_R = 8.314        # J/(mol·K)
DECAY_VAR_ALPHA = 0.05        # 5th percentile for Value-at-Risk of decay

# ── Scope 3 Carbon ───────────────────────────────────────────────
CO2E_PER_TON_KM_OCEAN = 0.016     # kg CO2e per ton-km (ocean freight)
CO2E_PER_TON_KM_AIR = 0.602       # kg CO2e per ton-km (air freight)
CO2E_PER_TON_KM_TRUCK = 0.062     # kg CO2e per ton-km (truck)
CO2E_PER_TON_KM_RAIL = 0.022      # kg CO2e per ton-km (rail)
CO2E_REPRODUCE_MULTIPLIER = 2.5   # Re-production emits ~2.5x the original manufacturing

# ── GARCH Volatility ─────────────────────────────────────────────
GARCH_OMEGA = 0.00001
GARCH_ALPHA = 0.1
GARCH_BETA = 0.85

# ── Simulation Defaults ──────────────────────────────────────────
DEFAULT_BETA = 0.6               # Default competitor panic parameter
DEFAULT_ADOPTION_PCT = 0.0       # Default market adoption of SupplyChainAI
DEFAULT_SHOCK_INTENSITY = 0.85   # Default disruption severity
DEFAULT_NUM_AGENTS = 120         # Number of buyer agents in simulation

# ── Network Topology ─────────────────────────────────────────────
NODE_TYPES = ["port", "factory", "distribution_hub", "raw_material_source", "end_market"]
LANE_TYPES = ["ocean_freight", "air_freight", "rail", "truck", "intermodal"]

# ── Demo Target KPIs ─────────────────────────────────────────────
# These are the target numbers for the Kaohsiung Typhoon scenario
DEMO_NAIVE_COST_USD = 12_400_000
DEMO_AI_COST_USD = 3_100_000
DEMO_NAIVE_SLA_MISS_PCT = 23.0
DEMO_AI_SLA_MISS_PCT = 4.0
DEMO_NAIVE_CARBON_DELTA_PCT = 19.0
DEMO_AI_CARBON_DELTA_PCT = 6.0
DEMO_NAIVE_PRICE_SPIKE_PCT = 34.0
DEMO_AI_PRICE_SPIKE_PCT = 4.0
DEMO_NAIVE_INDEX_PEAK = 87
DEMO_AI_INDEX_PEAK = 21
