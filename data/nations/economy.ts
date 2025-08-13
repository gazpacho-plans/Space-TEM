// economy.ts
import { CAPACITY_SEED_BY_PROFILE, CP_BY_TIER, PROSPERITY_MULT, UNREST_MULT } from "./rules";

export type Yields = { money: number; influence: number; ops: number; boost: number };

export function computeNationCapacity(n: NationState): Yields {
  const seed = CAPACITY_SEED_BY_PROFILE[n.economyProfile];
  const pMult = PROSPERITY_MULT[n.prosperity];
  const uMult = UNREST_MULT(n.unrest);

  // Stage: capacity (nationwide effects)
  const capMult = n.modifiers
    .filter(m => m.stage === "capacity")
    .reduce((acc, m) => multYields(acc, m.effect), unitYields());

  return mulYields(seed, pMult * uMult, capMult); // seed × prosperity × unrest × nation mods
}

export function perCPSlice(n: NationState): Yields {
  const cap = computeNationCapacity(n);
  const cpCount = n.cp.length;
  return scaleYields(cap, 1 / cpCount);
}

export function computeFactionIncomeInNation(n: NationState, factionId: string): Yields {
  const slice = perCPSlice(n);
  const owned = n.cp.filter(c => c.owner === factionId).length;

  // Owner-share (faction-scoped effects, e.g., orgs)
  const ownerMult = n.modifiers
    .filter(m => m.stage === "owner_share" && (!m.appliesToFactionId || m.appliesToFactionId === factionId))
    .reduce((acc, m) => multYields(acc, m.effect), unitYields());

  const base = scaleYields(slice, owned);
  const withOwner = mulYields(base, 1, ownerMult);

  // Post (flat grants like exec +1 Boost)
  const postFlat = flatPostIncome(n, factionId);
  return addYields(withOwner, postFlat);
}

// helpers…
const unitYields = (): Yields => ({ money:1, influence:1, ops:1, boost:1 });
function multYields(a: Yields, e: Partial<Yields>): Yields {
  return {
    money: a.money * (e.money ?? 1),
    influence: a.influence * (e.influence ?? 1),
    ops: a.ops * (e.ops ?? 1),
    boost: a.boost * (e.boost ?? 1),
  };
}
function mulYields(y: Yields, k: number, m?: Yields): Yields {
  const r = { money: y.money * k, influence: y.influence * k, ops: y.ops * k, boost: y.boost * k };
  return m ? multYields(r, m) : r;
}
function scaleYields(y: Yields, k: number): Yields { return mulYields(y, k); }
function addYields(a: Yields, b: Yields): Yields {
  return { money: a.money + b.money, influence: a.influence + b.influence, ops: a.ops + b.ops, boost: a.boost + b.boost };
}
function flatPostIncome(n: NationState, factionId: string): Yields {
  const holdsExec = n.cp.at(-1)?.owner === factionId;
  return holdsExec && n.flags.has("launch_capability") ? { money:0, influence:0, ops:0, boost:1 } : { money:0, influence:0, ops:0, boost:0 };
}