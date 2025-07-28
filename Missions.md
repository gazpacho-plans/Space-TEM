### **9.2. Mission Resolution Logic**

#### **9.2.0. Turn Structure & Resolution Order**

The weekly turn is resolved in a strict sequence to allow for intelligence and reaction gameplay.

1. **Phase 1: Commitment & Intel**  
   * Players assign Councillors to either **Committed Missions** (e.g., Control Nation, Hostile Takeover, Go to Hiding, Turn Councillor) or **Quick Intel Missions** (Investigate Councillor).  
   * At the end of Phase 1, all Investigate missions are resolved simultaneously. Intel reports are sent privately to the relevant players.  
2. **Mid-Turn: Reaction Window**  
   * Players review the intel reports.  
   * Players may choose to **Cancel** any of their previously assigned Committed Missions.  
   * **Penalty:** If a mission is cancelled, the resources spent on it are **lost**. The Councillor becomes free for Phase 2\.  
3. **Phase 2: Action & Reaction**  
   * Any Councillor not on a Committed Mission can be assigned to a **Quick Reaction Mission** (e.g., Protect Target).  
   * At the end of Phase 2, all remaining Committed Missions and all Quick Reaction Missions are resolved simultaneously.  
   * The turn report is generated and published.  
* **General Formula:** (Relevant\_Attribute \+ d10\_Roll \+ Modifiers)  
* **Success Tiers:** Missions have four potential outcomes based on how much the roll beats or misses the DC.  
  * **Critical Success:** Occurs when the roll exceeds the DC by 10 or more. Grants a significant bonus.  
  * **Success:** Occurs when the roll meets or exceeds the DC.  
  * **Failure:** Occurs when the roll is below the DC.  
  * **Critical Failure:** Occurs when the d10 roll is a natural 1\. Results in a negative consequence.

#### **9.2.1. Mission: Public Campaign**

* **Goal:** To increase your faction's Public Opinion in a target nation.  
* **Resource Cost:** 10 ✨ Influence, 50 💰 Money.  
* **Check:** (📢 Persuasion \+ d10\_Roll) vs. Nation's Base DC.  
* **Outcomes:**  
  * **Critical Success (Beat DC by 10+):** Public Opinion increases by a large amount (e.g., 15 points). The Faction also receives a **"Golden Opportunity"** token.  
  * **Success (Beat DC):** Public Opinion increases by a standard amount (e.g., 5 points).  
  * **Failure (Miss DC):** The mission fails. Resources are lost.  
  * **Critical Failure (d10 roll is 1):** Public Opinion for your faction *decreases*. Possible negative trait gain.

#### **9.2.2. Mission: Control Nation**

* **Goal:** To seize a Control Point in a target nation.  
* **Resource Cost:** 30 ✨ Influence, 25 ⚔️ Operations.  
* **Check:** Opposed Roll: (🎖️ Command \+ d10\_Roll \+ Public\_Opinion\_Bonus) vs. Defender's (🔐 Security \+ d10\_Roll) or Nation's static DC.  
* **Outcomes:**  
  * **Critical Success (Beat DC by 10+):** Seize one CP and the rival faction loses Public Opinion.  
  * **Success (Beat DC):** Seize one CP.  
  * **Failure (Miss DC):** Mission fails. Attacker is revealed.  
  * **Critical Failure (d10 roll is 1):** Mission fails. Attacker is **Detained** for one turn and their faction loses Public Opinion.

#### **9.2.3. Mission: Hostile Takeover**

* **Goal:** To seize control of an Org.  
* **Resource Cost:** 20 ⚔️ Operations, 100 💰 Money.  
* **Check:** Opposed Roll: (🕶️ Espionage \+ d10\_Roll) vs. Defender's (🔐 Security \+ d10\_Roll) or Org's static DC.  
* **Outcomes:**  
  * **Critical Success (Beat DC by 10+):** Seize the Org. Defending Councillor is **Detained**.  
  * **Success (Beat DC):** Seize the Org.  
  * **Failure (Miss DC):** Mission fails. Attacker is revealed.  
  * **Critical Failure (d10 roll is 1):** Mission fails. Attacker is **Detained** and gains the Marked trait.

