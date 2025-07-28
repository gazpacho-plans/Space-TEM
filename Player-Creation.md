### **9.3. Character Creation Logic**

* **Process:**  
  1. Player runs /create\_councillor command, choosing a Profession.  
  2. Bot retrieves the attribute ranges for that Profession from the table in 9.3.1.  
  3. For each attribute, the bot rolls a random number within the defined range.  
  4. The bot assigns one random positive Trait **with a 0 XP Cost** from the table in 9.4.1.  
  5. The bot has a small chance to also assign a random Negative or Mixed Trait to the character from the tables in 9.4.2 and 9.4.3.  
  6. The resulting Councillor object is saved to the database.  
* **9.3.1. Profession Attribute Ranges Table:**

| Profession | Per | Inv | Esp | Com | Adm | Sci | Sec | XP Cost |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Kingpin** | 3-5 | 0-4 | 3-5 | 3-5 | 4-6 | 0 | 2-6 |  |
| **Professor** | 1-7 | 4-6 | 0-4 | 0-4 | 2-6 | 4-6 | 0-1 | 20 |
| **Officer** | 2-6 | 0-3 | 2-4 | 6-8 | 2-6 | 0-2 | 4-6 | 20 |
| **Governor** | 4-8 | 1-5 | 0-4 | 0-3 | 2-6 | 0-1 | 2-4 | 20 |
| **Celebrity** | 6-8 | 0-3 | 0-1 | 0-1 | 2-6 | 0 | 2-6 |  |
| **Rebel** | 2-6 | 0-4 | 3-7 | 5-7 | 0-2 | 0 | 2-6 |  |
| **Spy** | 2-6 | 4-6 | 6 | 1-3 | 0-2 | 0-1 | 3-5 | 10 |
| **Executive** | 1-7 | 0-4 | 0-2 | 3-5 | 4-6 | 0-3 | 2-4 |  |
| **Test Pilot** | 1d5 | 0-4 | 0-2 | 5-7 | 0-6 | 4-6 | 2-6 | 20 |
| **Inspector** | 2-4 | 4-6 | 0-4 | 3-5 | 0-2 | 0-2 | 3-5 |  |
| **Operative** | 1-3 | 2-4 | 6 | 3-5 | 0-1 | 0-1 | 3-5 |  |
| **Tycoon** | 0-5 | 0-3 | 0-3 | 1-5 | 7 | 0-4 | 1-5 | 20 |
| **Agency Director** | 2-4 | 2-6 | 0-2 | 0 | 1-5 | 7 | 1-3 | 20 |
| **Journalist** | 4-8 | 6 | 1-5 | 0 | 0-2 | 0-3 | 0-1 |  |
| **Activist** | 4-8 | 3-5 | 1-5 | 0-1 | 0-1 | 0-1 | 0-1 | 10 |
| **Tech Mogul** | 2-6 | 0-4 | 0-3 | 0-2 | 2-6 | 4-6 | 2-4 |  |
| **Local Agent** | 1-3 | 7 | 3-5 | 0-1 | 0-3 | 0-2 | 2-4 | 10 |
| **Diplomat** | 3-7 | 1-5 | 2-6 | 1-3 | 2-6 | 0-1 | 3-5 |  |
| **Judge** | 3-7 | 4-6 | 0-3 | 0-2 | 1-5 | 0-1 | 2-4 |  |
| **Hacker** | 0-4 | 4-6 | 4-6 | 0-1 | 0-3 | 1-3 | 0-3 |  |
| **Fixer** | 2-4 | 2-6 | 4-6 | 0-1 | 0-1 | 0-1 | 0-4 |  |
| **Captain** | 1 | 0-5 | 2-6 | 4-6 | 1 | 0-1 | 1-5 | 20 |
| **Evangelist** | 6-8 | 0-2 | 0-1 | 2-4 | 1-5 | 0 | 0-4 |  |

### **9.4. Traits Logic**

Traits are passive modifiers that affect a Councillor's abilities. They can be positive, negative, or mixed. Players start with one random, free positive trait and can purchase more with XP. Negative traits can sometimes be removed by paying a cost.

* **Acquisition/Removal:**  
  * /acquire\_trait \[trait\_name\]  
  * /remove\_trait \[trait\_name\]  
* **9.4.1. Positive Traits Table:**

