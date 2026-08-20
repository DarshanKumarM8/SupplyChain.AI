/**
 * KPICards — Cost, SLA Miss %, Carbon Delta % readout cards
 * Shows animated counters with danger/safe variants
 */
export default function KPICards({ cost = 0, sla = 0, carbon = 0, variant = 'danger', active = false }) {
  const formatCost = (v) => {
    if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
    if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
    return `$${v}`;
  };

  const colorClass = variant === 'danger' ? 'danger' : 'safe';

  return (
    <div className="kpi-grid">
      <div className="kpi-card glass-card">
        <div className="kpi-label">Total Cost</div>
        <div className={`kpi-value ${colorClass}`}>
          {active ? formatCost(cost) : '—'}
        </div>
      </div>
      <div className="kpi-card glass-card">
        <div className="kpi-label">SLA Miss</div>
        <div className={`kpi-value ${colorClass}`}>
          {active ? `${sla.toFixed(1)}%` : '—'}
        </div>
      </div>
      <div className="kpi-card glass-card">
        <div className="kpi-label">Carbon Δ</div>
        <div className={`kpi-value ${colorClass}`}>
          {active ? `+${carbon.toFixed(1)}%` : '—'}
        </div>
      </div>
    </div>
  );
}