#### **9.2.4. Mission: Investigate Councillor**

* **Goal:** To uncover intelligence about a rival Councillor.  
* **Resource Cost:** 10 ✨ Influence.  
* **Check:** Opposed Roll: (🔎 Investigation \+ d10\_Roll) vs. (Target's 🔐 Security \+ d10\_Roll).  
* **Outcomes:**  
  * **Critical Success (Beat DC by 10+):** You learn the target's Profession, all Attributes, all Traits, AND their personal resource income from Orgs for the current turn.  
  * **Success (Beat DC):** You learn what **Committed Mission** the target Councillor is currently assigned to for the turn.  
  * **Failure (Miss DC):** You learn nothing. The target receives a notification: "You sense you are being watched."  
  * **Critical Failure (d10 roll is 1):** The mission fails, and the target is notified of exactly who was investigating them.

#### **9.2.5. Mission: Protect Target**

* **Goal:** To defend a friendly asset (a controlled CP, a controlled Org, or another Councillor) for one turn.  
* **Resource Cost:** 5 ✨ Influence, 5 ⚔️ Operations.  
* **Mechanic:** This is a **Quick Reaction Mission** assigned in Phase 2\. When a Councillor is assigned to Protect Target, they actively defend that one asset. If that asset is targeted by a hostile mission this turn, the defender's roll for any opposed check is (Protecting Councillor's 🔐 Security \+ d10\_Roll). This roll replaces the asset's normal static DC.

#### **9.2.6. Mission: Go to Hiding**

* **Goal:** To hide a Councillor from enemy intelligence for one turn.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 5 ⚔️ Operations.  
* **Mechanic:** No roll required. The Councillor is assigned this mission and cannot perform any other actions this turn.  
* **Effect:** Any hostile mission targeting this Councillor that relies on an opposed Investigation or Espionage roll has a **\-10 penalty** applied to the attacker's roll.

#### **9.2.7. Mission: Turn Councillor**

