# Sample Bot Output

This file shows what the Discord bot's character creation flow will look like.

## Step 1: Faction Selection

The bot will send an embed like this:

```
┌─────────────────────────────────────────────────────────┐
│ Choose Your Faction                                     │
│ Select the faction your Councillor will belong to:      │
├─────────────────────────────────────────────────────────┤
│ The Academy                                             │
│ Convince the aliens that we are equal.                  │
│                                                         │
│ Humanity First                                          │
│ Eradicate the aliens and all who support them.          │
│                                                         │
│ The Protectorate                                        │
│ Protect humanity by appeasing the aliens.               │
│                                                         │
│ The Initiative                                          │
│ Exploit the alien arrival to gain power.                │
├─────────────────────────────────────────────────────────┤
│ [Choose a faction... ▼]                                 │
│ You have 60 seconds to make your selection              │
└─────────────────────────────────────────────────────────┘
```

## Step 2: Profession Selection

After selecting a faction, the bot will show:

```
┌─────────────────────────────────────────────────────────┐
│ Choose Your Profession                                  │
│ Faction: The Academy                                    │
│                                                         │
│ Select your Councillor's profession:                    │
├─────────────────────────────────────────────────────────┤
│ Spy                                                     │
│ A covert operative skilled in gathering secrets and     │
│ subterfuge.                                             │
│ Missions: Hostile Takeover, Investigate, Steal Project  │
│                                                         │
│ Diplomat                                                │
│ A skilled negotiator, fostering alliances and acquiring │
│ influence.                                              │
│ Missions: Public Campaign, Purchase Org, Stabilize...   │
│                                                         │
│ [and 20 more professions...]                            │
├─────────────────────────────────────────────────────────┤
│ [Choose a profession... ▼]                              │
│ You have 60 seconds to make your selection              │
└─────────────────────────────────────────────────────────┘
```

## Step 3: Confirmation

After selecting a profession:

```
┌─────────────────────────────────────────────────────────┐
│ Confirm Character Creation                              │
│ Review your character details:                          │
├─────────────────────────────────────────────────────────┤
│ Name: John Smith                                        │
│ Faction: The Academy                                    │
│ Profession: Spy                                         │
├─────────────────────────────────────────────────────────┤
│ [Create Character] [Cancel]                             │
│ Click Create to confirm or Cancel to start over         │
└─────────────────────────────────────────────────────────┘
```

## Step 4: Final Character Sheet

After confirming:

```
┌─────────────────────────────────────────────────────────┐
│ Character Created: John Smith                           │
│ Faction: The Academy                                    │
│ Profession: Spy                                         │
├─────────────────────────────────────────────────────────┤
│ Attributes                    │ Traits                   │
│ Persuasion: 4                │ • Beloved                │
│ Investigation: 5             │ • Paranoid               │
│ Espionage: 6                 │                          │
│ Command: 2                   │                          │
│ Administration: 1            │                          │
│ Science: 0                   │                          │
│ Security: 4                  │                          │
├─────────────────────────────────────────────────────────┤
│ Income:                                                │
│ Research: 0/month                                        │
├─────────────────────────────────────────────────────────┤
│ Available Missions:                                     │
│ Hostile Takeover, Investigate, Steal Project, Turn      │
│ Councillor, Increase Unrest, Coup Nation               │
├─────────────────────────────────────────────────────────┤
│ Character creation complete!                            │
└─────────────────────────────────────────────────────────┘
```

## Features

- **Interactive Dropdowns**: Users can select from lists using Discord's select menus
- **Ephemeral Messages**: All character creation messages are private to the user
- **Timeout Handling**: Each step has a 60-second timeout
- **State Management**: The bot tracks active character creations per user
- **Rich Embeds**: Beautiful formatting with colors and structured information
- **Error Handling**: Graceful error messages and validation

## Commands Available

- `/create_councillor [name]` - Start character creation
- `/cancel_creation` - Cancel active character creation

The bot will automatically sync these slash commands with Discord when it starts up.
