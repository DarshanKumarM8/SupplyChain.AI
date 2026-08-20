"""
Option Escrow — Capacity Call Option Mock
============================================

Mock smart-contract escrow for capacity call options.
Firms pre-negotiate bilateral options on lane capacity at a strike price.
On exercise, capacity is reserved without spot market price impact.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ── Spec-compliant option record ──────────────────────────────────────────────

@dataclass
class Option:
    """
    Represents a capacity call option held in escrow.

    Fields match the contract schema exactly:
        option_id     — Unique option identifier.
        holder        — ID of the firm holding this option.
        strike_price  — Pre-agreed $/unit price (no spot impact on exercise).
        expiry_tick   — Simulation tick after which the option lapses.
        lane_id       — Freight lane the option covers.
        units         — Capacity units reserved by this option.
        is_exercised  — Whether the option has already been exercised.
    """
    option_id: str
    holder: str
    strike_price: float
    expiry_tick: int
    lane_id: str
    units: int = 0
    is_exercised: bool = False


# ── Legacy dataclass (preserved for backwards compatibility) ──────────────────

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


# ── OptionEscrow class ────────────────────────────────────────────────────────

class OptionEscrow:
    """
    Mock smart-contract escrow for capacity call options.

    Internally tracks two independent registries:
    - ``_options``  — spec-compliant Option records (tick-based expiry)
    - ``_legacy``   — CapacityOption records (ISO-datetime expiry)

    The primary interface is:
        ``register_option()`` / ``exercise_option()`` using tick-based Options.
    The legacy ``create_option()`` / ``list_options()`` helpers are retained.
    """

    def __init__(self) -> None:
        self._options: dict[str, Option] = {}
        # Legacy registry kept for backwards compatibility
        self._legacy: dict[str, CapacityOption] = {}

    # ── Primary (spec) interface ──────────────────────────────────────────────

    def register_option(
        self,
        option_id: str,
        holder: str,
        strike_price: float,
        expiry_tick: int,
        lane_id: str,
        units: int = 0,
    ) -> Option:
        """
        Register a new capacity call option in escrow.

        Args:
            option_id:    Unique identifier for this option.
            holder:       ID of the firm holding the option.
            strike_price: Pre-agreed $/unit price.
            expiry_tick:  Last simulation tick on which exercise is valid.
            lane_id:      Freight lane the option covers.
            units:        Capacity units reserved.

        Returns:
            The newly created ``Option`` record.
        """
        opt = Option(
            option_id=option_id,
            holder=holder,
            strike_price=strike_price,
            expiry_tick=expiry_tick,
            lane_id=lane_id,
            units=units,
        )
        self._options[option_id] = opt
        return opt

    def exercise_option(
        self,
        option_id: str,
        current_tick: int,
        available_capacity: dict,
    ) -> tuple[bool, dict]:
        """
        Attempt to exercise a capacity option.

        Validates:
          1. The option exists.
          2. It has not already been exercised.
          3. ``current_tick <= expiry_tick`` (option has not lapsed).

        On success, deducts the option's ``units`` from
        ``available_capacity[lane_id]`` with **no spot market price impact**
        (the whole point of pre-negotiated options).

        Args:
            option_id:          Option to exercise.
            current_tick:       Current simulation tick.
            available_capacity: Mutable dict mapping lane_id → available units.

        Returns:
            A tuple of ``(success: bool, updated_capacity: dict)``.
            On failure ``updated_capacity`` is returned unchanged so the
            caller can inspect the original state.
        """
        opt = self._options.get(option_id)

        if opt is None:
            return False, available_capacity

        if opt.is_exercised:
            return False, available_capacity

        if current_tick > opt.expiry_tick:
            # Option has lapsed — do not modify capacity
            return False, available_capacity

        # ── Exercise: deduct capacity, no spot market signal ──────────────────
        updated = dict(available_capacity)  # shallow copy so caller dict is unaffected
        current = updated.get(opt.lane_id, 0)
        updated[opt.lane_id] = max(0, current - opt.units)

        opt.is_exercised = True

        return True, updated

    def get_option(self, option_id: str) -> Optional[Option]:
        """Return the Option record for *option_id*, or None if not found."""
        return self._options.get(option_id)

    # ── Legacy interface (backwards compatibility) ────────────────────────────

    def create_option(
        self,
        firm_id: str,
        lane_id: str,
        units: int,
        strike: float,
        expiry: str,
    ) -> CapacityOption:
        """Create a new capacity call option held in escrow (legacy API)."""
        oid = f"opt_{firm_id}_{lane_id}_{len(self._legacy)}"
        option = CapacityOption(
            option_id=oid,
            holder_firm_id=firm_id,
            lane_id=lane_id,
            capacity_units=units,
            strike_price=strike,
            expiry=expiry,
        )
        self._legacy[oid] = option
        return option

    def list_options(self, firm_id: Optional[str] = None) -> list[dict]:
        """List all legacy options, optionally filtered by firm."""
        options = self._legacy.values()
        if firm_id:
            options = [o for o in options if o.holder_firm_id == firm_id]  # type: ignore[assignment]
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


# ── Module-level singleton ─────────────────────────────────────────────────────
option_escrow = OptionEscrow()
