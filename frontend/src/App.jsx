import React, { useState, useCallback } from 'react';
import './index.css';
import PanicSlider from './components/PanicSlider';
import AdoptionSlider from './components/AdoptionSlider';
import TelegraphToggle from './components/TelegraphToggle';
import ActionButton from './components/ActionButton';
import { DEMO_STATES } from './utils/constants';
import useManifold from './hooks/useManifold';
import SupplyChainFlow from './components/SupplyChainFlow';
import AskSupplyChainAI from './components/AskSupplyChainAI';

function App() {
  const [demoState, setDemoState] = useState(DEMO_STATES.IDLE);
  const [useOptions, setUseOptions] = useState(false);
  const [chatAction, setChatAction] = useState(null); // Track what the chat triggered

  const {
    manifoldData,
    loading,
    beta,
    adoption,
    updateBeta,
    updateAdoption
  } = useManifold();

  // ── Extract supplier data from API ─────────────────────────
  const getNodeStates = useCallback(() => {
    if (!manifoldData) return [];
    return manifoldData.node_states || [];
  }, [manifoldData]);

  // ── Naive market: everyone panics → Supplier B gets crushed ──
  const getNaiveNodeStates = useCallback(() => {
    const states = getNodeStates();
    if (!states.length) return [];
    const naiveStates = JSON.parse(JSON.stringify(states));
    naiveStates.forEach(node => {
      if (node.id.includes('supplier_b')) {
        // Everyone rushes to B → it gets overloaded
        node.capacity_pct = Math.min(1.0, (node.capacity_pct || 0) + beta * 0.9);
        node.is_bottleneck = node.capacity_pct >= 0.75;
      }
      if (node.id.includes('supplier_c')) {
        // Nobody thinks of C → it sits empty
        node.capacity_pct = Math.max(0.05, (node.capacity_pct || 0) - beta * 0.5);
        node.is_bottleneck = false;
      }
      if (node.id.includes('hub_shanghai')) {
        // Shanghai hub gets congested from the B overflow
        node.capacity_pct = Math.min(0.95, (node.capacity_pct || 0) + beta * 0.4);
        node.is_bottleneck = node.capacity_pct >= 0.7;
      }
    });
    return naiveStates;
  }, [getNodeStates, beta]);

  // ── AI-optimized: smart redistribution across all suppliers ──
  const getAINodeStates = useCallback(() => {
    const states = getNodeStates();
    if (!states.length) return [];
    const aiStates = JSON.parse(JSON.stringify(states));
    aiStates.forEach(node => {
      if (node.id.includes('supplier_b')) {
        // AI limits B to prevent overload — caps at moderate usage
        node.capacity_pct = Math.min(0.55, (node.capacity_pct || 0) + beta * 0.15);
        node.is_bottleneck = false;
      }
      if (node.id.includes('supplier_c')) {
        // AI reroutes extra volume to C — it picks up the slack
        node.capacity_pct = Math.min(0.85, (node.capacity_pct || 0) + beta * 0.3);
        node.is_bottleneck = false;
      }
      if (node.id.includes('hub_singapore')) {
        // Singapore hub stays healthy with balanced load
        node.capacity_pct = Math.min(0.70, (node.capacity_pct || 0) + beta * 0.1);
        node.is_bottleneck = false;
      }
      if (node.id.includes('hub_shanghai')) {
        // Shanghai is kept under control
        node.capacity_pct = Math.min(0.50, (node.capacity_pct || 0) + beta * 0.05);
        node.is_bottleneck = false;
      }
      // Port stays offline regardless
      if (node.id.includes('port')) {
        node.capacity_pct = 0;
        node.is_bottleneck = true;
      }
    });
    return aiStates;
  }, [getNodeStates, beta]);

  // ── KPI calculations (both sides react to beta) ─────────────
  const getKPIs = useCallback(() => {
    const b = beta || 0;
    return {
      naive: {
        cost: Math.round(12400000 + b * 6000000),
        sla: Math.round(23 + b * 40),
        carbon: Math.round(19 + b * 8)
      },
      ai: {
        cost: Math.round(3100000 + b * 400000),
        sla: Math.round(4 + b * 3),
        carbon: Math.round(6 + b * 2)
      }
    };
  }, [beta]);

  const kpis = getKPIs();

  // ── Demo Flow ──────────────────────────────────────────────
  const handleShock = () => {
    setDemoState(DEMO_STATES.SHOCK_FIRED);
    // Actually bump the panic slider to show the disruption
    updateBeta(0.7);
  };

  const handleRunAI = () => {
    setDemoState(DEMO_STATES.AI_ACTIVE);
    setChatAction('ai_activated');
    // Clear the action indicator after 3 seconds
    setTimeout(() => setChatAction(null), 3000);
  };

  // Chat triggers a visible simulation change
  const handleChatSimulation = () => {
    // If not already in shock state, trigger it
    if (demoState === DEMO_STATES.IDLE) {
      setDemoState(DEMO_STATES.SHOCK_FIRED);
      updateBeta(0.7);
    }
    // Then activate AI
    setTimeout(() => {
      setDemoState(DEMO_STATES.AI_ACTIVE);
      setChatAction('ai_activated');
      setTimeout(() => setChatAction(null), 3000);
    }, 500);
  };

  // ── Helper: format cost ────────────────────────────────────
  const formatCost = (n) => {
    if (n >= 1000000) return `$${(n / 1000000).toFixed(1)}M`;
    if (n >= 1000) return `$${(n / 1000).toFixed(0)}K`;
    return `$${n}`;
  };

  return (
    <div className="dashboard">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="dashboard-header">
        <div>
          <h1>SupplyChainAI</h1>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 2 }}>
            Real-time supply chain disruption management
          </p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
          <span className={`badge ${demoState !== DEMO_STATES.IDLE ? 'active' : ''}`}>
            {demoState === DEMO_STATES.IDLE ? '● Standby' : '● Live'}
          </span>
          <ActionButton
            label="Simulate Disruption"
            variant="danger"
            onClick={handleShock}
            disabled={demoState !== DEMO_STATES.IDLE}
            pulse={demoState === DEMO_STATES.IDLE}
          />
          <ActionButton
            label="Activate AI"
            variant="safe"
            onClick={handleRunAI}
            disabled={demoState !== DEMO_STATES.SHOCK_FIRED && demoState !== DEMO_STATES.NAIVE_COLLAPSE}
            pulse={demoState === DEMO_STATES.SHOCK_FIRED}
          />
        </div>
      </header>

      {/* ── Scenario Banner ────────────────────────────────── */}
      {demoState !== DEMO_STATES.IDLE && (
        <div className="scenario-banner">
          <span style={{ fontSize: '1.5rem', flexShrink: 0, marginTop: '-4px' }}>⚠</span>
          <div>
            <strong>Active Scenario: Typhoon Hits Kaohsiung Port</strong>
            <p>Port is offline. Suppliers are rerouting shipments. Drag the "Competitor Panic" slider to see how the market reacts.</p>
          </div>
        </div>
      )}

      {/* ── AI Activated Banner ─────────────────────────────── */}
      {chatAction === 'ai_activated' && (
        <div className="ai-banner">
          <span style={{ fontSize: '1.5rem', flexShrink: 0, marginTop: '-4px' }}>i</span>
          <div>
            <strong>AI Activated — Redistributing shipments</strong>
            <p>Watch the "With AI" panel update. The AI is spreading orders across multiple suppliers to prevent overload.</p>
          </div>
        </div>
      )}

      {/* ── Comparison KPI Summary ─────────────────────────── */}
      <div className="kpi-summary-row">
        <div className="kpi-summary-card bad">
          <div className="kpi-summary-label">Without AI</div>
          <div className="kpi-summary-grid">
            <div className="kpi-item">
              <span className="kpi-item-label">Extra Cost</span>
              <span className="kpi-item-value bad">{formatCost(kpis.naive.cost)}</span>
            </div>
            <div className="kpi-item">
              <span className="kpi-item-label">Delayed Orders</span>
              <span className="kpi-item-value bad">{kpis.naive.sla}%</span>
            </div>
            <div className="kpi-item">
              <span className="kpi-item-label">Carbon Impact</span>
              <span className="kpi-item-value">{kpis.naive.carbon}%</span>
            </div>
          </div>
        </div>
        <div className="kpi-vs">vs</div>
        <div className="kpi-summary-card good">
          <div className="kpi-summary-label">With AI</div>
          <div className="kpi-summary-grid">
            <div className="kpi-item">
              <span className="kpi-item-label">Extra Cost</span>
              <span className="kpi-item-value good">{formatCost(kpis.ai.cost)}</span>
            </div>
            <div className="kpi-item">
              <span className="kpi-item-label">Delayed Orders</span>
              <span className="kpi-item-value good">{kpis.ai.sla}%</span>
            </div>
            <div className="kpi-item">
              <span className="kpi-item-label">Carbon Impact</span>
              <span className="kpi-item-value">{kpis.ai.carbon}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Body: Split Screen ─────────────────────────────── */}
      <div className="dashboard-body">
        {/* ── Left Panel: Without AI ──────────────────────── */}
        <div className="split-panel">
          <div className="panel-label naive">Without AI — Everyone panics</div>
          <div className="panel-card">
            <div className="network-title">Supplier Status (Market Panic)</div>
            <SupplyChainFlow
              nodeStates={getNaiveNodeStates()}
              variant="naive"
              beta={beta}
            />
          </div>
        </div>

        {/* ── Right Panel: With AI ────────────────────────── */}
        <div className="split-panel">
          <div className="panel-label ai">With AI — Smart redistribution</div>
          <div className="panel-card">
            <div className="network-title">Supplier Status (AI-Optimized)</div>
            <SupplyChainFlow
              nodeStates={getAINodeStates()}
              variant="ai"
              beta={beta}
            />
          </div>
        </div>
      </div>

      {/* ── Controls Panel ─────────────────────────────────── */}
      <div className="panel-card controls-panel">
        <div className="controls-header">
          <span style={{ display: 'none' }}></span>
          <strong>Simulation Controls</strong>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginLeft: 8 }}>
            Drag the sliders to simulate different market conditions
          </span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-xl)', marginTop: 'var(--space-md)' }}>
          <PanicSlider value={beta} onChange={updateBeta} />
          <AdoptionSlider value={adoption} onChange={updateAdoption} />
          <TelegraphToggle active={useOptions} onToggle={() => setUseOptions(!useOptions)} />
        </div>
      </div>

      {/* ── Chat ──────────────────────────────────────────── */}
      <AskSupplyChainAI
        onTriggerSimulation={handleChatSimulation}
        contextState={{ beta, adoption, naiveKPI: kpis.naive, aiKPI: kpis.ai, useOptions }}
      />
    </div>
  );
}

export default App;