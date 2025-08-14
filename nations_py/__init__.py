"""Python port of Space-TEM Nations economy utilities.

Exposes:
- config constants (see `nations_py.config`)
- economy functions (see `nations_py.economy`)
- simple dataclasses for types (see `nations_py.types`)
"""

from .config import (
    CP_BY_TIER,
    CAPACITY_SEED_BY_PROFILE,
    PROSPERITY_MULT,
    unrest_multiplier,
    BOOST_FLAG,
    EXECUTIVE_PO_THRESHOLD,
)

from .types import (
    Yields,
    CPState,
    ModifierEffect,
    ModifierState,
    NationState,
)

from .economy import (
    compute_nation_capacity,
    per_cp_slice,
    compute_faction_income_in_nation,
    compute_all_faction_income_in_nation,
    explain_income,
    has_launch_capability,
    compute_post_grants,
    holds_executive,
    add_yields,
    scale_yields,
    mult_all,
    mul_yields,
    combine_yield_mults,
    round_yields,
)

__all__ = [
    # config
    "CP_BY_TIER",
    "CAPACITY_SEED_BY_PROFILE",
    "PROSPERITY_MULT",
    "unrest_multiplier",
    "BOOST_FLAG",
    "EXECUTIVE_PO_THRESHOLD",
    # types
    "Yields",
    "CPState",
    "ModifierEffect",
    "ModifierState",
    "NationState",
    # economy
    "compute_nation_capacity",
    "per_cp_slice",
    "compute_faction_income_in_nation",
    "compute_all_faction_income_in_nation",
    "explain_income",
    "has_launch_capability",
    "compute_post_grants",
    "holds_executive",
    "add_yields",
    "scale_yields",
    "mult_all",
    "mul_yields",
    "combine_yield_mults",
    "round_yields",
]


