# Nation Card Example:  
(control point) (control point) (control point) (control point)  
### Stats:  

🏛️ Government Type (Autocratic, Thocratic, Monarchy, Olagarcy, Republic)  
🕊️ Democracy Index (1-10 float) // civil liberties and electoral process  
🐌 Bureaucracy Score (1-10 float) // gov efficiency  
🤬 Unrest (0-5 float, displayed as int: Peacful, Subversion, Strife, Insurgency, Civil War)  
---
📊 Public Opinion (0-100 pie chart with all other factions)  
📈 Prosperity (float) // economic and societal success  
📖 Education (1-10 float)  
🔬 Research Output (float)  
---
🪖 Armies (int)  
⚓ Navies (int always less than armies)  
☢️ Nukes (int)  
---
🧑‍🚀 Launch facilities (int)  

# System Explanation
## Control Points
 Control Points represent key nodes of political and economic power in a nation. Every nation has between 1 and 6 control points, depending on its 📈 prosperity.
 The faction that owns a control point has loyal followers in positions of authority. Control points grant their faction a portion of the 💰 money, 🔬 research, and 🚀 boost income produced by the nation. Proportional to controlled CPs vs total CPs of a nation.

### Control Point Types:
 Control points come in a variety of types, depending on the national Government.
 Last to control is always: 'Executive' Gives full control of Nation's Nukes.

## Government   
 Gov Type provides access to unique events and actions, aswell as affecting base resting vaules for 🕊️, 🐌, & 🤬.
 🕊️ Democracy Index affects how quickly 🤬 decays.
 🐌 Bureaucracy Score affects how quickly 🕊️ can change, and how much 💰 & 🔬 income is wasted.
 🤬 Unrest is primarily increased by players executing 'Increase Unrest' Missions in the nation. Once 🤬 is at (4)Insurgency or higher, 'Coup Nation' becomes available to factions with high public opinion. Sustained high 🤬 can cause a Revolution event (gov type can switch, and income penalties will be applied) 

## Public Opinion  
 Public opinion is a primary source of 📢 influence. You will also receive bonuses on missions in nations where a large portion of the public is on your side
 
## Prosperity, Education & Research
 📈 Prosperity is representative of GDP, population, & Investment Capital  
 📖 Education directly influences 🔬 at a cost to 📈  

## Military & Aerospace
 🪖/⚓ Can be built if nation prioritizes 'Fund Military' policy (-📈, +🐌)
 ☢️ Can be built if nation prioritizes 'Build Nuclear Weapons' policy (-📈, +🤬, +🔬)
 🧑‍🚀 Launch facilities directly determine 🚀 boost income. Can be built if nation prioritizes 'Fund Space Program' policy (-📈, +🐌, +📖)
