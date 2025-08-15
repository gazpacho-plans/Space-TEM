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
    EDU_BASE_MULT,
    education_effectiveness,
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
    effective_cp_count,
    compute_faction_income_in_nation,
    compute_all_faction_income_in_nation,
    compute_nation_research_output,
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

from .progression import (
    tick_nation_society,
)

__all__ = [
    # config
    "CP_BY_TIER",
    "CAPACITY_SEED_BY_PROFILE",
    "PROSPERITY_MULT",
    "unrest_multiplier",
    "BOOST_FLAG",
    "EXECUTIVE_PO_THRESHOLD",
    "EDU_BASE_MULT",
    "education_effectiveness",
    # types
    "Yields",
    "CPState",
    "ModifierEffect",
    "ModifierState",
    "NationState",
    # economy
    "compute_nation_capacity",
    "per_cp_slice",
    "effective_cp_count",
    "compute_faction_income_in_nation",
    "compute_all_faction_income_in_nation",
    "compute_nation_research_output",
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
    # progression
    "tick_nation_society",
]


