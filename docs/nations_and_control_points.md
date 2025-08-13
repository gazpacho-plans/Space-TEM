# Space TEM — Nations v0.5 (TypeScript‑backed Data & Rules)

**Scope**: Replaces the old nation object/CP spec with a two‑layer TypeScript system (Authoring → Runtime). Removes duplicated fields, clarifies Executive gating, and standardizes a future‑proof modifiers framework.

**Why**: Authors keep data minimal and readable; the game expands it into rich, validated runtime state. This avoids drift and makes later features (events, traits, projects) plug‑and‑play.

---

## 1) Design goals

- **Single source of truth** for CP count → `tier` only. No `cp_total` field.
- **Executive is a rule**, not a stored index → last CP is `kind:"executive"` and gate‐locked by logic.
- **Structured ownership** → CP slots carry `owner`, `defense`, and `tags` (not loose strings).
- **Extensible modifiers** → one normalized `modifiers[]` array for yields, DC deltas, flags, etc.
- **Consistent vocabulary** → Resources are **Money, Influence, Operations (Ops), Boost**.

---

## 2) Authoring schema (designer‑facing)

Use this for hand‑edited JSON/TS. Keep it minimal; everything else is derived at load.

```ts
export type NationTier = "major" | "regional" | "minor" | "micro";

export type Yields = { money: number; influence: number; ops: number; boost: number };

export type MissionKey =
  | "public_campaign" | "control" | "purge" | "increase_unrest" | "stabilize" | "coup";

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
  tier: NationTier;              // ← CP count is derived from this
  baseSecurity: number;          // opposed‑roll defense
  startProsperity?: number;      // 1–5 (default 3)
  startUnrest?: number;          // 0–5 (default 0)
  startPO?: Record<string, number>; // factionId → 0..100
  traits?: string[];             // flavor tags
  modifiers?: ModifierAuthoring[]; // optional starting modifiers
  yieldOverridesPerCP?: Partial<Yields>; // e.g. { boost: 0.30 }
  notes?: string;
  startOwners?: (string | null)[]; // optional initial owners by CP index
};
```

**Authoring example**

```json
{
  "id": "JPN",
  "name": "Japan",
  "tier": "major",
  "baseSecurity": 6,
  "startProsperity": 4,
  "startUnrest": 1,
  "startPO": { "Academy": 72, "Servants": 18, "Protectorate": 4 },
  "traits": ["industrial_base"],
  "yieldOverridesPerCP": { "boost": 0.3 },
  "modifiers": [
    { "kind": "yield_mult", "money": 1.05, "boost": 1.1 },
    { "kind": "flag", "name": "launch_capability" }
  ],
  "startOwners": ["Academy", "Academy", null, null, null, null]
}
```

---

## 3) Runtime schema (game‑facing)

The loader compiles Authoring → Runtime on startup. No duplication; everything consistent.

```ts
export type CPKind = "regular" | "executive";

export interface CPState {
  index: number;                       // 0..(n-1)
  kind: CPKind;                        // executive is always the last slot
  owner: string | null;                // factionId or null
  defense?: { byPlayerId: string; expiresOnTurn: number };
  tags?: string[];                     // e.g. ["capital", "spaceport"]
  locked?: { reason: string };         // exec gate message, etc.
}

export interface ModifierState {
  id: string;                          // unique
  source: "trait" | "project" | "event" | "mission" | "scenario";
  effect:
    | { kind: "yield_mult"; money?: number; influence?: number; ops?: number; boost?: number }
    | { kind: "mission_dc_delta"; mission: MissionKey; delta: number }
    | { kind: "po_change"; target: "all" | string; amount: number }
    | { kind: "security_delta"; amount: number }
    | { kind: "unrest_delta"; amount: number }
    | { kind: "flag"; name: string; value?: boolean };
  appliedOnTurn: number;
  expiresOnTurn?: number;
}

export interface NationState {
  id: string;
  name: string;
  tier: NationTier;
  cp: CPState[];                       // generated from tier; last = executive
  po: Record<string, number>;          // Public Opinion 0..100 per faction
  security: number;                    // live
  unrest: number;                      // 0..5
  prosperity: number;                  // 1..5
  launchCapability: boolean;           // from flags/projects
  projects: Record<string, "locked" | "available" | "completed">;
  modifiers: ModifierState[];          // normalized
  yieldPerCP: Yields;                  // after any nation overrides
  prosperityMult: number;              // e.g. 0.8..1.2
  totalYieldEstimate: Yields;          // cp.length × yieldPerCP × prosperityMult × yieldMults
}
```

---

## 4) Generation rules

- **CP slots**: `cp.length = mapTierToCount(tier)` where counts are Major 6 / Regional 4 / Minor 2 / Micro 1.
- **Executive slot**: last CP is `kind:"executive"` and is **gate‑locked** until the Exec rule passes.
- **Ownership**: each CP tracks `owner` (factionId or null) plus optional `defense` status from Protect Target.
- **Launch capability**: nation‑level boolean flag – surfaced via `flag:"launch_capability"` or projects.

**Exec gate (rule, not stored)**

> A faction may acquire the Executive CP if it has **PO ≥ 60** in the nation **and** owns at least **⌊cp.length/2⌋** non‑executive CPs.

The loader/UI may set `cp[last].locked.reason = "Requires majority (floor) of non‑exec CPs and PO ≥ 60."` for clarity.

---

## 5) Economy & yields

