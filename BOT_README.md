# Space-TEM Discord Bot

This Discord bot implements the character creation system for the Space-TEM game.


## Run the Bot

```bash
python bot.py
```

## Commands

### `/create_councillor [name]`
Starts the character creation process. The bot will guide you through:
1. **Faction Selection**: Choose from The Academy, Humanity First, The Protectorate, or The Initiative
2. **Profession Selection**: Choose from 22 different professions with unique attributes and missions
3. **Confirmation**: Review your choices and create the character

### `/cancel_creation`
Cancels your active character creation process.

## Character Creation Flow

The character creation process follows the specification from `docs/character_creation.md`:

1. **Name Validation**: Character names must be 2-50 characters
2. **Faction Selection**: Interactive dropdown with faction descriptions
3. **Profession Selection**: Interactive dropdown showing profession details and available missions
4. **Attribute Generation**: Random attributes within profession ranges
5. **Trait Assignment**: One free positive trait + 20% chance for additional negative/mixed trait
6. **Income Calculation**: Based on attributes and traits
7. **Character Sheet**: Final display with all character information

## Features

- **Interactive UI**: Uses Discord's select menus and buttons
- **Timeout Handling**: 60-second timeout for each step
- **State Management**: Tracks active character creations per user
- **Data Integration**: Loads game data from JSON files
- **Error Handling**: Graceful error handling and user feedback

## File Structure

- `bot.py`: Main bot file with all Discord integration
- `data/`: Game data files (factions, professions, traits)
- `requirements.txt`: Python dependencies
- `BOT_README.md`: This file

## Development Notes

- The bot uses Discord.py 2.3.0+ for slash commands
- Character creation is ephemeral (only visible to the user)
- All game data is loaded from JSON files at startup
- The bot supports multiple concurrent character creations
- Timeout tasks are properly cleaned up to prevent memory leaks