* **Goal:** To compromise a rival Councillor and turn them into a mole, revealing their faction's plans.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 75 ✨ Influence, 100 ⚔️ Operations.  
* **Check:** High-difficulty Opposed Roll: (🕶️ Espionage \+ d10\_Roll \+ Ideological\_Modifier) vs. (Target's 🔐 Security \+ d10\_Roll \+ 3).  
* **Modifiers:**  
  * **Ideological Modifier:** **\-3 Penalty** vs. ideologically opposite faction; **\-1 Penalty** vs. adjacent but opposing axis faction.  
* **Outcomes:**  
  * **Success (Beat DC):** The target is **Turned**. At the start of the next turn's Intel Phase, you receive a full, accurate report of all missions assigned by the target's entire faction.  
  * **Failure (Miss DC):** The attempt fails. The attacking Councillor is immediately **Detained** for one turn.  
  * **Critical Failure (d10 roll is 1):** The attempt fails catastrophically. The target's faction is immediately granted a free, successful Investigate Councillor mission (Critical Success outcome) against any one Councillor of the attacker's choice.

#### **9.2.8. Mission: Manage Project**

* **Goal:** To accelerate your faction's progress on a chosen Faction Project.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 25 💰 Money.  
* **Check:** (⚛️ Science \+ d10\_Roll) vs. Project's Base DC (e.g., DC 12).  
* **Outcomes:**  
  * **Critical Success (Beat DC by 10+):** Applies a **2.5x multiplier** to your faction's total passive 🔬 Research generation for this turn.  
  * **Success (Beat DC):** Applies a **1.5x multiplier** to your faction's total passive 🔬 Research generation for this turn.  
  * **Failure (Miss DC):** No multiplier is applied.  
  * **Critical Failure (d10 roll is 1):** A small amount of accumulated research on the project is lost.  
* **Special Rule:** If performed by a Councillor on-station at a Hab, this mission's research multiplier is increased by \+0.5x at each success tier (e.g., 1.5x becomes 2.0x).

#### **9.2.9. Mission: Investigate Alien Activity**

* **Goal:** To contribute a large amount of research to a Global Project.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 50 💰 Money, 20 ⚔️ Operations.  
* **Check:** (⚛️ Science \+ 🔎 Investigation \+ d10\_Roll) vs. Global Project's DC.  
* **Outcomes:**  
  * **Success:** A large, flat amount of 🔬 Research (e.g., 50 points) is added to the targeted Global Project.  
  * **Failure:** The mission fails. Resources are lost.  
  * **Critical Failure:** The mission fails, and the Councillor leading the investigation is **Detained** for one turn.

#### **9.2.10. Mission: Sabotage Project**

* **Goal:** To destroy a rival faction's accumulated research on their active Faction Project.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 75 💰 Money, 50 ⚔️ Operations.  
* **Check:** Opposed Roll: (Attacker's ⚛️ Science \+ d10\_Roll) vs. (Defender's Project Manager's 🔐 Security \+ d10\_Roll).  
* **Outcomes:**  
  * **Success:** A significant amount of 🔬 Research is destroyed from the target's project. The attacker is revealed.  
  * **Failure:** The attempt is thwarted. The attacker is revealed.  
  * **Critical Failure:** The attempt is thwarted, and the attacking Councillor is **Detained** for one turn.

#### **9.2.11. Mission: Steal Project**

* **Goal:** To steal a portion of a rival's research and add it to your own project.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 100 💰 Money, 25 ⚔️ Operations.  
* **Check:** Opposed Roll: (Attacker's 🕶️ Espionage \+ d10\_Roll) vs. (Defender's Project Manager's 🔐 Security \+ d10\_Roll).  
* **Outcomes:**  
  * **Success:** A portion of 🔬 Research is stolen from the target's project and added to your own active project. The attacker is revealed.  
  * **Failure:** The attempt is thwarted. The attacker is revealed.  
  * **Critical Failure:** The attempt is thwarted, and the attacking Councillor gains the Marked negative trait.

#### **9.2.12. Mission: Purchase Org**

* **Goal:** To acquire an unowned Org through economic and political influence.  
* **Type:** Committed Mission (Phase 1\)  
* **Mechanic:** No roll required. Automatically succeeds if prerequisites are met.  
* **Prerequisites:**  
  1. The target Org must be unowned.  
  2. The acting Councillor's faction must control at least one CP in the Org's home nation.  
  3. The faction must have enough 💰 Money and ✨ Influence to pay the purchase cost.  
* **Effect:** The resources are deducted from the faction's treasury, and the acting Councillor gains control of the Org.

#### **9.2.13. Mission: Launch Hab**

* **Goal:** To construct a Tier 1 Hab Core in a designated orbit.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 200 💰 Money, 100 ⚔️ Operations, 50 🚀 Boost.  
* **Prerequisites:** Faction must have researched the "Orbital Core" Faction Project.  
* **Check:** (⚛️ Science \+ 🏢 Administration \+ d10\_Roll) vs. Launch DC (e.g., DC 18).  
* **Outcomes:**  
  * **Success:** A new Hab Core is successfully established in the target orbit.  
  * **Failure:** The launch fails. All resources are lost.  
  * **Critical Failure:** The launch fails catastrophically. All resources are lost, and the Faction Project to build the Hab must be researched again.

#### **9.2.14. Mission: Go to Orbit**

* **Goal:** To move a Councillor from Earth to a friendly Hab.  
* **Type:** Committed Mission (Phase 1\)  
* **Resource Cost:** 10 💰 Money, 1 🚀 Boost.  
* **Mechanic:** No roll required. Automatically succeeds.  
* **Effect:** The Councillor's location is changed from "Earth" to the ID of the target Hab. They are considered "on-station" starting the next turn.
