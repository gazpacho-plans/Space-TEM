// economy.ts
// Space TEM — Economy v0.6 (Capacity → Distribution)
// - Nation has a total capacity (the pie).
// - CPs slice the pie; owners take their share.
// - Boost (🚀) is gated by launch capability: no facility, no Boost output.
//
// Imports: rules (seed + stat multipliers) and Nation types.

import { CAPACITY_SEED_BY_PROFILE, PROSPERITY_MULT, UNREST_MULT } from "./rules";
import type { NationState, ModifierState } from "./nation_schema";

// ———————————————————————————————————————————————————————————————————————
// Types
// ———————————————————————————————————————————————————————————————————————

export type Yields = { money: number; influence: number; ops: number; boost: number };

// Handy UI helpers if you want them:
export type IncomeExplanation = {
  profile: string;
  seed: Yields;
  prosperityMult: number;
  unrestMult: number;
  capacityMods: string[];         // IDs of capacity-stage mods
  capacityBeforeBoostGate: Yields;
  capacityAfterBoostGate: Yields; // boost set to 0 if no launch
  perCPSlice: Yields;
  cpCount: number;
  yourCPs: number;
  ownerMods: string[];            // IDs of owner-share mods that applied
  postGrants: Yields;             // flat additions (e.g., exec +1 boost)
  final: Yields;
};

// ———————————————————————————————————————————————————————————————————————
// Public API
// ———————————————————————————————————————————————————————————————————————

/** Nation-wide output before splitting across CPs. */
export function computeNationCapacity(n: NationState): Yields {
  const seed = CAPACITY_SEED_BY_PROFILE[n.economyProfile];
  const p = PROSPERITY_MULT[n.prosperity];
  const u = UNREST_MULT(n.unrest);

  const capMods = n.modifiers.filter(m => m.stage === "capacity");
  const capMult = combineYieldMults(capMods);

  // seed × prosperity × unrest × nation mods
  const capacity = mulYields(multAll(seed, p * u), capMult);

  // BOOST GATE: if the nation lacks launch capability, capacity boost is zero.
  if (!hasLaunchCapability(n)) capacity.boost = 0;

  return capacity;
}

/** Capacity divided equally among the nation’s CPs. */
export function perCPSlice(n: NationState): Yields {
  const cap = computeNationCapacity(n);
  const cpCount = Math.max(1, n.cp.length); // safety; micro nations still have 1
  return scaleYields(cap, 1 / cpCount);
}

/** Final weekly income for a faction from a single nation. */
export function computeFactionIncomeInNation(n: NationState, factionId: string): Yields {
  const slice = perCPSlice(n);
  const owned = n.cp.filter(c => c.owner === factionId).length;

  // Owner-share mods (typically from orgs), scoped to this faction when present.
  const ownerMods = n.modifiers.filter(
    m => m.stage === "owner_share" && (!m.appliesToFactionId || m.appliesToFactionId === factionId)
  );
  const ownerMult = combineYieldMults(ownerMods);

  // Base share (per-CP × number of CPs you own) with your multipliers.
  const base = scaleYields(slice, owned);
  const withOwner = mulYields(base, ownerMult);

  // Post-stage flat grants (e.g., Exec +1 Boost if the nation can launch).
  const post = computePostGrants(n, factionId);

  return addYields(withOwner, post);
}

/** Human-readable breakdown for UI/telemetry. */
export function explainIncome(n: NationState, factionId: string): IncomeExplanation {
  const seed = CAPACITY_SEED_BY_PROFILE[n.economyProfile];
  const prosperityMult = PROSPERITY_MULT[n.prosperity];
  const unrestMult = UNREST_MULT(n.unrest);

  const capModsArr = n.modifiers.filter(m => m.stage === "capacity");
  const capacityMods = capModsArr.map(m => m.id);

  const beforeGate = mulYields(multAll(seed, prosperityMult * unrestMult), combineYieldMults(capModsArr));
  const afterGate = { ...beforeGate, boost: hasLaunchCapability(n) ? beforeGate.boost : 0 };

  const cpCount = Math.max(1, n.cp.length);
  const perCPSliceVal = scaleYields(afterGate, 1 / cpCount);

  const yourCPs = n.cp.filter(c => c.owner === factionId).length;

  const ownerModsArr = n.modifiers.filter(
    m => m.stage === "owner_share" && (!m.appliesToFactionId || m.appliesToFactionId === factionId)
  );
  const ownerMods = ownerModsArr.map(m => m.id);

  const base = scaleYields(perCPSliceVal, yourCPs);
  const withOwner = mulYields(base, combineYieldMults(ownerModsArr));

  const postGrants = computePostGrants(n, factionId);
  const final = addYields(withOwner, postGrants);

  return {
    profile: n.economyProfile,
    seed,
    prosperityMult,
    unrestMult,
    capacityMods,
    capacityBeforeBoostGate: roundYields(beforeGate, 3),
    capacityAfterBoostGate: roundYields(afterGate, 3),
    perCPSlice: roundYields(perCPSliceVal, 3),
    cpCount,
    yourCPs,
    ownerMods,
    postGrants: roundYields(postGrants, 3),
    final: roundYields(final, 3),
  };
}

