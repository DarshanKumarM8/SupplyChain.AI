import { useEffect, useRef } from 'react';

/**
 * StampedeGauge — SVG Radial Gauge (0-100)
 * Animated needle with color gradient (green → yellow → red)
 */
export default function StampedeGauge({ value = 0, label = 'Index', variant = 'danger' }) {
  const clampedValue = Math.max(0, Math.min(100, value));

  // Map value to angle: 0 → -135°, 100 → 135° (270° sweep)
  const angle = -135 + (clampedValue / 100) * 270;

  // Dynamic color based on value
  const getColor = (v) => {
    if (v < 30) return 'var(--accent-green)';
    if (v < 60) return 'var(--accent-yellow)';
    return 'var(--accent-red)';
  };

  const color = getColor(clampedValue);

  return (
    <div className="gauge-container">
      <svg viewBox="0 0 200 140" width="220" height="160">
        {/* Background arc */}
        <path
          d="M 30 130 A 80 80 0 1 1 170 130"
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth="10"
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d="M 30 130 A 80 80 0 1 1 170 130"
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${(clampedValue / 100) * 377} 377`}
          style={{
            filter: `drop-shadow(0 0 8px ${color})`,
            transition: 'stroke-dasharray 0.6s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.3s ease',
          }}
        />
        {/* Needle */}
        <line
          x1="100"
          y1="130"
          x2="100"
          y2="55"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          style={{
            transformOrigin: '100px 130px',
            transform: `rotate(${angle}deg)`,
            transition: 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
            filter: `drop-shadow(0 0 4px ${color})`,
          }}
        />
        {/* Center dot */}
        <circle cx="100" cy="130" r="5" fill={color} style={{ filter: `drop-shadow(0 0 6px ${color})` }} />
        {/* Scale labels */}
        <text x="25" y="138" fill="var(--text-muted)" fontSize="10" fontFamily="var(--font-mono)">0</text>
        <text x="165" y="138" fill="var(--text-muted)" fontSize="10" fontFamily="var(--font-mono)">100</text>
      </svg>
      <div className="gauge-value" style={{ color, textShadow: `0 0 20px ${color}` }}>
        {Math.round(clampedValue)}
      </div>
      <div className="gauge-label">{label}</div>
    </div>
  );
}
