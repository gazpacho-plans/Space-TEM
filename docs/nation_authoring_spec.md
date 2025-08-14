## Nation Authoring Spec (Space-TEM)

This document defines the authoring requirements for nation data. There is no runtime enforcement in Python; validation can be performed by your content pipeline or tests. The economy utilities consume a `NationState` shaped object as described below.

### Required fields

- **id**: short unique string (e.g., `"JPN"`).
- **name**: display name (e.g., `"Japan"`).
- **tier**: one of `"major" | "regional" | "minor" | "micro"`.
  - Determines the total number of CPs via `CP_BY_TIER`.
- **economyProfile**: one of `"industrial" | "services" | "research" | "space"`.
  - Determines the capacity seed via `CAPACITY_SEED_BY_PROFILE`.
- **baseSecurity**: integer used for opposed checks (economy does not use this directly).

### Optional fields (with defaults)

- **startProsperity**: integer 1–5, default `3`.
- **startUnrest**: integer 0–5, default `0`.
- **startPO**: map of `factionId -> integer 0–100`. Values outside the range should be clamped by your data loader.
- **startFlags**: string array of nation flags. Notable flag: `"launch_capability"` enables Boost output.
- **startModifiers**: array of catalog ids that resolve to modifier records (see Effects below).
- **projects**: optional map of project states if you co-locate them on the nation.

### Control Points (CP)

- A nation has `CP_BY_TIER[tier]` control points; the last CP is always the `"executive"` CP.
- Each CP has: `index` (0..n-1), `kind` (`"regular" | "executive"`), `owner` (factionId or null), optional `tags`.
- Executive acquisition policy (computed at runtime, not stored): requires faction PO ≥ `EXECUTIVE_PO_THRESHOLD` and a strict majority of regular CPs.

### Effects and stages

- Effects are normalized modifier records attached to a nation. Current effect kind supported by the economy is `yield_mult`.
- **Stages**:
  - **capacity**: multiplies nation-wide capacity before splitting across CPs.
  - **owner_share**: multiplies a faction’s share after CP split; may specify `appliesToFactionId` to scope the effect to one faction.
  - **post**: reserved for flat grants after shares (e.g., executive +1 Boost if nation can launch). The built-in economy util adds this executive grant automatically; add more in your game logic if needed.

### Economy overview

1) Compute capacity: `seed × prosperity × unrest × capacity_mods`.
   - If the nation lacks `"launch_capability"`, set Boost capacity to 0.
2) Split equally across CPs (micro nations still count as 1 for splitting).
3) For a given faction: multiply by `owner_share` mods scoped to that faction (or global owner-share mods).
4) Add flat post-stage grants (currently: +1 Boost if the faction holds the executive and the nation can launch).

### Reference constants

- `CP_BY_TIER`: `{ major: 6, regional: 4, minor: 2, micro: 1 }`.
- `CAPACITY_SEED_BY_PROFILE`:
  - `industrial`: `{ money: 16, influence: 4, ops: 4, boost: 0.6 }`
  - `services`: `{ money: 18, influence: 5, ops: 3, boost: 0.3 }`
  - `research`: `{ money: 12, influence: 6, ops: 3, boost: 0.4 }`
  - `space`: `{ money: 11, influence: 3, ops: 3, boost: 0.9 }`
- `PROSPERITY_MULT`: `{ 1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2 }`.
- `UNREST_MULT(u)`: `max(0.6, 1 - 0.1 * u)`.
- `BOOST_FLAG`: `"launch_capability"`.
- `EXECUTIVE_PO_THRESHOLD`: `60`.

### Minimal runtime shape consumed by Python economy

- `NationState` must provide:
  - `id, name, tier, economyProfile`.
  - `cp: List[CPState]` (last CP must have `kind = "executive"`).
  - `po: Dict[factionId, int]`.
  - `security: int, unrest: int, prosperity: int`.
  - `flags: Set[str]`.
  - `modifiers: List[ModifierState]` with `effect.kind == "yield_mult"` and optional per-channel multipliers.

Author your source-of-truth in JSON/YAML or Python and adapt your loader to this shape; the Python economy util performs pure calculations and does not enforce invariants.


