from __future__ import annotations

"""Societal progression helpers (turn-tick updates).

This module intentionally lives outside `economy.py` to keep economy math pure.
It provides a small, opt-in tick function that updates slow-moving nation
attributes such as `government` and `prosperity` based on `education` and
`unrest`.

API is pure: it returns an updated NationState plus a carryover dict that the
caller can persist to accumulate fractional drift across turns.
"""

from dataclasses import replace
from typing import Dict, Optional, Tuple
import math

from .types import NationState
from .config import education_effectiveness


# Tunable drift constants (very conservative by default)
GOV_EDU_BONUS_PER_LEVEL = 0.01      # per edu level, scaled by edu effectiveness
GOV_UNREST_PENALTY_PER_POINT = 0.02 # per unrest point over baseline

PROS_EDU_BONUS_PER_LEVEL = 0.05     # per edu level, scaled by edu effectiveness
PROS_UNREST_PENALTY_PER_POINT = 0.03

GOV_BOUNDS = (0, 4)
PROS_BOUNDS = (0, 9)


def _extract_int_change(total: float) -> Tuple[int, float]:
    """Split a running float into an integer step and fractional remainder."""
    if total >= 1.0:
        step = math.floor(total)
        return step, total - step
    if total <= -1.0:
        step = math.ceil(total)
        return step, total - step
    return 0, total


def tick_nation_society(
    n: NationState,
    carry: Optional[Dict[str, float]] = None,
) -> Tuple[NationState, Dict[str, float]]:
    """Advance slow-moving societal stats by one tick.

    - High unrest slowly lowers `government`.
    - Higher education very slowly raises `government`.
    - Higher education slowly raises `prosperity`.
    - Unrest reduces the effectiveness of education and directly penalizes prosperity.

    Returns a tuple of (updated_nation, carryover) where `carryover` should be
    persisted by the caller to accumulate fractional drift.
    Keys in `carryover`: `govFrac`, `prosFrac`.
    """

    # Inputs (clamped at expected ranges)
    edu_level = max(0, min(9, getattr(n, "education", 0)))
    unrest = max(0, n.unrest)
    edu_eff = education_effectiveness(unrest)

    # Compute raw float deltas for this tick
    unrest_over_baseline = max(0.0, float(unrest) - 1.0)
    d_gov = edu_level * GOV_EDU_BONUS_PER_LEVEL * edu_eff - unrest_over_baseline * GOV_UNREST_PENALTY_PER_POINT
    d_pros = edu_level * PROS_EDU_BONUS_PER_LEVEL * edu_eff - float(unrest) * PROS_UNREST_PENALTY_PER_POINT

    # Merge with carryover fractional progress
    carry_in: Dict[str, float] = carry or {}
    gov_total = carry_in.get("govFrac", 0.0) + d_gov
    pros_total = carry_in.get("prosFrac", 0.0) + d_pros

    gov_step, gov_rem = _extract_int_change(gov_total)
    pros_step, pros_rem = _extract_int_change(pros_total)

    # Apply bounded integer steps
    new_government = max(GOV_BOUNDS[0], min(GOV_BOUNDS[1], n.government + gov_step))
    new_prosperity = max(PROS_BOUNDS[0], min(PROS_BOUNDS[1], n.prosperity + pros_step))

    updated = replace(n, government=new_government, prosperity=new_prosperity)
    carry_out = {"govFrac": gov_rem, "prosFrac": pros_rem}
    return updated, carry_out


