import { useEffect, useRef, useState } from 'react';
import Cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';
import './CytoscapeCanvas.css';

/**
 * Cytoscape Canvas Component for rendering the supply chain network
 * Visualizes nodes, edges, density overlays, and shock lines
 */
export default function CytoscapeCanvas({
  nodeStates = [],
  densityField = [],
  shockLine = 0.5,
  onNodeClick = null
}) {
  const containerRef = useRef(null);
  const [cy, setCy] = useState(null);

  useEffect(() => {
    // Initialize Cytoscape when container is available
    if (!containerRef.current) return;

    // Load cytoscape-fcose layout
    Cytoscape.use(fcose);

    const cyInstance = Cytoscape({
      container: containerRef.current,
      elements: [], // Start empty, let the second useEffect populate it
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#111111',
            'background-opacity': 1,
            'label': 'data(label)',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            'color': '#e4e4e7',
            'font-size': '11px',
            'font-weight': 400,
            'width': 'mapData(capacity_pct, 0, 1, 15, 35)',
            'height': 'mapData(capacity_pct, 0, 1, 15, 35)',
            'border-width': 2,
            'border-color': '#3b82f6'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#4b5563',
            'target-arrow-color': '#4b5563',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8
          }
        },
        {
          selector: '.bottleneck',
          style: {
            'border-color': '#ef4444',
            'border-width': 3,
            'background-color': '#2a0a0a'
          }
        },
        {
          selector: ':selected',
          style: {
            'border-width': 3,
            'border-color': '#ffff00'
          }
        }
      ],
      layout: {
        name: 'breadthfirst',
        directed: true,
        padding: 40,
        spacingFactor: 1.2,
        animate: true,
        animationDuration: 1000
      }
    });

    setCy(cyInstance);

    // Cleanup on unmount
    return () => {
      if (cyInstance) {
        cyInstance.destroy();
      }
    };
  }, []); // Initialize ONLY ONCE on mount

  // Update elements when nodeStates or densityField change
  useEffect(() => {
    if (cy) {
      cy.elements().remove();
      cy.add(getElements(nodeStates));
      cy.layout({ name: 'breadthfirst', directed: true, spacingFactor: 1.2, animate: true }).run();
    }
  }, [nodeStates, cy]);

  // Handle node clicks
  useEffect(() => {
    if (cy) {
      const handleClick = (evt) => {
        if (evt.target === cy) return; // Clicked on background

        const node = evt.target;
        const nodeId = node.data('id');

        if (onNodeClick) {
          onNodeClick(nodeId);
        }

        // Visual feedback for clicked node
        node.addClass('clicked');
        setTimeout(() => node.removeClass('clicked'), 300);
      };

      cy.on('tap', 'node', handleClick);

      return () => {
        cy.off('tap', 'node', handleClick);
      };
    }
  }, [cy, onNodeClick]);

  // Generate Cytoscape elements from node states
  function getElements(nodeStates) {
    const elements = {
      nodes: [],
      edges: []
    };

    // Format node IDs to be human-readable
    const formatNodeLabel = (id) => {
      if (!id) return '';
      return id.replace('node_', '')
               .split('_')
               .map(word => word.charAt(0).toUpperCase() + word.slice(1))
               .join(' ');
    };

    // Create nodes
    nodeStates.forEach((node, index) => {
      elements.nodes.push({
        data: {
          id: node.id || `node_${index}`,
          label: formatNodeLabel(node.id) || `Node ${index}`,
          capacity_pct: node.capacity_pct || 0.5,
          is_bottleneck: node.is_bottleneck || false
        },
        classes: node.is_bottleneck ? 'bottleneck' : ''
      });
    });

    // Create edges (simple linear chain for demo - in reality this would come from graph schema)
    for (let i = 0; i < nodeStates.length - 1; i++) {
      elements.edges.push({
        data: {
          id: `edge_${i}_${i+1}`,
          source: nodeStates[i].id || `node_${i}`,
          target: nodeStates[i+1].id || `node_${i+1}`
        }
      });
    }

    return elements;
  }

  return (
    <>
      {!cy && <div className="cytoscape-placeholder">Loading network visualization...</div>}
      <div ref={containerRef} className="cytoscape-container" style={{ opacity: cy ? 1 : 0 }} />
    </>
  );
}