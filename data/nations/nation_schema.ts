// Space TEM – Nation Schema Starter (TypeScript)
// Drop this in src/nations.ts (or similar). No external deps required.
// Provides: Authoring schema, Runtime schema, compileNation(), canAcquireExecutive().

/*************************
 * Core types & constants *
 *************************/
export type NationTier = "major" | "regional" | "minor" | "micro";

export type Yields = {
  money: number;
  influence: number;
  ops: number;
  boost: number;
};

export type MissionKey =
  | "public_campaign"
  | "control"
  | "purge"
  | "increase_unrest"
  | "stabilize"
  | "coup";

export const CP_COUNT_BY_TIER: Record<NationTier, number> = {
  major: 6,
  regional: 4,
  minor: 2,
  micro: 1,
};

// Per-CP baseline yields by tier (adjust to balance)
export const DEFAULT_PER_TIER_YIELD: Record<NationTier, Yields> = {
  major: { money: 6, influence: 2, ops: 1, boost: 0.25 },
  regional: { money: 4, influence: 1, ops: 1, boost: 0.15 },
  minor: { money: 2, influence: 1, ops: 0, boost: 0.1 },
  micro: { money: 1, influence: 0, ops: 0, boost: 0.05 },
};

/********************************
 * Authoring (designer-facing)  *
 ********************************/
export type ModifierAuthoring =
  | { kind: "yield_mult"; money?: number; influence?: number; ops?: number; boost?: number }
  | { kind: "mission_dc_delta"; mission: MissionKey; delta: number }
  | { kind: "po_change"; target: "all" | string; amount: number }
  | { kind: "security_delta"; amount: number }
  | { kind: "unrest_delta"; amount: number }
  | { kind: "flag"; name: string };

export type NationAuthoring = {
  id: string;                    // canonical slug, e.g. "JPN"
  name: string;                  // display name
  tier: NationTier;              // single source of truth for CP count
  baseSecurity: number;          // opposed-roll defense
  startProsperity?: number;      // 1–5 (defaults to 3)
  startUnrest?: number;          // 0–5 (defaults to 0)
  startPO?: Record<string, number>; // factionId -> 0..100
  traits?: string[];             // flavor tags
  modifiers?: ModifierAuthoring[]; // optional starting modifiers
  yieldOverridesPerCP?: Partial<Yields>; // e.g., { boost: 0.30 }
  notes?: string;
  // Optional: starting CP owners by index (0..n-1). If omitted, all null.
  startOwners?: (string | null)[];
};

/****************************
 * Runtime (game-facing)     *
 ****************************/
export type CPKind = "regular" | "executive";

export interface CPState {
  index: number;                 // 0..(n-1)
  kind: CPKind;                  // executive is always last
  owner: string | null;          // factionId or null
  defense?: { byPlayerId: string; expiresOnTurn: number };
  tags?: string[];               // e.g., ["capital"]
  locked?: { reason: string };
}

export type ModifierEffect =
  | { kind: "yield_mult"; money?: number; influence?: number; ops?: number; boost?: number }
  | { kind: "mission_dc_delta"; mission: MissionKey; delta: number }
  | { kind: "po_change"; target: "all" | string; amount: number }
  | { kind: "security_delta"; amount: number }
  | { kind: "unrest_delta"; amount: number }
  | { kind: "flag"; name: string; value?: boolean };

export interface ModifierState {
  id: string;                    // unique handle (e.g., "trait:industrial_base")
  source: "trait" | "project" | "event" | "mission" | "scenario";
  effect: ModifierEffect;
  appliedOnTurn: number;
  expiresOnTurn?: number;
}

export interface NationState {
  id: string;
  name: string;
  tier: NationTier;
  cp: CPState[];
  po: Record<string, number>;    // 0..100 per faction
  security: number;               // live
  unrest: number;                 // 0..5
  prosperity: number;             // 1..5
  launchCapability: boolean;      // derived from flags/projects
  projects: Record<string, "locked" | "available" | "completed">;
  modifiers: ModifierState[];     // normalized set
  yieldPerCP: Yields;             // after nation overrides
  prosperityMult: number;         // e.g., 0.8..1.2
  totalYieldEstimate: Yields;     // cp.length * yieldPerCP * prosperityMult * yieldMults
}

/**********************
 * Rules configuration *
 **********************/
