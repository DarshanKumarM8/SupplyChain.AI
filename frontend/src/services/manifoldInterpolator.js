/**
 * Manifold Frame Interpolator
 * Provides linear interpolation between two precomputed manifold frames
 * for smooth animation of the supply chain visualization
 */

/**
 * Linearly interpolate between two values
 * @param {number} start - Starting value
 * @param {number} end - Ending value
 * @param {number} t - Interpolation factor (0-1)
 * @returns {number} Interpolated value
 */
function lerp(start, end, t) {
  return start + (end - start) * t;
}

/**
 * Interpolate between two numbers or arrays of numbers
 * @param {number|number[]} start - Starting value(s)
 * @param {number|number[]} end - Ending value(s)
 * @param {number} t - Interpolation factor (0-1)
 * @returns {number|number[]} Interpolated value(s)
 */
function interpolateValue(start, end, t) {
  if (Array.isArray(start) && Array.isArray(end)) {
    // Handle arrays (like density_field_snapshot)
    return start.map((val, index) => lerp(val, end[index], t));
  }
  // Handle single numbers
  return lerp(start, end, t);
}

/**
 * Interpolate between two manifold frames
 * @param {Object} frameA - First manifold frame
 * @param {Object} frameB - Second manifold frame
 * @param {number} t - Interpolation factor (0-1, where 0=frameA, 1=frameB)
 * @returns {Object} Interpolated manifold frame
 */
export function interpolateManifoldFrames(frameA, frameB, t) {
  // Validate inputs
  if (!frameA || !frameB) {
    throw new Error('Both frameA and frameB are required for interpolation');
  }

  if (t < 0 || t > 1) {
    throw new Error('Interpolation factor t must be between 0 and 1');
  }

  // Interpolate params
  const interpolatedParams = {
    beta: lerp(frameA.params.beta, frameB.params.beta, t),
    adoption_pct: lerp(frameA.params.adoption_pct, frameB.params.adoption_pct, t),
    shock_intensity: lerp(frameA.params.shock_intensity, frameB.params.shock_intensity, t)
  };

  // Interpolate trajectories (arrays of numbers)
  const interpolatedStampedeIndexTrajectory = frameA.stampede_index_trajectory.map(
    (val, index) => lerp(val, frameB.stampede_index_trajectory[index], t)
  );

  const interpolatedAiIndexTrajectory = frameA.ai_index_trajectory.map(
    (val, index) => lerp(val, frameB.ai_index_trajectory[index], t)
  );

  // Interpolate node states
  const interpolatedNodeStates = frameA.node_states.map((nodeA, index) => {
    const nodeB = frameB.node_states[index];
    if (!nodeB) {
      // Fallback if node arrays are different lengths
      return { ...nodeA };
    }

    return {
      id: nodeA.id, // Keep original ID
      capacity_pct: lerp(nodeA.capacity_pct, nodeB.capacity_pct, t),
      is_bottleneck: nodeA.is_bottleneck && nodeB.is_bottleneck, // Conservative: true only if both true
      lane_price_delta: lerp(nodeA.lane_price_delta, nodeB.lane_price_delta, t)
    };
  });

  // Interpolate density field snapshot
  const interpolatedDensityFieldSnapshot = frameA.density_field_snapshot.map(
    (row, rowIndex) => {
      const rowB = frameB.density_field_snapshot[rowIndex];
      if (!rowB) return row;

      return row.map((val, colIndex) => lerp(val, rowB[colIndex], t));
    }
  );

  // For boolean fields, we'll use the value from frameA when t < 0.5, frameB when t >= 0.5
  // This prevents flickering during interpolation
  const interpolatedMetaHerdDetected = t < 0.5 ? frameA.meta_herd_detected : frameB.meta_herd_detected;
  const interpolatedEntropyBudgetActive = t < 0.5 ? frameA.entropy_budget_active : frameB.entropy_budget_active;

  return {
    params: interpolatedParams,
    frame_id: Math.round(lerp(frameA.frame_id, frameB.frame_id, t)), // Average frame ID
    stampede_index_trajectory: interpolatedStampedeIndexTrajectory,
    ai_index_trajectory: interpolatedAiIndexTrajectory,
    node_states: interpolatedNodeStates,
    density_field_snapshot: interpolatedDensityFieldSnapshot,
    meta_herd_detected: interpolatedMetaHerdDetected,
    entropy_budget_active: interpolatedEntropyBudgetActive
  };
}

/**
 * Find two adjacent frames for interpolation based on beta and adoption values
 * This would typically be called by a service that has access to the full manifold dataset
 * @param {Object[]} manifoldDataset - Array of all precomputed manifold frames
 * @param {number} beta - Beta value (0-1)
 * @param {number} adoption - Adoption percentage (0-1)
 * @param {number} shock - Shock intensity (0-1) - fixed for MVP
 * @returns {Object} { frameA, frameB, t } for interpolation
 */
export function findAdjacentFrames(manifoldDataset, beta, adoption, shock = 0.85) {
  if (!manifoldDataset || manifoldDataset.length === 0) {
    return null;
  }

  // For MVP, we'll use a simplified approach:
  // Since we don't have the full dataset in the frontend yet,
  // we'll return the same frame twice with t=0 (no interpolation)
  // In a full implementation, this would search the dataset for the two closest frames

  // Find the closest frame to our parameters
  let closestFrame = manifoldDataset[0];
  let minDistance = Infinity;

  for (const frame of manifoldDataset) {
    const distance = Math.pow(frame.params.beta - beta, 2) +
                    Math.pow(frame.params.adoption_pct - adoption, 2) +
                    Math.pow(frame.params.shock_intensity - shock, 2);

    if (distance < minDistance) {
      minDistance = distance;
      closestFrame = frame;
    }
  }

  // Return the same frame twice for no interpolation (will be improved when we have dataset)
  return {
    frameA: closestFrame,
    frameB: closestFrame,
    t: 0
  };
}

export default {
  interpolateManifoldFrames,
  findAdjacentFrames,
  lerp,
  interpolateValue
};