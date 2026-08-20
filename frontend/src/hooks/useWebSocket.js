import { useEffect, useState, useRef } from 'react';

/**
 * Custom hook for WebSocket connection to backend simulation stream
 * @returns {Object} { data, connected, error }
 */
export function useWebSocket() {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    // Construct WebSocket URL
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/simulation`;

    // Create WebSocket connection
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setConnected(true);
      setError(null);
      console.log('WebSocket connected to', wsUrl);
    };

    wsRef.current.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        setData(parsedData);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
        setError('Failed to parse simulation data');
      }
    };

    wsRef.current.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('WebSocket connection error');
      setConnected(false);
    };

    wsRef.current.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
          // Reconnection logic would go here in a production app
          console.log('Attempting to reconnect...');
        }
      }, 3000);
    };

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []); // Empty deps array - run once on mount

  // Function to send data (if needed for manual overrides, etc.)
  const sendData = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  };

  return {
    data,
    connected,
    error,
    sendData
  };
}