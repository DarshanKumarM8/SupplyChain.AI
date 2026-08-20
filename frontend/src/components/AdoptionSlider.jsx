/**
 * AdoptionSlider — Market Adoption % Slider
 */
export default function AdoptionSlider({ value, onChange }) {
  return (
    <div className="slider-container">
      <div className="slider-header">
        <span className="slider-label">Market Adoption</span>
        <span className="slider-value">{(value * 100).toFixed(0)}%</span>
      </div>
      <input
        type="range"
        min="0.0"
        max="0.8"
        step="0.1"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: '4px' }}>
        <span>0%</span>
        <span>80%</span>
      </div>
      {value > 0.6 && (
        <div style={{ textAlign: 'center', marginTop: '8px' }}>
          <span className="badge active">Meta-Herd Detected</span>
        </div>
      )}
    </div>
  );
}
