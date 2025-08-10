```markdown
# Nations & Control Points Mechanic Spec v0.4

## Overview
Nations represent political units on Earth, divided into tiers with a fixed number of Control Points (CPs) that factions compete to seize. CPs provide weekly resource yields (Funds, Influence, Ops, Boost) and enable special actions like launches. Public Opinion (PO) influences mission success, while unrest adds strategic depth. This mechanic encourages team play through coordinated PO building and defenses, with simplified simulation to avoid complexity.

## Mechanics

### Nation Tiers and CPs
- Nations are categorized by tier, determining CP count and yields.
- **CP by Tier**:
  - **Major**: 6 CPs (including 1 Executive).
  - **Regional**: 4 CPs (including 1 Executive).
  - **Minor**: 2 CPs (including 1 Executive).
  - **Micro**: 1 CP (Executive = the single CP).
- The Executive CP is the last CP (special rules in Section 6.3).

### Per-CP Yields (Per Week)
- Yields are per CP owned, before optional Prosperity multiplier.
- **Per-CP Yields Table**:
  | Tier     | 💰 Funds | ✨ Influence | ⚔️ Ops | 🚀 Boost/MC |
  | -------- | -------- | ----------- | ------ | ----------- |
  | Major    | 6        | 2           | 1      | 0.25        |
  | Regional | 4        | 1           | 1      | 0.15        |
  | Minor    | 2        | 1           | 0      | 0.10        |
  | Micro    | 1        | 0           | 0      | 0.05        |

### Prosperity Multiplier (Optional)
- A 1–5 knob to scale yields.
- **Multiplier Table**:
  | Prosperity | Multiplier |
  | :--------- | :--------- |
  | 1          | 0.8×       |
  | 2          | 0.9×       |
  | 3          | 1.0×       |
  | 4          | 1.1×       |
  | 5          | 1.2×       |

### Launch Capability
- Flag enabling launches and +1 🚀/week to the Executive holder.
- Established via *Build Launch Facility* mission (Section 6.5).
- Prerequisite for *Launch Hab* (GDD Section 9.2.13).

### Public Opinion (PO)
- 0–100 per faction per nation; clamp after changes.
- **PO Bonus Formula**:
  ```
  PO_Bonus = floor(PO / 10) − 3   # e.g., 30 = 0, 80 = +5
  ```
- **Thresholds**:
  - *Control Nation* (neutral CP): Any PO.
  - *Purge* (enemy CP): PO ≥ 40.
  - Executive CP: PO ≥ 60 + own ≥ ⌊cp_total/2⌋ non-Executive CPs.
- **Public Campaign Mission**:
  - DC 12.
  - Success: +10 PO; Crit: +20 PO; Fail: −5 PO (your faction only).

### Unrest
- 0–3 per nation; influenced by missions (Sections 6.6–6.8).
- Ties to Traits (e.g., *Apocalyptic*: +1 Persuasion for *Public Campaign* if unrest ≥ 2).

### Ops Spend (Optional for *Increase Unrest*, *Stabilize Nation*, *Coup Nation*)
- +1 to roll per 5 Ops spent (max +4).
- Declared on submission (attacker); defender can match if opposing.
- Ops consumed regardless of outcome.

### CP Interaction Missions (Committed Unless Stated)
1. **Control Nation (Seize Neutral CP)**:
   - Target: Neutral CP index.
   - Rolls: Attacker = Persuasion + d10 + PO_Bonus; Defender = Security + d10 (if Defended).
   - Outcomes: Success transfers CP; Crit: +5 PO (attacker).

2. **Purge (Seize Enemy-Held CP)**:
   - Requirements: PO ≥ 40.
   - Rolls: Attacker = Command + d10 + PO_Bonus; Defender = Security + d10 + 4 (if Defended).
   - Outcomes: Success: Transfer CP + Legitimacy shock (±5 PO); Crit Success: Remove Defend; Fail: No change; Crit Fail: +1 Heat, −5 PO (attacker).

3. **Protect Target (Quick)**:
   - Target: One asset (CP, Org, Councillor) per player per turn.
   - Effect: Asset Defended (+4 to defender rolls) until end of turn.

4. **Build Launch Facility (Committed)**:
   - Target: Nation without launch_capability.
   - Requirements: Hold Executive CP + completed National Launch Program.
   - Cost: 💰 200 + 🚀 10 (refunded if not met).
   - Roll: None (deterministic).
   - Effect: Set launch_capability = true; +1 🚀/week to Executive holder; enables *Launch Hab*.

5. **Increase Unrest (Committed)**:
   - Rolls: Attacker = Command + d10; Defender = Security + d10 + 4 (if Defended CP in nation).
   - Outcomes: Success: unrest +1 (max 3) −5 PO to CP holders; Crit: unrest +2; Fail: No change; Crit Fail: +1 Heat, −5 PO (attacker).

6. **Stabilize Nation (Committed)**:
   - Rolls: Attacker = Persuasion + d10 + 2 (if hold CP) + 2 (if hold Executive); Defender = Command + d10.
   - Outcomes: Success: unrest −1 (min 0) +5 PO to Executive holder; Crit: unrest −2.

7. **Coup Nation (Committed)**:
   - Requirements: unrest ≥ 2.
   - Rolls: Attacker = Command + d10 + (unrest × 2); Defender = Security + d10 + 2 (if hold Executive).
   - Outcomes: Success: All CPs neutral, remove Defend; −10 PO to former Executive holder, −5 PO to others; optional prosperity −1; Crit Fail: +2 Heat, −10 PO (attacker).

### Turn Sequence
1. **Upkeep**:
   - Compute yields (Section 9); apply Prosperity.
   - Progress projects (Section 11).
   - Reset Defend states.
2. **Phase 1 (Committed)**:
   - Submit *Public Campaign*, *Increase Unrest*, *Stabilize Nation*, *Purge*, *Control Nation*, *Build Launch Facility*.
   - Resolution order per nation: Public Campaign → Increase Unrest/Stabilize → Purge → Control Nation → Build Launch Facility.
3. **Phase 2 (Quick)**:
   - Submit *Protect Target* (if no Committed action).
4. **End of Turn**:
   - Apply status expirations.

### Data to Track
- **Nation JSON Example**:
  ```
  {
    "id": "USA",
    "name": "United States",
    "tier": "Major",
    "cp_total": 6,
    "executive_index": 5,
    "prosperity": 4,
    "launch_capability": true,
    "unrest": 1,
    "owners": [
      {"faction": "The Initiative", "cp": 5},
      {"faction": "Humanity First", "cp": 0}
    ],
    "po": {"The Initiative": 62, "Humanity First": 20, "The Protectorate": 10, "The Academy": 8},
    "cp_status": {
      "3": {"defended_by": null}
    }
  }
  ```
- **Per-CP Transient States**: `defended_by: faction_id | null` (cleared at end of turn).

## Examples
**Example 1 — Income Calculation**:
- Regional nation (4 CPs), Prosperity 3 (1.0×), ownership: The Initiative = 2 CPs.
- Per-CP yields: 💰4, ✨1, ⚔️1, 🚀0.15.
- Initiative income: 2 × (4,1,1,0.15) = (8,2,2,0.3).
- Split among 2 players: Each gets (4,1,1,0.15) + character sheet income (e.g., Traits, Orgs).
- If launch_capability = true: +1 🚀 to Executive holder, split equally.

**Example 2 — Purge Mission**:
- Attacker Command 6, PO 72 (PO_Bonus +4), rolls d10 = 7 → 6 + 7 + 4 = 17.
- Defender Security 5, Defended (+4), rolls d10 = 5 → 5 + 5 + 4 = 14.
- Success (17 > 14): Transfer CP, +5 PO attacker, −5 PO defender. No unrest impact.

**Example 3 — Build Launch Facility**:
- Initiative holds Executive in USA (no launch_capability).
- Completed National Launch Program.
- Pay 💰 200 + 🚀 10; deterministic success → launch_capability = true; +1 🚀/week to Initiative (split among players).

## Balance Dials
- Public Campaign DC / deltas: DC 12 / +10 / +20 / −5.
- Defend bonus: +4.
- Purge PO gate: PO ≥ 40.
- Executive PO gate: PO ≥ 60.
- Legitimacy shock on Purge success: ±5 PO.
- Unrest range: 0–3.
- Increase Unrest: Success +1 (crit +2) unrest; PO −5 to CP holders.
- Stabilize Nation: Success −1 (crit −2) unrest; PO +5 to Exec holder.
- Coup Nation: Req unrest ≥ 2; attacker bonus +2 per unrest; optional prosperity −1 on success.
- Build Launch Facility cost: 💰 200 + 🚀 10.
- Ops spend rate & cap: +1 per 5 Ops, max +4 (for Increase Unrest, Stabilize, Coup).

## Future Considerations
- **Resource Transfers**: `/transfer_resource [target_player] [amount] [type]` to send/receive resources.
- **Dynamic Traits**: Missions may add/remove Traits based on unrest (e.g., high unrest adding Pariah).
- **Crackdown**: Add as an optional mission to reduce unrest but increase PO penalties.
- **Projects Expansion**: Link to full research system (GDD Section 9.7).

## References
- `professions.json`: Mission access (GDD Section 9.5).
- `positive_traits.json`: Unrest conditions (GDD Section 9.4.1).
- GDD Sections: 9.2 (Mission Resolution), 5 (Resources), 9.7 (Projects), 9.2.13 (Launch Hab).
```
