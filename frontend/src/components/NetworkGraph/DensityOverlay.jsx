import { useEffect, useRef } from 'react';
import './DensityOverlay.css';

/**
 * Density Overlay Component
 * Renders the Fokker-Planck density field as a heatmap behind the Cytoscape graph
 */
export default function DensityOverlay({
  densityField = [],
  width = 800,
  height = 600
}) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !densityField.length) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    // Set canvas dimensions
    canvas.width = width;
    canvas.height = height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (!densityField.length || !densityField[0].length) return;

    const rows = densityField.length;
    const cols = densityField[0].length;

    // Find min and max values for normalization
    let minVal = Infinity;
    let maxVal = -Infinity;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = densityField[r][c];
        if (val < minVal) minVal = val;
        if (val > maxVal) maxVal = val;
      }
    }

    // Avoid division by zero
    const range = maxVal - minVal || 1;

    // Draw each cell as a colored rectangle
    const cellWidth = width / cols;
    const cellHeight = height / rows;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = densityField[r][c];
        const normalized = (val - minVal) / range;

        // Use a monochromatic crimson heat map for a sleek, dark aesthetic
        const alpha = normalized * 0.9;
        ctx.fillStyle = `rgba(220, 38, 38, ${alpha})`;
        ctx.fillRect(c * cellWidth, r * cellHeight, cellWidth, cellHeight);

        // Add subtle grid lines
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(c * cellWidth, r * cellHeight, cellWidth, cellHeight);
      }
    }
  }, [densityField, width, height]);

  return (
    <div
      className="density-overlay"
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        opacity: 0.6,
        filter: 'blur(50px)'
      }}
    >
      <canvas ref={canvasRef} className="density-canvas" />
    </div>
  );
}