import { useState } from 'react';
import './index.css';
import StampedeGauge from './components/StampedeGauge';
import KPICards from './components/KPICards';
import PanicSlider from './components/PanicSlider';
import AdoptionSlider from './components/AdoptionSlider';
import TelegraphToggle from './components/TelegraphToggle';
import TradeoffCard from './components/TradeoffCard';
import ActionButton from './components/ActionButton';
import { DEMO_STATES } from './utils/constants';

function App() {
  // ── Demo State Machine ────────────────────────────────────
  const [demoState, setDemoState] = useState(DEMO_STATES.IDLE);
  const [beta, setBeta] = useState(0.6);
  const [adoption, setAdoption] = useState(0.0);
  const [useOptions, setUseOptions] = useState(false);

  // ── Simulated Index Values (driven by demo state) ─────────
  const getIndexValues = () => {
    switch (demoState) {
      case DEMO_STATES.IDLE:
        return { naive: 12, ai: 12 };
      case DEMO_STATES.SHOCK_FIRED:
      case DEMO_STATES.NAIVE_COLLAPSE:
        return { naive: Math.min(87, 12 + beta * 100), ai: 12 };
      case DEMO_STATES.AI_ACTIVE:
        return { naive: Math.min(87, 12 + beta * 100), ai: Math.min(27, 12 + beta * 15) };
      case DEMO_STATES.JURY_INTERACTIVE:
        return { naive: Math.min(98, 87 + beta * 15), ai: Math.min(27, 21 + beta * 8) };
      default:
        return { naive: 87, ai: 21 };
    }
  };

  const { naive: naiveIndex, ai: aiIndex } = getIndexValues();

  // ── Demo KPIs ─────────────────────────────────────────────
  const naiveKPI = { cost: 12400000, sla: 23.0, carbon: 19.0 };
  const aiKPI = { cost: 3100000, sla: 4.0, carbon: 6.0 };

  // ── Demo Flow Handlers ────────────────────────────────────
  const handleShock = () => setDemoState(DEMO_STATES.SHOCK_FIRED);
  const handleRunAI = () => setDemoState(DEMO_STATES.AI_ACTIVE);

  // ── Keyboard shortcut for presentation mode ───────────────
  // Ctrl+Shift+P toggles presentation mode (future implementation)

  return (
    <div className="dashboard">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="dashboard-header">
        <h1>⚡ SupplyChainAI</h1>
        <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
          <span className={`badge ${demoState !== DEMO_STATES.IDLE ? 'active' : 'warning'}`}>
            {demoState === DEMO_STATES.IDLE ? '● STANDBY' : '● LIVE'}
          </span>
          <ActionButton
            label="Typhoon Hits Port K"
            variant="danger"
            onClick={handleShock}
            disabled={demoState !== DEMO_STATES.IDLE}
            pulse={demoState === DEMO_STATES.IDLE}
          />
          <ActionButton
            label="Run SupplyChainAI"
            variant="safe"
            onClick={handleRunAI}
            disabled={demoState !== DEMO_STATES.SHOCK_FIRED && demoState !== DEMO_STATES.NAIVE_COLLAPSE}
            pulse={demoState === DEMO_STATES.SHOCK_FIRED}
          />
        </div>
      </header>

      {/* ── Body: Split Screen ─────────────────────────────── */}
      <div className="dashboard-body">
        {/* ── Left Panel: Naive Market ───────────────────── */}
        <div className="split-panel fade-in">
          <div className="panel-label naive">⚠ Naive Market (No AI)</div>
          <div className="glass-card">
            <StampedeGauge value={naiveIndex} label="Market Herd Index" variant="danger" />
          </div>
          <KPICards
            cost={naiveKPI.cost}
            sla={naiveKPI.sla}
            carbon={naiveKPI.carbon}
            variant="danger"
            active={demoState !== DEMO_STATES.IDLE}
          />
        </div>

        {/* ── Right Panel: SupplyChainAI ─────────────────── */}
        <div className="split-panel fade-in">
          <div className="panel-label ai">✓ SupplyChainAI Active</div>
          <div className="glass-card">
            <StampedeGauge value={aiIndex} label="SupplyChainAI Index" variant="safe" />
          </div>
          <KPICards
            cost={aiKPI.cost}
            sla={aiKPI.sla}
            carbon={aiKPI.carbon}
            variant="safe"
            active={demoState !== DEMO_STATES.IDLE}
          />
        </div>
      </div>

      {/* ── Controls Panel ─────────────────────────────────── */}
      <div className="glass-card controls-panel" style={{ marginTop: 'var(--space-md)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-xl)' }}>
          <PanicSlider value={beta} onChange={setBeta} />
          <AdoptionSlider value={adoption} onChange={setAdoption} />
          <TelegraphToggle active={useOptions} onToggle={() => setUseOptions(!useOptions)} />
        </div>
        {demoState === DEMO_STATES.CLOSE && <TradeoffCard />}
      </div>
    </div>
  );
}

export default App;
