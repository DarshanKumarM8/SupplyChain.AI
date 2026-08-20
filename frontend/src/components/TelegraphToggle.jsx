/**
 * TelegraphToggle — Switch between Naive Spot Booking and Option Exercise
 */
export default function TelegraphToggle({ active, onToggle }) {
  return (
    <div className="slider-container">
      <div className="slider-header" style={{ marginBottom: 'var(--space-sm)' }}>
        <span className="slider-label">Execution Strategy</span>
      </div>
      <div className="toggle-container">
        <div className={`toggle-label ${!active ? 'inactive' : ''}`}>
          Spot Booking<br/>
          <span style={{ fontSize: 'var(--text-xs)', opacity: 0.8 }}>+34% Price Spike</span>
        </div>
        <div className={`toggle-switch ${active ? 'active' : ''}`} onClick={onToggle}>
          <div className="toggle-knob"></div>
        </div>
        <div className={`toggle-label ${active ? 'active' : ''}`}>
          Option Escrow<br/>
          <span style={{ fontSize: 'var(--text-xs)', opacity: 0.8 }}>+4% Price Spike</span>
        </div>
      </div>
    </div>
  );
}
