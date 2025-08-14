# Space-TEM Discord Bot

This Discord bot implements the character creation system for the Space-TEM game and persists created Councillors to SQLite.

For overall project overview and Quickstart, see [README.md](README.md). This document focuses on bot behavior and internals.

## Setup

See the Quickstart in [README.md](README.md) for installation, environment configuration, inviting the bot, and running it. This document intentionally avoids duplicating those steps.

## Commands

- **User commands**
  - `/create_councillor name:<text>`: Start guided character creation
  - `/cancel_creation`: Cancel your in-progress creation
  - `/my_councillor`: Show your most recently saved Councillor

- **Admin commands** (require Manage Server/Guild permission)
  - `/list [user] [limit]`: List saved Councillors (optionally filter by `user`, default `limit` up to 50)
  - `/delete_councillor character_id:<number>`: Delete a Councillor by ID

## Character Creation Flow

1. Name validation (2–50 chars)
2. Faction selection (interactive menu with descriptions)
3. Profession selection (6 core professions with attribute ranges and missions)
4. Attribute generation (random within profession ranges)
5. Trait assignment (one free positive trait; 20% chance of an extra negative/mixed trait)
6. Income calculation (based on attributes and trait effects)
7. Final character sheet embed and persistence to the database

## Features

- Interactive UI with select menus and buttons (ephemeral to the user)
- Timeouts: 5 minutes on selection steps, 60 seconds on confirmation, background 5-minute inactivity cleanup
- Per-user state tracking; safe cleanup on completion/cancel/timeout
- SQLite persistence at `data/db/characters.db`
- JSON-backed game data loaded at startup from `data/static/`
- Admin moderation tools to list and delete saved characters

## Architecture

- `bot.py` loads extensions and manages slash command sync (supports guild-scoped sync via `DISCORD_GUILD_ID` and optional clearing of globals via `CLEAR_GLOBAL_COMMANDS`).
- `cogs/character_creation.py` exposes `/create_councillor`, `/cancel_creation`, `/my_councillor`, implements UI and generation logic.
- `cogs/admin.py` exposes `/list` and `/delete_councillor` for server admins.
- `storage/character_repo.py` provides async SQLite persistence using a thread pool.
- Game data is loaded once at import into module-level `GAME_DATA` for static UI options.

 

## Development Notes

- Python 3.10+ (uses modern union types like `int | None`)
- discord.py 2.3.0+ with `app_commands` for slash commands
- Interactions are ephemeral to the user
- Do not commit real tokens. Keep `token.env` out of version control
