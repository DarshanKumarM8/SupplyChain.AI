# Person 3: Frontend Engineer - Implementation Plan

Based on the SupplyChainAI Master Implementation Plan (V3) and your current progress, here is your step-by-step implementation plan.

## Current Status ✅
**Phase 1 (Hours 0-8): UI Scaffold & Design System - COMPLETED**
- Vite + React project initialized
- Global CSS design system created
- Component files stubbed/created
- Mock manifold data created
- Hooks and services structure planned

## Next Phase: 🚀 Phase 1.5 (Hours 8-16): Manifold Interpolation - CRITICAL PATH

This phase focuses on connecting the frontend to the backend manifold data and enabling smooth interpolation for real-time visualization.

### Step-by-Step Tasks:

#### 3.9: Build WebSocket Connection Hook
**File:** `src/hooks/useWebSocket.js`
- Connect to backend WebSocket endpoint: `ws://localhost:8000/ws/simulation`
- Handle connection, reconnection, and error handling
- Parse incoming JSON frames (stampede_index.json format)
- Provide cleanup on unmount
- Export hook that returns latest frame and connection status

#### 3.10: Build Manifold Frame Interpolator
**File:** `src/services/manifoldInterpolator.js`
- Given two adjacent precomputed frames, linearly interpolate:
  - Node states (capacity_pct, is_bottleneck, lane_price_delta)
  - Index values (stampede_index_trajectory, ai_index_trajectory)
  - Density fields (density_field_snapshot)
- Implement smooth 60fps interpolation for animation
- Handle edge cases (same frame, missing frames)
- Export interpolation function

#### 3.11: Build useManifold Hook
**File:** `src/hooks/useManifold.js`
- Manages slider state (beta, adoption) from PanicSlider and AdoptionSlider
- Fetches manifold frame from backend via REST API: `GET /api/manifold/frame?beta={beta}&adoption={adoption}&shock={shock}`
- Feeds fetched frame to manifold interpolator
- Outputs smooth animation state for components
- Handles loading states and errors
- Memoizes expensive operations

#### 3.12: Wire Sliders to Manifold Lookups
**File:** `src/App.jsx` (modify existing)
- Connect PanicSlider (β) and AdoptionSlider (%) to trigger manifold frame fetch
- Verify <16ms render latency for smooth UI
- Implement shock intensity as fixed value (0.85) for MVP or make configurable
- Ensure both sliders trigger manifold lookup when changed
- Pass interpolated manifold data to visualization components

## Immediate Action Items:

1. **Create missing directories:**
   ```bash
   mkdir -p frontend/src/hooks
   mkdir -p frontend/src/services
   mkdir -p frontend/src/data
   mkdir -p frontend/src/components/NetworkGraph
   ```

2. **Start with WebSocket hook:** Create `src/hooks/useWebSocket.js`

3. **Then create interpolator:** Create `src/services/manifoldInterpolator.js`

4. **Build useManifold hook:** Create `src/hooks/useManifold.js`

5. **Update App.jsx:** Wire sliders to trigger manifold lookups

## Reference Files to Consult:
- `shared/api_schemas/manifold_frame.json` - Understand the data structure
- `shared/constants.py` - Mirror these values in frontend constants
- Implementation Plan Section 4.3 (Person 3 steps) for detailed specifications

## Success Criteria for This Phase:
- [ ] WebSocket connection successfully established and receiving frames
- [ ] Manifold interpolator correctly interpolates between two frames
- [ ] useManifold hook responds to slider changes with <100ms latency
- [ ] Sliders trigger manifold lookups and update UI smoothly
- [ ] No React hooks rules violations
- [ ] Proper error handling and loading states

## After This Phase:
Once Phase 1.5 is complete, you'll move to:
**Phase 2 (Hours 16-28): Cytoscape Network Visualization**
- Build Cytoscape canvas component
- Build density field overlay
- Build shock line indicator
- Implement split-screen layout
- Implement click-to-act on graph nodes

## Notes:
- Remember to keep changes conflict-free by only working in `frontend/` directory
- Shared contracts in `shared/` are frozen after Phase 1 - do not modify schemas
- Use the mock data in `src/data/mockManifold.json` for offline development
- Test WebSocket connection to `http://localhost:8000` once backend is running