// rules.ts
export const CP_BY_TIER: Record<NationTier, number> = {
  major: 6, regional: 4, minor: 2, micro: 1
};

export const CAPACITY_SEED_BY_PROFILE = {
  industrial: { money: 16, influence: 4, ops: 4, boost: 0.6 },
  services:   { money: 18, influence: 5, ops: 3, boost: 0.3 },
  research:   { money: 12, influence: 6, ops: 3, boost: 0.4 },
  space:      { money: 11, influence: 3, ops: 3, boost: 0.9 },
} as const;

export const PROSPERITY_MULT = { 1:0.8, 2:0.9, 3:1.0, 4:1.1, 5:1.2 } as const;
// Clamp at 0.6 so late-game chaos doesn’t nuke economies:
export const UNREST_MULT = (u: number) => Math.max(0.6, 1 - 0.1 * u);