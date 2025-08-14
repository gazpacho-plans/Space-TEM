"""Centralized constants for Nations/Economy (Python port).

Mirrors the semantics of the TypeScript version in `nations/config.ts`.
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


# Multipliers by prosperity (1–5)
PROSPERITY_MULT: Dict[int, float] = {1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2}


def unrest_multiplier(unrest: int) -> float:
    """Unrest multiplier, clamped at 0.6 so late-game chaos doesn’t nuke economies."""
    return max(0.6, 1 - 0.1 * float(unrest))


# Flags
BOOST_FLAG = "launch_capability"


# Policy thresholds
EXECUTIVE_PO_THRESHOLD = 60