export interface RulesConfig {
  perTierYield: Record<NationTier, Yields>;
  prosperityMultiplier: (prosperity: number) => number;
  execGate: {
    // For UI text; logic is in canAcquireExecutive()
    poThreshold: number; // e.g., 60
  };
}

export const DEFAULT_RULES: RulesConfig = {
  perTierYield: DEFAULT_PER_TIER_YIELD,
  prosperityMultiplier: (p: number) => 0.8 + (p - 1) * 0.1, // 1→0.8, 3→1.0, 5→1.2
  execGate: { poThreshold: 60 },
};

/***********************
 * Helper calculations  *
 ***********************/
export function cpCountForTier(tier: NationTier): number {
  return CP_COUNT_BY_TIER[tier];
}

function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

function mergeYields(base: Yields, override?: Partial<Yields>): Yields {
  return {
    money: override?.money ?? base.money,
    influence: override?.influence ?? base.influence,
    ops: override?.ops ?? base.ops,
    boost: override?.boost ?? base.boost,
  };
}

function multiplyYields(a: Yields, scalar: number): Yields {
  return {
    money: a.money * scalar,
    influence: a.influence * scalar,
    ops: a.ops * scalar,
    boost: a.boost * scalar,
  };
}

function addYields(a: Yields, b: Yields): Yields {
  return {
    money: a.money + b.money,
    influence: a.influence + b.influence,
    ops: a.ops + b.ops,
    boost: a.boost + b.boost,
  };
}

function aggregateYieldMult(mods: ModifierState[]): Yields {
  // Start at 1.0 multipliers; multiply any present component-wise
  let m = { money: 1, influence: 1, ops: 1, boost: 1 } as Yields;
  for (const mod of mods) {
    if (mod.effect.kind === "yield_mult") {
      m.money *= mod.effect.money ?? 1;
      m.influence *= mod.effect.influence ?? 1;
      m.ops *= mod.effect.ops ?? 1;
      m.boost *= mod.effect.boost ?? 1;
    }
  }
  return m;
}

function applyYieldMultipliers(y: Yields, mults: Yields): Yields {
  return {
    money: y.money * mults.money,
    influence: y.influence * mults.influence,
    ops: y.ops * mults.ops,
    boost: y.boost * mults.boost,
  };
}

/************************
 * Compilation pipeline  *
 ************************/
export function compileNation(
  a: NationAuthoring,
  turn: number = 1,
  rules: RulesConfig = DEFAULT_RULES
): NationState {
  const cpCount = cpCountForTier(a.tier);

  // Build CP slots (last is executive)
  const cp: CPState[] = Array.from({ length: cpCount }, (_, i) => ({
    index: i,
    kind: i === cpCount - 1 ? "executive" : "regular",
    owner: a.startOwners?.[i] ?? null,
  }));

  // Executive starts locked (UI hint). Enforcement is via canAcquireExecutive().
  const exec = cp[cp.length - 1];
  exec.locked = { reason: `Requires majority (floor) of non-exec CPs and PO ≥ ${rules.execGate.poThreshold}.` };

  // Normalize starting values
  const prosperity = clamp(a.startProsperity ?? 3, 1, 5);
  const unrest = clamp(a.startUnrest ?? 0, 0, 5);
  const po: Record<string, number> = {};
  if (a.startPO) {
    for (const [f, v] of Object.entries(a.startPO)) {
      po[f] = clamp(Math.round(v), 0, 100);
    }
  }

  // Convert authoring modifiers → runtime modifiers
  const modifiers: ModifierState[] = normalizeModifiers(a.modifiers ?? [], turn);

  // Flags → example: launch_capability
  const launchCapability = modifiers.some(
    (m) => m.effect.kind === "flag" && m.effect.name === "launch_capability" && (m.effect.value ?? true)
  );

  // Yields: per-tier then apply per-nation overrides
  const basePerCP = rules.perTierYield[a.tier];
  const yieldPerCP = mergeYields(basePerCP, a.yieldOverridesPerCP);

  // Multipliers: prosperity + yield_mult modifiers
  const prosperityMult = rules.prosperityMultiplier(prosperity);
  const yieldMults = aggregateYieldMult(modifiers);

  // Total estimate: cp.length × perCP × prosperity × yieldMults
  const perCPWithProsperity = multiplyYields(yieldPerCP, prosperityMult);
  const perCPWithAllMults = applyYieldMultipliers(perCPWithProsperity, yieldMults);
  const totalYieldEstimate = multiplyYields(perCPWithAllMults, cp.length);

  return {
    id: a.id,
    name: a.name,
    tier: a.tier,
    cp,
    po,
    security: a.baseSecurity,
    unrest,
    prosperity,
    launchCapability,
    projects: {},
    modifiers,
    yieldPerCP,
    prosperityMult,
    totalYieldEstimate,
  };
}

