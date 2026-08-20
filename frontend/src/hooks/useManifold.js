import { useEffect, useState, useCallback, useRef } from 'react';
import { interpolateManifoldFrames } from '../services/manifoldInterpolator';
import { DEMO_STATES } from '../utils/constants';

/**
 * Hook for managing manifold data fetching and interpolation
 * @returns {Object} { manifoldData, loading, error, refresh }
 */
export function useManifold() {
  const [manifoldData, setManifoldData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [beta, setBeta] = useState(0.6); // Default from constants
  const [adoption, setAdoption] = useState(0.0); // Default from constants
  const [shock, setShock] = useState(0.85); // Fixed for MVP
  const [demoState, setDemoState] = useState(DEMO_STATES.IDLE);

  // Cache for storing recently fetched frames to avoid redundant API calls
  const frameCache = useRef(new Map());

  // Fetch manifold frame from backend API
  const fetchManifoldFrame = useCallback(async (betaVal, adoptionVal, shockVal) => {
    const cacheKey = `${betaVal}-${adoptionVal}-${shockVal}`;

    // Check cache first
    if (frameCache.current.has(cacheKey)) {
      return frameCache.current.get(cacheKey);
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/manifold/frame?` +
        new URLSearchParams({
          beta: betaVal.toString(),
          adoption: adoptionVal.toString(),
          shock: shockVal.toString()
        })
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const frameData = await response.json();

      // Cache the result
      frameCache.current.set(cacheKey, frameData);

      return frameData;
    } catch (err) {
      console.error('Failed to fetch manifold frame:', err);
      setError(err.message || 'Failed to load manifold data');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch initial manifold data on mount and when parameters change
  useEffect(() => {
    let isMounted = true;

    const loadInitialData = async () => {
      const frame = await fetchManifoldFrame(beta, adoption, shock);
      if (isMounted && frame) {
        setManifoldData(frame);
      }
    };

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [beta, adoption, shock, fetchManifoldFrame]);

  // Update beta value
  const updateBeta = (newBeta) => {
    setBeta(newBeta);
  };

  // Update adoption value
  const updateAdoption = (newAdoption) => {
    setAdoption(newAdoption);
  };

  // Update shock value
  const updateShock = (newShock) => {
    setShock(newShock);
  };

  // Update demo state
  const updateDemoState = (newState) => {
    setDemoState(newState);
  };

  // Manual refresh function
  const refreshManifoldData = useCallback(async () => {
    // Clear cache to force fresh fetch
    frameCache.current.clear();
    const frame = await fetchManifoldFrame(beta, adoption, shock);
    if (frame) {
      setManifoldData(frame);
    }
  }, [beta, adoption, shock, fetchManifoldFrame]);

  return {
    manifoldData,
    loading,
    error,
    beta,
    adoption,
    shock,
    demoState,
    updateBeta,
    updateAdoption,
    updateShock,
    updateDemoState,
    refreshManifoldData
  };
}

export default useManifold;