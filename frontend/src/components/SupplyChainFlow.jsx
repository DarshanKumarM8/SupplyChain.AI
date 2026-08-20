import React from 'react';
import './SupplyChainFlow.css';

/**
 * Clean, professional supply chain visualization using HTML/CSS
 * Replaces the ugly Cytoscape graph with intuitive supplier cards
 */
export default function SupplyChainFlow({ nodeStates = [], variant = 'naive', beta = 0 }) {
  // Format raw node data into human-readable supplier info
  const formatNodes = (nodes) => {
    return nodes.map(node => {
      const id = node.id || '';
      const name = id.replace('node_', '')
        .split('_')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');

      const capacity = Math.round((node.capacity_pct || 0) * 100);
      const isBottleneck = node.is_bottleneck || false;
      const isPort = id.includes('port');

      // Determine status based on context
      let status = 'normal';
      let statusLabel = 'Online';

      if (isPort && capacity <= 5) {
        // Port is shut down by the typhoon
        status = 'offline';
        statusLabel = 'Shut Down';
      } else if (isBottleneck) {
        status = 'critical';
        statusLabel = 'Overloaded';
      } else if (variant === 'ai' && capacity < 20) {
        // AI deliberately limited this supplier — that's a GOOD thing
        status = 'limited';
        statusLabel = 'Reduced by AI';
      } else if (variant === 'naive' && capacity < 20) {
        status = 'offline';
        statusLabel = 'Underused';
      } else if (capacity > 80) {
        status = 'warning';
        statusLabel = variant === 'naive' ? 'Near Capacity' : 'High Load';
      } else if (capacity > 60) {
        status = variant === 'naive' ? 'warning' : 'normal';
        statusLabel = variant === 'naive' ? 'Straining' : 'Balanced';
      } else {
        status = 'normal';
        statusLabel = variant === 'ai' ? 'Balanced' : 'Online';
      }

      // Icon based on type
      let icon = '📦';
      if (isPort) icon = '🚢';
      else if (id.includes('hub')) icon = '🏭';

      return { id, name, capacity, isBottleneck, status, statusLabel, icon };
    });
  };

  const suppliers = formatNodes(nodeStates);

  if (!suppliers.length) {
    return (
      <div className="flow-empty">
        <span>Waiting for simulation data…</span>
      </div>
    );
  }

  return (
    <div className={`supply-flow ${variant}`}>
      {suppliers.map((supplier, i) => (
        <React.Fragment key={supplier.id}>
          <div className={`supplier-card ${supplier.status}`}>
            <div className="supplier-icon">{supplier.icon}</div>
            <div className="supplier-info">
              <div className="supplier-name">{supplier.name}</div>
              <div className={`supplier-status ${supplier.status}`}>
                {supplier.statusLabel}
              </div>
            </div>
            <div className="supplier-capacity">
              <div className="capacity-bar-bg">
                <div
                  className={`capacity-bar-fill ${supplier.status}`}
                  style={{ width: `${supplier.capacity}%` }}
                />
              </div>
              <span className="capacity-label">{supplier.capacity}%</span>
            </div>
          </div>
          {i < suppliers.length - 1 && (
            <div className="flow-connector">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 5v14M5 12l7 7 7-7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}