| Trait | XP Cost | Description |
| :---- | :---- | :---- |
| **Government** | 20 | A member of a recognized government with official status. |
| **Transparent** |  | Always means exactly what he or she says. |
| **Apocalyptic** |  | Believes the end of humanity is nigh and wishes others to do so. |
| **Aware** |  | Particularly skilled at detecting other councillors. |
| **Beloved** |  | Popular regardless of their loyalties. |
| **Hard Target** | 20 | Will strike back if attacked. |
| **Streetwise** | 20 | Skilled at navigating dark corners in his or her home nation. |
| **Untouchable** | 150 | In too important a position to be safely deleted. |
| **Veteran** |  | A former member of his or her home nation's armed forces. |
| **Ace Assassin** |  | An efficient killer. |
| **Vengeful** |  | It's payback time. |
| **Quick Learner** |  | Picks up new skills faster than most. |
| **Striver** |  | Dedicated to self-improvement. |
| **Survivor** | 10 | Very hard to kill during episodes of mass violence. |
| **Crew** |  | Has a small team of loyal followers who serve as bodyguards and can conduct operations. |
| **Counselor** | 20 | Appeals to what we have in common. |
| **Unifier** | 40 | Influential in nations with a sense of common purpose. |
| **Affluent** | 10 | Makes a good living. |
| **Prosperous** | 20 | Well-off and able to contribute meaningful funds to the cause. |
| **Wealthy** | 40 | Has access to a hefty bank account. |
| **Astronomer** |  | An expert in the study of Space Science. |
| **Chemist** |  | An expert in the study of Materials. |
| **Doctor** |  | An expert in the study of Life Science. |
| **Physicist** |  | An expert in the study of Energy. |
| **Computer Scientist** |  | An expert in a study of Information Science. |
| **Military Scientist** |  | An expert in the study of Military Science. |
| **Social Scientist** |  | An expert in the study of Social Science. |
| **Connected** | 20 | Able to use back channels to exert a measure of influence. |
| **Puppet Master** | 40 | Able to pull strings in many places without notice. |
| **Low Profile** |  | Skilled at evading detection. |
| **Undercover** |  | This person's public persona conceals someone who is able to infiltrate enemy space installations without fear of identification. |
| **Agitator** | 20 | Excels at gaining the support of those unhappy with their nation. |

* **9.4.2. Negative Traits Table:**

| Trait | Remove Cost | Description |
| :---- | :---- | :---- |
| **Inflexible** | 40 XP | Slow to learn new things. |
| **Declining** | Permanent | Age is taking its toll. |
| **Careless** | 20 XP | Someone who doesn't take personal security terribly seriously. |
| **Delinquent** | 300K Money | Refuses to honour outstanding debts, gaining a reputation for untrustworthiness... |
| **Anxious** | 20 XP | Not ready to die for the cause. |
| **Insecure** | 20 XP | Is troubled by personal failure. |
| **Loss Averse** | 20 XP | Haunted by defeat. |
| **Addict** | 40 XP | Addicted to an illicit substance and willing to go to any length to acquire it. |
| **Earthbound** | 20 XP | This person refuses to travel to space. |
| **Extorted** | 300K Money | Feels that they have been taken advantage of financially by our faction... |
| **Indebted** | 150K Money | Owes a very large sum of money to creditors, reducing their credibility. |
| **Indulgent** | 20 XP | Spends lots of money on personal gratification. |
| **Marked** | 50 XP, 1000 Money, 500 Influence, 100 ⚔️ Operations | This councilor has done something public, and terrible, and is the target of surveillance... |
| **Pariah** | Permanent | Strongly disliked in his or her home nation, this person fares better in foreign lands. |
| **Enemy of the State** | 20 Influence | Faces imprisonment or execution in his or her home nation. |
| **Non Grata** | 20 XP, 100 Money, 20 Influence | Faces imprisonment or execution in rivals of his or her home nation. |

* **9.4.3. Mixed Traits Table:**

