import { useEffect, useRef, useState } from 'react';
import './ShockLine.css';

/**
 * Shock Line Indicator Component
 * Displays an animated dashed line showing critical density threshold
 */
export default function ShockLine({
  shockThreshold = 0.5,
  width = 800,
  height = 600
}) {
  const svgRef = useRef(null);
  const [offset, setOffset] = useState(0);

  // Animate the dash offset for flowing effect
  useEffect(() => {
    const animate = () => {
      setOffset((offset + 0.5) % 20); // Adjust speed as needed
      requestAnimationFrame(animate);
    };

    const animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, [offset]);

  useEffect(() => {
    // Update SVG dimensions if needed
    if (!svgRef.current) return;

    const svg = svgRef.current;
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
  }, [width, height]);

  // Calculate line position based on shock threshold
  // Assuming shockThreshold of 0.0 = bottom, 1.0 = top
  const yPosition = height * (1 - shockThreshold); // Invert Y for SVG coordinates

  return (
    <div
      ref={svgRef}
      className="shock-line-container"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none'
      }}
    >
      <svg className="shock-line-svg">
        <defs>
          <linearGradient id="shockGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ff3366" />
            <stop offset="100%" stopColor="#ff6699" />
          </linearGradient>
        </defs>
        <line
          x1="0"
          y1={yPosition}
          x2={width}
          y2={yPosition}
          stroke="var(--accent-red)"
          strokeWidth="1"
          strokeDasharray="10,5"
          strokeDashoffset={offset}
          style={{
            animation: 'flow 4s linear infinite',
          }}
        />
        {/* Optional: Add pulses at intervals */}
        {[0, width * 0.3, width * 0.7, width].map((x, i) => (
          <circle
            key={i}
            cx={x}
            cy={yPosition}
            r={4}
            fill="var(--bg-primary)"
            stroke="var(--accent-red)"
            strokeWidth="1"
            style={{}}
          />
        ))}
      </svg>
    </div>
  );
}