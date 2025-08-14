from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List, TypedDict

from .config import (
    CAPACITY_SEED_BY_PROFILE,
    PROSPERITY_MULT,
    unrest_multiplier,
    BOOST_FLAG,
)
from .types import NationState, ModifierState, Yields


class IncomeExplanation(TypedDict):
    profile: str
    seed: Dict[str, float]
    prosperityMult: float
    unrestMult: float
    capacityMods: List[str]
    capacityBeforeBoostGate: Dict[str, float]
    capacityAfterBoostGate: Dict[str, float]
    perCPSlice: Dict[str, float]
    cpCount: int
    yourCPs: int
    ownerMods: List[str]
    postGrants: Dict[str, float]
    final: Dict[str, float]


# ———————————————————————————————————————————————————————————————————————
# Public API
# ———————————————————————————————————————————————————————————————————————


def compute_nation_capacity(n: NationState) -> Yields:
    """Nation-wide output before splitting across CPs.

    seed × prosperity × unrest × nation capacity-stage modifiers.
    Boost is gated to 0 if the nation lacks launch capability.
    """
    seed = CAPACITY_SEED_BY_PROFILE[n.economyProfile]
    prosperity_mult = PROSPERITY_MULT[n.prosperity]
    unrest_mult = unrest_multiplier(n.unrest)

    cap_mods = [m for m in n.modifiers if m.stage == "capacity"]
    cap_mult = combine_yield_mults(cap_mods)

    capacity = mul_yields(mult_all(Yields(seed.money, seed.influence, seed.ops, seed.boost), prosperity_mult * unrest_mult), cap_mult)

    if not has_launch_capability(n):
        capacity.boost = 0

    return capacity


def per_cp_slice(n: NationState) -> Yields:
    cap = compute_nation_capacity(n)
    cp_count = max(1, len(n.cp))
    return scale_yields(cap, 1 / cp_count)


def compute_faction_income_in_nation(n: NationState, faction_id: str) -> Yields:
    slice_ = per_cp_slice(n)
    owned = sum(1 for c in n.cp if c.owner == faction_id)

    owner_mods = [
        m for m in n.modifiers if m.stage == "owner_share" and (not m.appliesToFactionId or m.appliesToFactionId == faction_id)
    ]
    owner_mult = combine_yield_mults(owner_mods)

    base = scale_yields(slice_, owned)
    with_owner = mul_yields(base, owner_mult)

    post = compute_post_grants(n, faction_id)
    return add_yields(with_owner, post)


def explain_income(n: NationState, faction_id: str) -> IncomeExplanation:
    seed = CAPACITY_SEED_BY_PROFILE[n.economyProfile]
    prosperity_mult = PROSPERITY_MULT[n.prosperity]
    u_mult = unrest_multiplier(n.unrest)

    cap_mods_arr = [m for m in n.modifiers if m.stage == "capacity"]
    capacity_mods = [m.id for m in cap_mods_arr]

    before_gate = mul_yields(mult_all(Yields(seed.money, seed.influence, seed.ops, seed.boost), prosperity_mult * u_mult), combine_yield_mults(cap_mods_arr))
    after_gate = Yields(before_gate.money, before_gate.influence, before_gate.ops, before_gate.boost if has_launch_capability(n) else 0)

    cp_count = max(1, len(n.cp))
    per_cp_slice_val = scale_yields(after_gate, 1 / cp_count)

    your_cps = sum(1 for c in n.cp if c.owner == faction_id)

    owner_mods_arr = [
        m for m in n.modifiers if m.stage == "owner_share" and (not m.appliesToFactionId or m.appliesToFactionId == faction_id)
    ]
    owner_mods = [m.id for m in owner_mods_arr]

    base = scale_yields(per_cp_slice_val, your_cps)
    with_owner = mul_yields(base, combine_yield_mults(owner_mods_arr))

    post_grants = compute_post_grants(n, faction_id)
    final = add_yields(with_owner, post_grants)

    return {
        "profile": n.economyProfile,
        "seed": asdict(Yields(seed.money, seed.influence, seed.ops, seed.boost)),
        "prosperityMult": prosperity_mult,
        "unrestMult": u_mult,
        "capacityMods": capacity_mods,
        "capacityBeforeBoostGate": asdict(round_yields(before_gate, 3)),
        "capacityAfterBoostGate": asdict(round_yields(after_gate, 3)),
        "perCPSlice": asdict(round_yields(per_cp_slice_val, 3)),
        "cpCount": cp_count,
        "yourCPs": your_cps,
        "ownerMods": owner_mods,
        "postGrants": asdict(round_yields(post_grants, 3)),
        "final": asdict(round_yields(final, 3)),
    }


def compute_all_faction_income_in_nation(n: NationState, faction_ids: List[str]) -> Dict[str, Yields]:
    return {f: compute_faction_income_in_nation(n, f) for f in faction_ids}


# ———————————————————————————————————————————————————————————————————————
# Rules (grant logic & capability checks)
# ———————————————————————————————————————————————————————————————————————


def has_launch_capability(n: NationState) -> bool:
    return BOOST_FLAG in n.flags


def compute_post_grants(n: NationState, faction_id: str) -> Yields:
    flat = zero_yields()

    if has_launch_capability(n) and holds_executive(n, faction_id):
        flat = add_yields(flat, Yields(money=0, influence=0, ops=0, boost=1))

    return flat


def holds_executive(n: NationState, faction_id: str) -> bool:
    exec_cp = n.cp[-1] if n.cp else None
    return bool(exec_cp and exec_cp.kind == "executive" and exec_cp.owner == faction_id)


# ———————————————————————————————————————————————————————————————————————
# Math helpers
# ———————————————————————————————————————————————————————————————————————


def zero_yields() -> Yields:
    return Yields(money=0, influence=0, ops=0, boost=0)


def one_yields() -> Yields:
    return Yields(money=1, influence=1, ops=1, boost=1)


def add_yields(a: Yields, b: Yields) -> Yields:
    return Yields(
        money=a.money + b.money,
        influence=a.influence + b.influence,
        ops=a.ops + b.ops,
        boost=a.boost + b.boost,
    )


def scale_yields(y: Yields, k: float) -> Yields:
    return Yields(money=y.money * k, influence=y.influence * k, ops=y.ops * k, boost=y.boost * k)


def mult_all(y: Yields, k: float) -> Yields:
    return scale_yields(y, k)


def mul_yields(y: Yields, mult: Yields) -> Yields:
    return Yields(
        money=y.money * mult.money,
        influence=y.influence * mult.influence,
        ops=y.ops * mult.ops,
        boost=y.boost * mult.boost,
    )


def combine_yield_mults(mods: List[ModifierState]) -> Yields:
    m = one_yields()
    for mod in mods:
        if not mod.effect or mod.effect.kind != "yield_mult":
            continue
        m = Yields(
            money=m.money * (mod.effect.money if mod.effect.money is not None else 1),
            influence=m.influence * (mod.effect.influence if mod.effect.influence is not None else 1),
            ops=m.ops * (mod.effect.ops if mod.effect.ops is not None else 1),
            boost=m.boost * (mod.effect.boost if mod.effect.boost is not None else 1),
        )
    return m


def round_yields(y: Yields, digits: int = 2) -> Yields:
    p = 10 ** digits
    return Yields(
        money=round(y.money * p) / p,
        influence=round(y.influence * p) / p,
        ops=round(y.ops * p) / p,
        boost=round(y.boost * p) / p,
    )


