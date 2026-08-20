/**
 * ActionButton — Demo trigger buttons (Typhoon / Run SupplyChainAI)
 */
export default function ActionButton({ label, variant = 'danger', onClick, disabled = false, pulse = false }) {
  let className = `action-btn ${variant}`;
  if (pulse && !disabled) className += ' pulse';

  return (
    <button
      className={className}
      onClick={onClick}
      disabled={disabled}
      style={{ opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
    >
      {label}
    </button>
  );
}