export function canAcquireExecutive(nation: NationState, factionId: string): boolean {
  const poOK = (nation.po[factionId] ?? 0) >= DEFAULT_RULES.execGate.poThreshold;
  const nonExecOwned = nation.cp.filter((c) => c.kind === "regular" && c.owner === factionId).length;
  const majorityNeeded = Math.floor(nation.cp.length / 2);
  return poOK && nonExecOwned >= majorityNeeded;
}

/*******************************
 * Modifiers: normalization     *
 *******************************/
export function normalizeModifiers(authoring: ModifierAuthoring[], turn: number): ModifierState[] {
  const out: ModifierState[] = [];
  let autoId = 0;
  for (const m of authoring) {
    const id = `mod:${autoId++}`;
    switch (m.kind) {
      case "yield_mult":
        out.push({ id, source: "scenario", effect: { kind: "yield_mult", ...m }, appliedOnTurn: turn });
        break;
      case "mission_dc_delta":
        out.push({ id, source: "scenario", effect: { kind: "mission_dc_delta", mission: m.mission, delta: m.delta }, appliedOnTurn: turn });
        break;
      case "po_change":
        out.push({ id, source: "scenario", effect: { kind: "po_change", target: m.target, amount: m.amount }, appliedOnTurn: turn });
        break;
      case "security_delta":
        out.push({ id, source: "scenario", effect: { kind: "security_delta", amount: m.amount }, appliedOnTurn: turn });
        break;
      case "unrest_delta":
        out.push({ id, source: "scenario", effect: { kind: "unrest_delta", amount: m.amount }, appliedOnTurn: turn });
        break;
      case "flag":
        out.push({ id, source: "scenario", effect: { kind: "flag", name: m.name, value: true }, appliedOnTurn: turn });
        break;
    }
  }
  return out;
}

/*********************
 * Example usage      *
 *********************/
export const EXAMPLE_AUTHORING: NationAuthoring = {
  id: "JPN",
  name: "Japan",
  tier: "major",
  baseSecurity: 6,
  startProsperity: 4,
  startUnrest: 1,
  startPO: { Academy: 72, Servants: 18, Protectorate: 4 },
  traits: ["industrial_base"],
  yieldOverridesPerCP: { boost: 0.3 },
  modifiers: [
    { kind: "yield_mult", money: 1.05, boost: 1.1 },
    { kind: "flag", name: "launch_capability" },
  ],
  startOwners: ["Academy", "Academy", null, null, null, null],
};

// Compile on load (example)
export const EXAMPLE_RUNTIME = compileNation(EXAMPLE_AUTHORING, 1, DEFAULT_RULES);

// Exec gate check (example)
export const EXAMPLE_CAN_TAKE_EXEC = canAcquireExecutive(EXAMPLE_RUNTIME, "Academy");

/************************************************
 * Optional: Public Opinion bonus (derived only) *
 ************************************************/
export function poBonus(po: number): number {
  // Example formula: floor(PO/10) - 3
  return Math.floor(po / 10) - 3;
}

/***************************************************
 * Optional: Basic authoring validator (lightweight) *
 ***************************************************/
export function validateAuthoring(a: NationAuthoring): string[] {
  const errs: string[] = [];
  if (!a.id) errs.push("id is required");
  if (!a.name) errs.push("name is required");
  if (!CP_COUNT_BY_TIER[a.tier]) errs.push(`invalid tier: ${a.tier}`);
  if (typeof a.baseSecurity !== "number") errs.push("baseSecurity must be a number");
  if (a.startProsperity && (a.startProsperity < 1 || a.startProsperity > 5)) errs.push("startProsperity must be 1..5");
  if (a.startUnrest && (a.startUnrest < 0 || a.startUnrest > 5)) errs.push("startUnrest must be 0..5");
  if (a.startOwners) {
    const cpCount = cpCountForTier(a.tier);
    if (a.startOwners.length !== cpCount) errs.push(`startOwners length must be ${cpCount}`);
  }
  return errs;
}