| Trait | Effect / Mission | Description |
| :---- | :---- | :---- |
| **Criminal** | \+1 Monthly Money Income\-1 Security in nations where unrest is 1 or less*Can purchase Criminal Orgs* | Involved in illegal activities. |
| **Sociopath** | \+1 Persuasion\-3 Loyalty*Can purchase Sociopath Orgs* | Someone skilled at managing others in sole pursuit of his or her own satisfaction. |
| **Firebrand** | \+4 Monthly Influence Income\+2 Persuasion in nations where education is 6 or less\+2 Persuasion in nations where cohesion is 4 or less\-1 Persuasion in nations where education is at least 9\-3 Espionage when being detected by other councilors | Appeals to the anger and fear of an uncritical audience. |
| **Demagogue** | \+5 Monthly Influence Income \+3 Persuasion in nations where education is 6 or less \+3 Persuasion in nations where cohesion is 4 or less \-2 Persuasion in nations where education is at least 9 \-6 Espionage when being detected by other councilors | An influential rabble-rouser who plays to the basest instincts of the public. |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
| **Rich** | \+10 Monthly Money Income \+1 Monthly Influence Income \-1 Persuasion in nations where Inequality is 4 or less | Has vast sums to call on, but disliked in egalitarian nations. |
|  |  |  |
|  |  |  |
| **Billionaire** | \+40 Monthly Money Income \+2 Monthly Influence Income \-2 Persuasion in nations where Inequality is 4 or less \-1 Espionage when being detected by other councilors | Access to truly obscene amounts of money, to the point of unpopularity in nations that prize equality. |
|  |  |  |
|  |  |  |
|  |  |  |
| **Eminent** | \+6 Monthly Influence Income\-2 Espionage when being detected by other councilors | Influential among elites, but well-known enough to sometimes attract unwanted attention. |
|  |  |  |
| **Famous** | \+9 Monthly Influence Income | Broadly known among elites and the public. |
|  | \-4 Espionage when being detected by other councilors |  |
| **Megastar** | \+12 Monthly Influence Income | A person of global renown, whose very movements make the news worldwide. |
|  | \-8 Espionage when being detected by other councilors |  |
|  | *Prohibited: Go To Ground* |  |
| **Opinion Leader** | \+4 Monthly Influence Income | A respected commentator on public affairs, whose words reach many in free nations. |
|  | \+2 Persuasion in nations where Government is at least 6 |  |
|  | \-2 Espionage when being detected by other councilors |  |
| **Media Darling** | \+7 Monthly Influence Income | A popular speaker on media channels in free nations. |
|  | \+3 Persuasion in nations where Government is at least 6 |  |
|  | \-4 Espuasion when being detected by other councilors |  |
| **Elder Statesman** | \+10 Monthly Influence Income | A widely respected and influential member of the political elite. |
|  | \+4 Persuasion in nations where Government is at least 6 |  |
|  | \-4 Espionage when being detected by other councilors |  |
| **Averse** | \+1 Security | Flouts elite conventions, gaining influence among the masses at some personal risk. |
|  | *Cannot perform missions in nations with unrest of 6 or higher* |  |
| **Paranoid** | \+3 Security | Sees enemies everywhere. Only right some of the time. |
|  | \+2 Investigation |  |
|  | \+2 Espionage when being detected by other councilors |  |
|  | \-2 Persuasion |  |
|  | *Cannot perform missions in nations with unrest of 6 or higher* |  |
|  | *Prohibited: Inspire* |  |
| **Ethical** | \+1 Persuasion in nations where Inequality is 3.5 or less | A person of principle who believes not all means are justified by their end. |
|  | \-1 Loyalty per atrocity by faction |  |
|  | *Prohibited: Assassinate* |  |
| **Pacifist** | \+2 Persuasion in nations where Education is at least 9 | Personally refuses to take part in any violent action. |
|  | \-2 Loyalty per atrocity by faction |  |
|  | \-3 Command |  |
|  | *Prohibited: Assassinate, Assault Alien Asset, Assault Enemy Space Asset, Increase Unrest, Sabotage Facilities* |  |
| **Academic** | \+10 Monthly Research Income | Affiliated with a research university. |
|  | \-1 Command |  |
|  | *Granted: Advise* |  |
| **Awkward Genius** | \+2 Investigation | Poor at recognizing social cues and working with others but able to conduct scientific investigations with unparalleled focus. |
|  | \+3 Science |  |
|  | \-3 Persuasion |  |
|  | \-3 Command |  |
|  | *Prohibited: Inspire, Public Campaign* |  |
| **Brazen** | \+1 Persuasion in nations where Education is 7 or less | Flouts elite conventions, gaining influence among the masses at some personal risk. |
|  | \-1 Security |  |
| **Conspiracy Theorist** | \+1 Security | Sees connections between events that others will not. Occasionally right about them. |
|  | \+2 Investigation |  |
|  | \-1 Monthly Influence Income |  |
|  | \-1 Persuasion |  |
|  | *Granted: Investigate Alien Activity* |  |
| **Corrupt** | \+2 Espionage | Influential, but will steal from us. |
|  | \+3 Monthly Influence Income |  |
|  | \-4 Monthly Money Income |  |
|  | \-3 Loyalty |  |
| **Cynic** | \+1 Investigation | Difficult to fool, but expresses little hope for humanity's future. |
|  | \-1 Loyalty |  |
|  | *Prohibited: Inspire* |  |
| **Demanding** | \+2 Administration | Does not tolerate failure from anyone. |
|  | \+1 Command |  |
|  | \-1 Loyalty per critical failure on a mission |  |
| **Expert** | \+2 Monthly Influence Income | An oft-quoted speaker on topics in a certain realm of expertise. |
|  | \+5 Monthly Research Income |  |
|  | \+1 Persuasion |  |
|  | \+1 Science |  |
|  | \-1 Security |  |
|  | \-1 Espionage when being detected by other councilors |  |
|  | *Granted: Advise* |  |
| **Family Ties** | \+1 Persuasion in home nation | Feels a strong connection to their homeland and has family there. |
|  | \+1 Security in home nation |  |
|  | *Loses loyalty if home nation is hit with a Strategic Nuclear Barrage* |  |
| **Lone Wolf** | \+2 Espionage | Does not work well with others, but skilled at secretive activity. |
|  | \-1 Command |  |
|  | \-1 Administration |  |
|  | *Prohibited: Inspire* |  |
| **Martyr** | \+1 Persuasion | A violent death will draw millions to their cause. |
|  | \-1 Security |  |
|  | *If it dies violently owner receives Public Campaign effects in every nation* |  |
|  | *Granted: Inspire* |  |
| **National Hero** | \+4 Persuasion when in home nation | Well known and influential in his or her home nation. |
|  | \-1 Security when in home nation |  |
| **Oligarch** | \+3 Monthly Money Income | Has gained riches via political power; influential in nations with high inequality. |
|  | \+4 Monthly Influence Income |  |
|  | \+1 Persuasion in nations where Inequality is above 4 |  |
|  | \-1 Persuasion in nations where Inequality is below 4 |  |
| **Suspicious** | \+2 Espionage | Naturally inclined to distrust others. |
|  | \+2 Security |  |
|  | \+2 Investigation |  |
|  | \+2 Investigation when detecting other councilors |  |
|  | \+1 Espionage when being detected by other councilors |  |
|  | \-2 Apparent Loyalty |  |
|  | *Prohibited: Inspire* |  |
| **Technocrat** | \+2 Monthly Influence Income | Believes that social relations are simply an engineering problem. |
|  | \+3 Monthly Research Income |  |
|  | \+3 Administration |  |
|  | \+1 Science |  |
|  | \+5% Social Science Research |  |
|  | \-1 Persuasion in nations where education is 8 or less |  |
|  | *Granted: Advise* |  |
| **Furtive** | \+2 Espionage | A secretive and often negative personality. |
|  | \-1 Persuasion |  |
|  | \-1 Administration |  |
|  | 2 Apparent Loyalty |  |
|  | *Prohibited: Inspire* |  |
| **Inscrutable** | 12 Apparent Loyalty | Never seems to express a strong opinion. |
|  | *Prohibited: Inspire* |  |
| **Pollyanna** | 25 Apparent Loyalty | Always expresses a sunny outlook on events, regardless of their reality. |
| **Extremist** | \+3 Loyalty | Utterly devoted to the cause and holds those who aren't in low regard. |
|  | \+1 Investigation |  |
|  | \-1 Persuasion in nations where education is at least 8 |  |
|  | \+3 Apparent Loyalty |  |
| **Fanatic** | \+5 Loyalty | An absolute true believer who lacks an understanding of certain subtleties of dealing with the world. |
|  | \+2 Persuasion in nations where education is 6 or less |  |
|  | \-1 Investigation |  |
|  | \+5 Apparent Loyalty |  |

