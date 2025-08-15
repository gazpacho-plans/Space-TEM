"""Centralized constants for Nations/Economy (Python port).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class YieldsSeed:
    money: float
    influence: float
    ops: float
    boost: float


# Control Points per nation tier
CP_BY_TIER: Dict[str, int] = {
    "major": 6,
    "regional": 4,
    "minor": 2,
    "micro": 1,
}


# Economy capacity seeds by profile
CAPACITY_SEED_BY_PROFILE: Dict[str, YieldsSeed] = {
    "industrial": YieldsSeed(money=16, influence=4, ops=4, boost=0.6),
    "services": YieldsSeed(money=18, influence=5, ops=3, boost=0.3),
    "research": YieldsSeed(money=12, influence=6, ops=3, boost=0.4),
    "space": YieldsSeed(money=11, influence=3, ops=3, boost=0.9),
}


# Multipliers by prosperity (0–9) 0 represents economic collapse; 9 represents highly prosperous.
PROSPERITY_MULT: Dict[int, float] = {
    0: 0.6,
    1: 0.7,
    2: 0.8,
    3: 0.9,
    4: 1.0,
    5: 1.05,
    6: 1.1,
    7: 1.15,
    8: 1.2,
    9: 1.25,
}


def unrest_multiplier(unrest: int) -> float:
    """Unrest multiplier, clamped at 0.6 so late-game chaos doesn’t nuke economies."""
    return max(0.6, 1 - 0.1 * float(unrest))


# Education impact constants
# Education primarily drives influence and ops (research/admin capacity).
# It has mild impact on money and almost none on boost directly.
# Strong unrest significantly reduces the effectiveness of education.
EDU_BASE_MULT: Dict[str, float] = {
    "money": 0.01,       # +1% per edu level
    "influence": 0.025,  # +2.5% per edu level
    "ops": 0.03,         # +3% per edu level
    "boost": 0.0,
}

def education_effectiveness(unrest: int) -> float:
    """Returns a dampening factor [0..1] reducing the effect of education with unrest.

    At unrest 0, full effect (1.0). Each point of unrest reduces effectiveness by 7%,
    clamped to a floor of 0.3.
    """
    return max(0.3, 1.0 - 0.07 * float(unrest))


# Research composition weights (derived from nation capacity before CP split)
# Research output is computed as: influence * W_INFLUENCE + ops * W_OPS
RESEARCH_INFLUENCE_WEIGHT: float = 0.5
RESEARCH_OPS_WEIGHT: float = 1.0


# Flags
BOOST_FLAG = "launch_capability"


# Policy thresholds
EXECUTIVE_PO_THRESHOLD = 60
