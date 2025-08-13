// nation_schema.ts
// Space TEM — Nations v0.6 (TypeScript-backed data & rules)
//
// Single-source-of-truth:
// - Tier sets CP count (only).
// - Economy seed comes from economyProfile (not tier).
// - Income math lives in economy.ts; this file defines data shapes + compile helpers.
//
// Minimal deps: only needs CP_BY_TIER from rules.ts.
// You can inject a modifier catalog via `resolveModifier` when compiling.

import { CP_BY_TIER } from "./rules";

// ———————————————————————————————————————————————————————————————————————
// Types (Authoring → Runtime)
// ———————————————————————————————————————————————————————————————————————

export type NationTier = "major" | "regional" | "minor" | "micro";
export type EconomyProfile = "industrial" | "services" | "research" | "space";

export type NationAuthoring = {
  id: string;                  // "JPN"
  name: string;                // "Japan"
  tier: NationTier;            // source of CP count (see CP_BY_TIER)
  economyProfile: EconomyProfile; // source of capacity seed (see rules.ts / economy.ts)
  baseSecurity: number;        // used in opposed checks
  startProsperity?: 1 | 2 | 3 | 4 | 5; // default 3
  startUnrest?: 0 | 1 | 2 | 3 | 4 | 5; // default 0
  startPO?: Record<string, number>;    // PO per factionId (0–100)
  startFlags?: string[];               // e.g. ["launch_capability"]
  // Optional: IDs from your central modifier catalog (traits/projects/events/etc.)
  startModifiers?: string[];
};

export type NationState = {
  id: string;
  name: string;
  tier: NationTier;
  economyProfile: EconomyProfile;

  cp: CPState[];                    // generated from tier; last is executive
  po: Record<string, number>;       // live PO per factionId (0–100)
  security: number;                 // live
  unrest: 0 | 1 | 2 | 3 | 4 | 5;    // live
  prosperity: 1 | 2 | 3 | 4 | 5;    // live

  flags: Set<string>;               // e.g. "launch_capability"
  modifiers: ModifierState[];       // normalized, typed effects (can expire)

  // Optional place for nation-specific project states (if you want it here)
  projects?: Record<string, "locked" | "available" | "completed">;
};

export type CPState = {
  index: number;                    // 0..n-1
  kind: "regular" | "executive";    // last slot is always executive
  owner: string | null;             // factionId or null
  defenseBy?: string | null;        // playerId who cast Protect Target (cleared EOT)
  tags?: string[];                  // future hooks (e.g., "capital", "spaceport")
};

export type EffectStage = "capacity" | "owner_share" | "post";

export type YieldMultEffect = {
  kind: "yield_mult";
  money?: number;
  influence?: number;
  ops?: number;
  boost?: number;
};

export type ModifierState = {
  id: string;                       // catalog id
  stage: EffectStage;               // defaulted by resolver (capacity/owner_share/post)
  effect: YieldMultEffect;          // currently only yield_mult; extend later if needed
  source: "trait" | "project" | "event" | "scenario" | "org";
  appliesToFactionId?: string;      // used for owner_share scopes (orgs)
  appliedOnTurn: number;            // when it became active
  expiresOnTurn?: number;           // optional
};

// ———————————————————————————————————————————————————————————————————————
// Compile & helpers
// ———————————————————————————————————————————————————————————————————————

export type CompileOptions = {
  turn?: number;
  // Optional array of initial owners by CP index (length must equal CP count)
  initialOwners?: (string | null)[];
  // Optional function to resolve catalog ids → ModifierState (without id/appliedOnTurn)
  resolveModifier?: (id: string) => Omit<ModifierState, "id" | "appliedOnTurn"> | null;
};

export function compileNation(author: NationAuthoring, opts: CompileOptions = {}): NationState {
  const turn = opts.turn ?? 1;
  const cpCount = CP_BY_TIER[author.tier];
  if (!Number.isFinite(cpCount)) {
    throw new Error(`Unknown tier '${author.tier}' for nation ${author.id}`);
  }

  // Build CP slots (last is executive)
  const cp: CPState[] = Array.from({ length: cpCount }, (_, i) => ({
    index: i,
    kind: i === cpCount - 1 ? "executive" : "regular",
    owner: opts.initialOwners?.[i] ?? null,
  }));

  // Normalize PO (clamp 0–100 & drop negatives/NaN)
  const po: Record<string, number> = {};
  const startPO = author.startPO ?? {};
  for (const [factionId, raw] of Object.entries(startPO)) {
    const v = clamp(Math.round(raw), 0, 100);
    if (v > 0) po[factionId] = v;
  }

  // Flags
  const flags = new Set(author.startFlags ?? []);

  // Resolve modifiers (optional catalog injection)
  const modifiers: ModifierState[] = [];
  const ids = author.startModifiers ?? [];
  for (const id of ids) {
    const base = opts.resolveModifier?.(id);
    if (!base) continue; // silently skip unknown ids; your resolver can throw instead
    modifiers.push({
      id,
      appliedOnTurn: turn,
      ...base,
    });
  }

  const nation: NationState = {
    id: author.id,
    name: author.name,
    tier: author.tier,
    economyProfile: author.economyProfile,

    cp,
    po,
    security: author.baseSecurity,
    unrest: (author.startUnrest ?? 0) as 0 | 1 | 2 | 3 | 4 | 5,
    prosperity: (author.startProsperity ?? 3) as 1 | 2 | 3 | 4 | 5,

    flags,
    modifiers,
  };

  // Invariants for sanity (throws in dev if violated)
  assertNationInvariants(nation);

  return nation;
}

