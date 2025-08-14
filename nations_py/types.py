from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Literal


# Core numeric channels used by the economy
@dataclass
class Yields:
    money: float
    influence: float
    ops: float
    boost: float


@dataclass
class CPState:
    index: int
    kind: Literal["regular", "executive"]
    owner: Optional[str] = None
    defenseBy: Optional[str] = None
    tags: Optional[List[str]] = None


@dataclass
class ModifierEffect:
    kind: Literal["yield_mult"]
    money: Optional[float] = None
    influence: Optional[float] = None
    ops: Optional[float] = None
    boost: Optional[float] = None


@dataclass
class ModifierState:
    id: str
    stage: Literal["capacity", "owner_share", "post"]
    effect: ModifierEffect
    source: Literal["trait", "project", "event", "scenario", "org"]
    appliesToFactionId: Optional[str] = None
    appliedOnTurn: Optional[int] = None
    expiresOnTurn: Optional[int] = None


@dataclass
class NationState:
    id: str
    name: str
    tier: Literal["major", "regional", "minor", "micro"]
    economyProfile: Literal["industrial", "services", "research", "space"]

    cp: List[CPState]
    po: Dict[str, int]
    security: int
    unrest: int
    prosperity: int

    flags: Set[str] = field(default_factory=set)
    modifiers: List[ModifierState] = field(default_factory=list)