### **9.5. Profession Mission Access**

| Mission | Authorized Professions | Notes |
| :---- | :---- | :---- |
| **Public Campaign** | Activist, Celebrity, Diplomat, Evangelist, Governor, Journalist, Professor | Boosts public support for your faction. |
| **Control Nation** | Governor, Kingpin, Officer, Rebel | The core mission for taking control of a nation's CPs. |
| **Hostile Takeover** | Executive, Fixer, Hacker, Kingpin, Spy, Tycoon | Forcibly seizing control of an Org. |
| **Investigate** | Hacker, Inspector, Journalist, Local Agent, Spy | Uncovering information on rival Councillors, Orgs, or nations. |
| **Protect Target** | Captain, Fixer, Inspector, Officer, Operative | Defending friendly assets from hostile missions. |
| **Go to Hiding** | Any | Any Councillor can attempt to hide. |
| **Turn Councillor** | Kingpin, Spy, Fixer | A high-level espionage mission requiring specific skills. |
| **Manage Project** | Scientist, Professor, Agency Director, Executive | Accelerates your own faction's research. |
| **Investigate Alien Activity** | Scientist, Professor, Test Pilot | Contributes to global, high-risk research. |
| **Sabotage Project** | Operative, Rebel, Scientist | Disrupts an enemy faction's research. |
| **Steal Project** | Hacker, Spy, Tech Mogul | Steals research from a rival faction. |
| **Purchase Org** | Diplomat, Executive, Governor, Tycoon | Requires political and economic savvy. |
| **Launch Hab** | Scientist, Executive, Test Pilot, Agency Director | Requires high-tech and administrative skills. |
| **Go to Orbit** | Any | Any Councillor can travel to a hab. |
| Execute Transfer | Captain, Test Pilot, Scientist, Agency Director | Required to pilot spacecraft on complex trajectories. |