/**
 * Exec gate — computed policy (do not store).
 * Requires: PO ≥ 60 AND majority (floor) of non-exec CPs.
 */
export function canAcquireExecutive(n: NationState, factionId: string): boolean {
  const nonExecOwned = n.cp.filter(c => c.kind === "regular" && c.owner === factionId).length;
  const majorityNeeded = Math.floor((n.cp.length - 1) / 2); // among regular CPs only
  const poOK = (n.po[factionId] ?? 0) >= 60;
  return poOK && nonExecOwned >= majorityNeeded;
}

/**
 * Optional helper for UI: if the exec is locked for a faction, explain why.
 * Returns null if no lock applies.
 */
export function executiveLockReason(n: NationState, factionId: string): string | null {
  const po = n.po[factionId] ?? 0;
  const nonExecOwned = n.cp.filter(c => c.kind === "regular" && c.owner === factionId).length;
  const majorityNeeded = Math.floor((n.cp.length - 1) / 2);

  const reasons: string[] = [];
  if (po < 60) reasons.push(`PO ${po}/60`);
  if (nonExecOwned < majorityNeeded) reasons.push(`need ${majorityNeeded} regular CPs (have ${nonExecOwned})`);
  return reasons.length ? `Executive locked: ${reasons.join("; ")}` : null;
}

// ———————————————————————————————————————————————————————————————————————
// Validation (lightweight guards for bad data during dev)
// ———————————————————————————————————————————————————————————————————————

export function assertNationInvariants(n: NationState): void {
  const expectedCPs = CP_BY_TIER[n.tier];
  if (n.cp.length !== expectedCPs) {
    throw new Error(`[${n.id}] cp.length=${n.cp.length} but tier '${n.tier}' expects ${expectedCPs}`);
  }
  const last = n.cp.at(-1)!;
  if (last.kind !== "executive") {
    throw new Error(`[${n.id}] last CP must be 'executive'`);
  }
  for (const [f, v] of Object.entries(n.po)) {
    if (!Number.isFinite(v) || v < 0 || v > 100) {
      throw new Error(`[${n.id}] PO for faction '${f}' is out of bounds: ${v}`);
    }
  }
  if (!isBounded(n.unrest, 0, 5)) throw new Error(`[${n.id}] unrest out of bounds: ${n.unrest}`);
  if (!isBounded(n.prosperity, 1, 5)) throw new Error(`[${n.id}] prosperity out of bounds: ${n.prosperity}`);
}

// ———————————————————————————————————————————————————————————————————————
// Utils
// ———————————————————————————————————————————————————————————————————————

function clamp(v: number, lo: number, hi: number): number {
  return Math.min(hi, Math.max(lo, v));
}
function isBounded(v: number, lo: number, hi: number): boolean {
  return Number.isFinite(v) && v >= lo && v <= hi;
}

// ———————————————————————————————————————————————————————————————————————
// Example (commented):
// 
// const JPN: NationAuthoring = {
//   id: "JPN",
//   name: "Japan",
//   tier: "major",
//   economyProfile: "industrial",
//   baseSecurity: 6,
//   startProsperity: 4,
//   startUnrest: 1,
//   startPO: { Academy: 72, Servants: 18, Protectorate: 4 },
//   startFlags: ["launch_capability"],
//   startModifiers: ["industrial_policy_money_10"]
// };
// 
// const nation = compileNation(JPN, {
//   turn: 1,
//   initialOwners: [ "Academy", "Academy", null, null, null, null ],
//   resolveModifier: (id) => {
//     switch (id) {
//       case "industrial_policy_money_10":
//         return { stage: "capacity", source: "project", effect: { kind: "yield_mult", money: 1.10 } };
//       default:
//         return null;
//     }
//   }
// });
// 
// // To compute/explain income, call functions from economy.ts:
// //   computeFactionIncomeInNation(nation, "Academy")
// //   explainIncome(nation, "Academy")
// ———————————————————————————————————————————————————————————————————————
