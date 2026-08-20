import { useEffect, useState } from 'react';
import './MetaHerdIndicator.css';

/**
 * MetaHerd Indicator Component
 * Visual indicator showing when meta-herd behavior is detected (adoption > 60%)
 * Shows pulsing gray routes on the network and entropy budget meter
 */
export default function MetaHerdIndicator({
  adoption = 0,
  networkRefs = {}, // Refs to network containers for injecting visual effects
  onEntropyBudgetChange = null // Callback when entropy budget is used
}) {
  const [dots, setDots] = useState([]); // Animated dots for pulsing effect
  const [entropySpent, setEntropySpent] = useState(0); // 0 to 1 (0% to 100% of budget)
  const [pulseInterval, setPulseInterval] = useState(null);

  const ENTROPY_BUDGET_PCT = 0.023; // 2.3% from constants
  const META_HERD_THRESHOLD = 0.60; // 60% adoption triggers meta-herd detection
  const isMetaHerdDetected = adoption > META_HERD_THRESHOLD;

  // Initialize pulsing dots when meta-herd is detected
  useEffect(() => {
    if (isMetaHerdDetected) {
      // Create 3-5 animated dots that will pulse along network routes
      const newDots = Array.from({ length: 4 }, (_, i) => ({
        id: i,
        progress: (i / 4) * 100, // Distribute dots along path
        size: 8 + Math.random() * 4, // Vary sizes slightly
        delay: i * 200 // Stagger animation start times
      }));
      setDots(newDots);

      // Start pulsing animation
      const interval = setInterval(() => {
        setDots(prevDots =>
          prevDots.map(dot => ({
            ...dot,
            progress: (dot.progress + 2) % 100 // Move dots along path
          }))
        );
      }, 50);
      setPulseInterval(interval);
    } else {
      // Clear dots and stop animation when not detected
      setDots([]);
      if (pulseInterval) {
        clearInterval(pulseInterval);
        setPulseInterval(null);
      }
    }
  }, [isMetaHerdDetected, pulseInterval]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (pulseInterval) {
        clearInterval(pulseInterval);
      }
    };
  }, [pulseInterval]);

  // Simulate entropy budget spending when meta-herd is active
  useEffect(() => {
    if (isMetaHerdDetected) {
      // Gradually spend entropy budget over time when meta-herd is detected
      const interval = setInterval(() => {
        setEntropySpent(prev => {
          const newSpent = Math.min(prev + 0.005, 1); // Increment by 0.5% per tick
          if (onEntropyBudgetChange && newSpent >= 0.95) { // Notify when nearly spent
            onEntropyBudgetChange('budget_nearly_depleted');
          }
          return newSpent;
        });
      }, 1000); // Update every second
      return () => clearInterval(interval);
    }
    return () => {};
  }, [isMetaHerdDetected, onEntropyBudgetChange]);

  if (!isMetaHerdDetected) {
    return null; // Don't render anything when not detected
  }

  const entropyBudgetUsed = entropySpent * ENTROPY_BUDGET_PCT * 100; // Convert to percentage
  const entropyBudgetRemaining = (1 - entropySpent) * ENTROPY_BUDGET_PCT * 100;

  return (
    <div className="meta-herd-indicator">
      <div className="meta-herd-badge">
        <div className="meta-herd-icon">⚠️</div>
        <div className="meta-herd-text">
          <strong>META-HERD DETECTED</strong>
          <div className="meta-herd-details">
            Adoption: {(adoption * 100).toFixed(0)}% &gt; 60% threshold
          </div>
        </div>
      </div>

      {/* Animated pulsing dots overlay (would be positioned over network in CSS) */}
      <div className="meta-herd-overlay">
        {dots.map(dot => (
          <div
            key={dot.id}
            className="meta-herd-dot"
            style={{
              left: `${dot.progress}%`,
              width: `${dot.size}px`,
              height: `${dot.size}px`,
              animationDelay: `${dot.delay}ms`
            }}
          />
        ))}
      </div>

      {/* Entropy Budget Meter */}
      <div className="entropy-budget-meter">
        <div className="entropy-label">Entropy Budget:</div>
        <div className="entropy-bar-container">
          <div className="entropy-bar-background">
            <div
              className="entropy-bar-fill"
              style={{ width: `${entropySpent * 100}%` }}
            ></div>
          </div>
          <div className="entropy-stats">
            <span className="entropy-used">+{entropyBudgetUsed.toFixed(2)}% Cost</span>
            <span className="entropy-remaining">-{entropyBudgetRemaining.toFixed(2)}% Risk</span>
          </div>
        </div>
      </div>
    </div>
  );
}