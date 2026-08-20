"""
Sentinel Agent -- NLP Event Extraction with Self-Influence Decorrelation
========================================================================

Responsibilities:
- Extract disruption events from GDELT/mock data feeds
- Corroborate signals across multiple sources
- Apply self-influence decorrelation: down-weight any market signals
  causally linked to SupplyChainAI's own prior interventions
- Output: DisruptionEvent schema (see shared/api_schemas/disruption_event.json)

Key Formula:
  Self-influence filter: if signal S_j was preceded by SupplyChainAI action A_i
  within causal window tau, weight w_j is reduced by factor (1 - correlation(A_i, S_j))
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class DisruptionEvent:
    """Structured disruption event matching the shared API schema."""
    event_id: str
    timestamp: str
    event_type: str  # port_closure, factory_shutdown, lane_congestion, weather_disruption, geopolitical_sanction
    source: str      # GDELT_corroborated, manual_input, sensor_feed
    confidence: float
    corroboration_latency_ms: int
    affected_nodes: list[str]
    self_influence_filtered: bool = False
    raw_signal_count: int = 0
    filtered_signal_count: int = 0


class SentinelAgent:
    """
    Sentinel Agent: monitors for supply chain disruption signals,
    corroborates across sources, and filters self-influenced data.
    """

    CONFIDENCE_THRESHOLD = 0.5
    SELF_INFLUENCE_CORRELATION_THRESHOLD = 0.6

    def __init__(self, causal_window_seconds: int = 3600):
        self.causal_window = causal_window_seconds
        self.prior_actions: list[dict] = []  # Track SupplyChainAI's own actions
        self.signal_buffer: list[dict] = []

    def ingest_signal(self, signal: dict) -> None:
        """Ingest a raw market/event signal into the buffer."""
        if "timestamp" not in signal:
            signal["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.signal_buffer.append(signal)

    def register_own_action(self, action: dict) -> None:
        """Register a SupplyChainAI-generated action for decorrelation tracking."""
        self.prior_actions.append({
            **action,
            "registered_at": datetime.now(timezone.utc).isoformat()
        })

    def _is_self_influenced(self, signal: dict) -> bool:
        """
        Check if a signal was causally induced by a prior SupplyChainAI action.
        Uses temporal proximity + affected node overlap as causal proxy.
        """
        signal_time = signal.get("timestamp", "")
        signal_nodes = set(signal.get("affected_nodes", []))

        if not signal_time or not signal_nodes:
            return False

        try:
            sig_dt = datetime.fromisoformat(signal_time.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return False

        for action in self.prior_actions:
            action_time = action.get("registered_at", "")
            action_nodes = set(action.get("affected_nodes", []))

            if not action_time:
                continue

            try:
                act_dt = datetime.fromisoformat(action_time.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                continue

            # Check temporal proximity: signal must be AFTER action and within causal window
            time_diff = (sig_dt - act_dt).total_seconds()
            if 0 < time_diff < self.causal_window:
                # Check node overlap as causal correlation proxy
                overlap = signal_nodes & action_nodes
                if len(overlap) > 0:
                    # Correlation = proportion of overlapping nodes
                    correlation = len(overlap) / max(len(signal_nodes), 1)
                    if correlation > self.SELF_INFLUENCE_CORRELATION_THRESHOLD:
                        return True

        return False

    def _corroborate_signals(self, signals: list[dict]) -> tuple[float, int]:
        """
        Cross-reference signals to compute corroboration confidence.
        Returns (confidence_score, latency_ms).

        Confidence = unique_sources / total_known_source_types, capped at 1.0
        """
        if not signals:
            return 0.0, 0

        known_source_types = {"GDELT", "Reuters", "MarineTraffic", "NOAA",
                              "sensor_feed", "manual_input", "trade_wire"}
        unique_sources = set()
        for s in signals:
            src = s.get("source", "unknown")
            unique_sources.add(src)

        confidence = min(1.0, len(unique_sources) / max(len(known_source_types) * 0.3, 1))

        # Boost confidence if multiple signals agree on affected nodes
        all_node_sets = [set(s.get("affected_nodes", [])) for s in signals]
        if len(all_node_sets) >= 2:
            common_nodes = all_node_sets[0]
            for ns in all_node_sets[1:]:
                common_nodes = common_nodes & ns
            if len(common_nodes) > 0:
                confidence = min(1.0, confidence + 0.2)

        # Latency: time between first and last signal
        timestamps = []
        for s in signals:
            ts = s.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
                except (ValueError, TypeError):
                    pass

        latency_ms = 0
        if len(timestamps) >= 2:
            latency_ms = int((max(timestamps) - min(timestamps)).total_seconds() * 1000)

        return round(confidence, 2), latency_ms

    def detect_disruption(self, raw_signals: list[dict]) -> Optional[DisruptionEvent]:
        """
        Main entry point: process raw signals -> corroborate -> filter self-influence -> emit event.
        """
        # 1. Buffer incoming signals
        for signal in raw_signals:
            self.ingest_signal(signal)

        raw_count = len(self.signal_buffer)

        # 2. Filter self-influenced signals
        filtered_signals = [
            s for s in self.signal_buffer if not self._is_self_influenced(s)
        ]
        filtered_count = len(filtered_signals)
        was_filtered = filtered_count < raw_count

        # 3. Corroborate remaining signals
        confidence, latency_ms = self._corroborate_signals(filtered_signals)

        # 4. If confidence > threshold, emit DisruptionEvent
        if confidence < self.CONFIDENCE_THRESHOLD:
            self.signal_buffer.clear()
            return None

        # Aggregate affected nodes from all corroborated signals
        all_affected_nodes = set()
        for s in filtered_signals:
            for node in s.get("affected_nodes", []):
                all_affected_nodes.add(node)

        # Determine event type from most common signal type
        event_types = [s.get("event_type", "unknown") for s in filtered_signals]
        event_type = max(set(event_types), key=event_types.count) if event_types else "unknown"

        event = DisruptionEvent(
            event_id=f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            source="GDELT_corroborated" if confidence > 0.7 else "partial_corroboration",
            confidence=confidence,
            corroboration_latency_ms=latency_ms,
            affected_nodes=sorted(list(all_affected_nodes)),
            self_influence_filtered=was_filtered,
            raw_signal_count=raw_count,
            filtered_signal_count=filtered_count,
        )

        # Clear buffer after emitting
        self.signal_buffer.clear()

        return event

    def to_dict(self, event: DisruptionEvent) -> dict:
        """Serialize to API schema format."""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "source": event.source,
            "confidence": event.confidence,
            "corroboration_latency_ms": event.corroboration_latency_ms,
            "affected_nodes": event.affected_nodes,
            "self_influence_filtered": event.self_influence_filtered,
            "raw_signal_count": event.raw_signal_count,
            "filtered_signal_count": event.filtered_signal_count,
        }
