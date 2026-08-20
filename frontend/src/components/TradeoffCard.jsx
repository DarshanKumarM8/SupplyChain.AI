/**
 * TradeoffCard — Transparency trade-off for entropy budget
 */
export default function TradeoffCard() {
  return (
    <div className="tradeoff-card slide-up">
      <div className="tradeoff-cost">+2.3% Entropy Premium</div>
      <div className="tradeoff-benefit">
        Purchased a 61% reduction in systemic herd-induced stockouts.
      </div>
      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-secondary)', marginTop: 'var(--space-md)' }}>
        Deliberate randomization prevents telegraphing private signals.
      </div>
    </div>
  );
}
