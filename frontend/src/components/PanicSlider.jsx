/**
 * PanicSlider — Competitor Panic (Beta) Slider
 */
export default function PanicSlider({ value, onChange }) {
  return (
    <div className="slider-container">
      <div className="slider-header">
        <span className="slider-label">Competitor Panic (β)</span>
        <span className="slider-value">{value.toFixed(1)}</span>
      </div>
      <input
        type="range"
        min="0.1"
        max="0.9"
        step="0.1"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: '4px' }}>
        <span>Low</span>
        <span>High</span>
      </div>
    </div>
  );
}
