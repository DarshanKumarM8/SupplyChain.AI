/**
 * SupplyChainAI — Frontend Constants
 * Mirror of shared/constants.py for client-side use
 */

// ── SupplyChainAI Index Weights ──────────────────────────────
export const INDEX_W1_SPEARMAN = 0.45;
export const INDEX_W2_DEPLETION = 0.35;
export const INDEX_W3_VOLATILITY = 0.20;

// ── Kyle Market Impact ───────────────────────────────────────
export const KYLE_LAMBDA = 0.5;
export const KYLE_GAMMA = 1.5;

// ── Entropy Budget ───────────────────────────────────────────
export const ENTROPY_BUDGET_PCT = 0.023;
export const META_HERD_COSINE_THRESHOLD = 0.85;

// ── Demo Target KPIs ─────────────────────────────────────────
export const DEMO_NAIVE_COST = 12_400_000;
export const DEMO_AI_COST = 3_100_000;
export const DEMO_NAIVE_SLA_MISS = 23.0;
export const DEMO_AI_SLA_MISS = 4.0;
export const DEMO_NAIVE_CARBON = 19.0;
export const DEMO_AI_CARBON = 6.0;
export const DEMO_NAIVE_PRICE_SPIKE = 34.0;
export const DEMO_AI_PRICE_SPIKE = 4.0;
export const DEMO_NAIVE_INDEX_PEAK = 87;
export const DEMO_AI_INDEX_PEAK = 21;

// ── API Configuration ────────────────────────────────────────
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// ── Demo Flow States ─────────────────────────────────────────
export const DEMO_STATES = {
  IDLE: 'IDLE',
  SHOCK_FIRED: 'SHOCK_FIRED',
  NAIVE_COLLAPSE: 'NAIVE_COLLAPSE',
  AI_ACTIVE: 'AI_ACTIVE',
  JURY_INTERACTIVE: 'JURY_INTERACTIVE',
  TELEGRAPH_COMPARE: 'TELEGRAPH_COMPARE',
  META_HERD: 'META_HERD',
  CLOSE: 'CLOSE',
};