### **9.6. Organizations (Orgs) Table**

This table lists the Organizations available in the game.

| Org Name | Nation | Cost (💰/✨) | Resource Bonus | DC | Tier | Grants Mission |
| :---- | :---- | :---- | :---- | ----- | ----- | :---- |
| **\-- North America \--** |  |  |  |  |  |  |
| The Heritage Foundation | USA | 100 / 20 | \+3 ✨ Inf | 11 | 1 |  |
| RAND Corporation | USA | 120 / 15 | \+2 🔬 Res | 12 | 1 |  |
| United Launch Alliance | USA | 250 / 25 | \+5 🚀 Boost | 16 | 2 |  |
| Goldman Sachs | USA | 400 / 50 | \+15 💰 Money | 17 | 2 |  |
| SpaceX | USA | 300 / 30 | \+6 🚀 Boost | 17 | 2 |  |
| DARPA | USA | 350 / 40 | \+5 🔬 Res | 18 | 2 | Manage Project |
| NASA | USA | 500 / 75 | \+5 🚀 Boost, \+4 🔬 Res | 20 | 3 | Investigate Alien Activity |
| CIA | USA | 600 / 100 | \+8 ⚔️ Ops | 22 | 3 | Turn Councillor |
| **\-- Europe \--** |  |  |  |  |  |  |
| De Beers | UK | 150 / 10 | \+5 💰 Money | 12 | 1 |  |
| CERN | Switzerland | 200 / 30 | \+4 🔬 Res | 13 | 1 |  |
| The Hague | Netherlands | 200 / 50 | \+5 ✨ Inf | 16 | 2 |  |
| Interpol | France | 300 / 60 | \+4 ✨ Inf, \+2 ⚔️ Ops | 17 | 2 | Investigate Councillor |
| MI6 | UK | 450 / 70 | \+5 ⚔️ Ops | 18 | 2 | Investigate Councillor |
| European Space Agency | France | 500 / 75 | \+6 🚀 Boost, \+2 🔬 Res | 20 | 3 |  |
| **\-- East Asia \--** |  |  |  |  |  |  |
| Toyota | Japan | 180 / 10 | \+6 💰 Money | 12 | 1 |  |
| National Space Program | China | 400 / 50 | \+4 🚀 Boost | 18 | 2 |  |
| Samsung | South Korea | 300 / 20 | \+8 💰 Money, \+2 🔬 Res | 17 | 2 |  |
| Ministry of State Security | China | 500 / 80 | \+6 ⚔️ Ops | 20 | 3 | Go to Hiding |
| **\-- Russia & Central Asia \--** |  |  |  |  |  |  |
| Eurasian Development Bank | Russia | 200 / 20 | \+8 💰 Money | 13 | 1 |  |
| Roscosmos | Russia | 300 / 40 | \+3 🚀 Boost | 16 | 2 |  |
| Gazprom | Russia | 350 / 30 | \+12 💰 Money | 17 | 2 |  |
| **\-- Middle East & Africa \--** |  |  |  |  |  |  |
| Al-Jazeera | Qatar | 80 / 25 | \+2 ✨ Inf | 10 | 1 | Public Campaign |
| Mossad | Israel | 400 / 60 | \+6 ⚔️ Ops | 19 | 2 | Sabotage Project |
| **\-- South America \--** |  |  |  |  |  |  |
| Petrobras | Brazil | 150 / 10 | \+5 💰 Money | 12 | 1 |  |
| **\-- Global \--** |  |  |  |  |  |  |
| International Monetary Fund | N/A | 800 / 200 | \+20 💰 Money | 21 | 3 |  |
| United Nations | N/A | 600 / 300 | \+10 ✨ Inf | 22 | 3 |  |
| World Bank | N/A | 750 / 150 | \+18 💰 Money | 21 | 3 |  |