// Convenience if you want a whole-nation map keyed by faction:
export function computeAllFactionIncomeInNation(n: NationState, factionIds: string[]): Record<string, Yields> {
  const out: Record<string, Yields> = {};
  for (const f of factionIds) out[f] = computeFactionIncomeInNation(n, f);
  return out;
}

// ———————————————————————————————————————————————————————————————————————
// Rules (grant logic & capability checks)
// ———————————————————————————————————————————————————————————————————————

export const BOOST_FLAG = "launch_capability";

export function hasLaunchCapability(n: NationState): boolean {
  return n.flags.has(BOOST_FLAG);
}

/** Flat “post” grants after shares. Extend as needed. */
export function computePostGrants(n: NationState, factionId: string): Yields {
  let flat: Yields = ZERO_YIELDS();

  // Example: Exec holder gets +1 Boost/week IF the nation can launch.
  if (hasLaunchCapability(n) && holdsExecutive(n, factionId)) {
    flat = addYields(flat, { money: 0, influence: 0, ops: 0, boost: 1 });
  }

  // If you later add post-stage catalog items that are flat (e.g., events),
  // fetch and add them here.

  return flat;
}

export function holdsExecutive(n: NationState, factionId: string): boolean {
  const exec = n.cp[n.cp.length - 1];
  return !!exec && exec.kind === "executive" && exec.owner === factionId;
}

// ———————————————————————————————————————————————————————————————————————
// Math helpers
// ———————————————————————————————————————————————————————————————————————

const ZERO_YIELDS = (): Yields => ({ money: 0, influence: 0, ops: 0, boost: 0 });
const ONE_YIELDS = (): Yields => ({ money: 1, influence: 1, ops: 1, boost: 1 });

export function addYields(a: Yields, b: Yields): Yields {
  return {
    money: a.money + b.money,
    influence: a.influence + b.influence,
    ops: a.ops + b.ops,
    boost: a.boost + b.boost,
  };
}
export function scaleYields(y: Yields, k: number): Yields {
  return { money: y.money * k, influence: y.influence * k, ops: y.ops * k, boost: y.boost * k };
}
export function multAll(y: Yields, k: number): Yields {
  // multiply all four channels by the same scalar (prosperity/unrest)
  return scaleYields(y, k);
}
export function mulYields(y: Yields, mult: Yields): Yields {
  return {
    money: y.money * mult.money,
    influence: y.influence * mult.influence,
    ops: y.ops * mult.ops,
    boost: y.boost * mult.boost,
  };
}

/** Collapse a set of yield_mult modifiers into a single multiplicative vector. */
export function combineYieldMults(mods: ModifierState[]): Yields {
  let m = ONE_YIELDS();
  for (const mod of mods) {
    if (mod.effect?.kind !== "yield_mult") continue;
    m = {
      money: m.money * (mod.effect.money ?? 1),
      influence: m.influence * (mod.effect.influence ?? 1),
      ops: m.ops * (mod.effect.ops ?? 1),
      boost: m.boost * (mod.effect.boost ?? 1),
    };
  }
  return m;
}

export function roundYields(y: Yields, digits = 2): Yields {
  const p = 10 ** digits;
  return {
    money: Math.round(y.money * p) / p,
    influence: Math.round(y.influence * p) / p,
    ops: Math.round(y.ops * p) / p,
    boost: Math.round(y.boost * p) / p,
  };
}