Per‑tier baseline **per‑CP** yields (edit in balance config):

- **Major**: Money 6, Influence 2, Ops 1, Boost 0.25
- **Regional**: 4, 1, 1, 0.15
- **Minor**: 2, 1, 0, 0.10
- **Micro**: 1, 0, 0, 0.05

**Prosperity** (1–5) multiplies yields: `mult = 0.8 .. 1.2` (linear by step of 0.1). Store prosperity in runtime; it’s scenario‑driven or affected by events.

**Nation overrides**: `yieldOverridesPerCP` lets a nation tweak its per‑CP baseline (e.g., a space‑focused country with +Boost).

**Total yield estimate** (for UI): `cp.length × perCP × prosperityMult × (stacked yield_mult modifiers)`.

---

## 6) Public Opinion (PO)

Store raw PO per faction on the nation (`po[factionId] = 0..100`).

- **Derived bonus** (not stored): `poBonus(po) = floor(po/10) − 3` (e.g., 30→0, 80→+5).
- **Shifts** come from missions, events, and modifiers (e.g., `{kind:"po_change", target:"all", amount:+5}`).

---

## 7) Missions that touch nations (interface points)

This doc defines only the **nation‑side** pieces each mission needs. (Mission access/costs live in the Missions doc.)

- **Public Campaign**: uses nation PO. Check style is configurable:

  - **Option A (flat)**: `(Persuasion + d10) vs DC 12` → PO: +10 / +20 / −5.
  - **Option B (per‑nation)**: `(Persuasion + d10) vs Nation Base DC` with the same outcomes.
  - Apply any `mission_dc_delta` modifiers.

- **Control Nation**: contested check uses nation **Security** on defense.

  - Default: `(Persuasion + d10 + poBonus) vs (Security + d10)`
  - Alt config (project preference): make **Command** the attacker stat. Keep the nation side unchanged.

- **Purge / Increase Unrest / Stabilize / Coup**: these reference `security`, `unrest`, and optional Ops‑spend meta‑rule (below). Any defense from Protect Target on a CP grants the **defender** a +4.

**Optional: Operations‑spend meta‑rule**

> For **Increase Unrest, Stabilize, Coup**, attackers may spend Ops: **+1 per 5 Ops (max +4)**. Defenders may spend to match. Ops are consumed regardless of outcome.

---

## 8) Modifiers framework

One normalized array powers all tweaks:

- `yield_mult` → multiplicative economy dials.
- `mission_dc_delta` → per‑mission difficulty seasoning.
- `po_change`, `security_delta`, `unrest_delta` → immediate or timed state shifts.
- `flag` → boolean capabilities (e.g., `launch_capability`).
- Each modifier records `source`, `appliedOnTurn`, and optional `expiresOnTurn` for decay.

This avoids adding ad‑hoc fields for every new rule.

---

## 9) Example: compiled runtime (snippet)

```json
{
  "id": "JPN",
  "name": "Japan",
  "tier": "major",
  "cp": [
    { "index": 0, "kind": "regular", "owner": "Academy" },
    { "index": 1, "kind": "regular", "owner": "Academy", "defense": { "byPlayerId": "p1", "expiresOnTurn": 7 } },
    { "index": 2, "kind": "regular", "owner": null },
    { "index": 3, "kind": "regular", "owner": null },
    { "index": 4, "kind": "regular", "owner": null },
    { "index": 5, "kind": "executive", "owner": null, "locked": { "reason": "Requires majority (floor) of non‑exec CPs and PO ≥ 60." } }
  ],
  "po": { "Academy": 72, "Servants": 18, "Protectorate": 4 },
  "security": 6,
  "unrest": 1,
  "prosperity": 4,
  "launchCapability": true,
  "projects": {},
  "modifiers": [
    { "id": "m1", "source": "trait", "effect": { "kind": "yield_mult", "money": 1.05, "boost": 1.1 }, "appliedOnTurn": 1 }
  ],
  "yieldPerCP": { "money": 6, "influence": 2, "ops": 1, "boost": 0.3 },
  "prosperityMult": 1.1,
  "totalYieldEstimate": { "money": 39.6, "influence": 13.2, "ops": 6.6, "boost": 1.98 }
}
```

---

## 10) Migration checklist (from v0.4)

- **Delete** `cp_total` and `executive_index`.
- **Keep** `tier`; runtime generates `cp[]` and flags the last one as `executive`.
- **Replace** ownership arrays with structured `cp: CPState[]` entries.
- **Rename** resources to **Money, Influence, Operations (Ops), Boost** everywhere.
- **Move** any special‑case nation quirks into `modifiers[]`.
- **Centralize** the Exec gate (don’t store booleans; enforce at mission/assignment time).
- **Optionally** adopt per‑nation Public Campaign DC via `mission_dc_delta` (otherwise keep flat DC 12).

---

## 11) Appendix: Rules hooks

- **PO bonus** (derived only): `floor(PO/10) − 3`.
- **Prosperity multiplier**: `0.8 + 0.1 × (prosperity − 1)` (1→0.8 … 5→1.2).
- **Tier → CP count**: Major 6 / Regional 4 / Minor 2 / Micro 1.
- **Protect Target**: defends **one asset** (a CP, an Org, or a Councillor) and grants +4 to the defender vs hostile missions.

> Implementation lives in the TypeScript starter we ship with this doc (compileNation, canAcquireExecutive, etc.).

---

### End v0.5

