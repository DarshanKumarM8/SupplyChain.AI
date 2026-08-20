"""
Option Escrow — Capacity Call Option Mock
============================================

Mock smart-contract escrow for capacity call options.
Firms pre-negotiate bilateral options on lane capacity at a strike price.
On exercise, capacity is reserved without spot market impact.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CapacityOption:
    option_id: str
    holder_firm_id: str
    lane_id: str
    capacity_units: int
    strike_price: float  # $/unit
    expiry: str          # ISO datetime
    is_exercised: bool = False
    exercised_at: Optional[str] = None


class OptionEscrow:
    """Mock escrow for capacity call options."""

    def __init__(self):
        self._options: dict[str, CapacityOption] = {}

    def create_option(self, firm_id: str, lane_id: str, units: int, strike: float, expiry: str) -> CapacityOption:
        """Create a new capacity call option held in escrow."""
        oid = f"opt_{firm_id}_{lane_id}_{len(self._options)}"
        option = CapacityOption(
            option_id=oid,
            holder_firm_id=firm_id,
            lane_id=lane_id,
            capacity_units=units,
            strike_price=strike,
            expiry=expiry,
        )
        self._options[oid] = option
        return option

    def exercise_option(self, option_id: str) -> dict:
        """Exercise a capacity option — deducts from lane capacity without spot impact."""
        option = self._options.get(option_id)
        if not option:
            return {"error": "Option not found"}
        if option.is_exercised:
            return {"error": "Option already exercised"}

        option.is_exercised = True
        option.exercised_at = datetime.utcnow().isoformat()

        return {
            "status": "exercised",
            "option_id": option_id,
            "lane_id": option.lane_id,
            "capacity_reserved": option.capacity_units,
            "cost_per_unit": option.strike_price,
            "spot_impact": 0.0,  # No spot market signal
        }

    def list_options(self, firm_id: Optional[str] = None) -> list[dict]:
        """List all options, optionally filtered by firm."""
        options = self._options.values()
        if firm_id:
            options = [o for o in options if o.holder_firm_id == firm_id]
        return [
            {
                "option_id": o.option_id,
                "lane_id": o.lane_id,
                "capacity_units": o.capacity_units,
                "strike_price": o.strike_price,
                "is_exercised": o.is_exercised,
            }
            for o in options
        ]
