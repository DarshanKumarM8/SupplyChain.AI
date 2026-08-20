"""
Sentinel Agent — NLP Event Extraction with Self-Influence Decorrelation
========================================================================

Responsibilities:
- Extract disruption events from GDELT/mock data feeds
- Corroborate signals across multiple sources
- Apply self-influence decorrelation: down-weight any market signals
  causally linked to SupplyChainAI's own prior interventions
- Output: DisruptionEvent schema (see shared/api_schemas/disruption_event.json)

Key Formula:
  Self-influence filter: if signal S_j was preceded by SupplyChainAI action A_i
  within causal window τ, weight w_j is reduced by factor (1 - correlation(A_i, S_j))
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
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

    def __init__(self, causal_window_seconds: int = 3600):
        self.causal_window = causal_window_seconds
        self.prior_actions: list[dict] = []  # Track SupplyChainAI's own actions
        self.signal_buffer: list[dict] = []

    def ingest_signal(self, signal: dict) -> None:
        """Ingest a raw market/event signal into the buffer."""
        # TODO: Implement signal ingestion from GDELT mock feed
        self.signal_buffer.append(signal)

    def register_own_action(self, action: dict) -> None:
        """Register a SupplyChainAI-generated action for decorrelation tracking."""
        self.prior_actions.append({
            **action,
            "registered_at": datetime.utcnow().isoformat()
        })

    def _is_self_influenced(self, signal: dict) -> bool:
        """
        Check if a signal was causally induced by a prior SupplyChainAI action.
        Uses temporal proximity + affected node overlap as causal proxy.
        """
        # TODO: Implement causal correlation check
        # For each prior action within causal_window:
        #   if affected_nodes overlap AND signal timestamp > action timestamp:
        #     compute correlation(action, signal)
        #     return True if correlation > threshold
        return False

    def _corroborate_signals(self, signals: list[dict]) -> tuple[float, int]:
        """
        Cross-reference signals to compute corroboration confidence.
        Returns (confidence_score, latency_ms).
        """
        # TODO: Implement multi-source corroboration
        # Simple approach: confidence = count(unique_sources) / total_source_types
        if not signals:
            return 0.0, 0
        return 0.91, 400  # Placeholder

    def detect_disruption(self, raw_signals: list[dict]) -> Optional[DisruptionEvent]:
        """
        Main entry point: process raw signals → corroborate → filter self-influence → emit event.
        """
        # TODO: Implement full pipeline
        # 1. Buffer incoming signals
        # 2. Filter self-influenced signals
        # 3. Corroborate remaining signals
        # 4. If confidence > threshold, emit DisruptionEvent
        raise NotImplementedError("Sentinel detection pipeline not yet implemented")

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
