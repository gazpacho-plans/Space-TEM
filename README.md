# Space-TEM



## Quickstart

1. Python 3.10+
2. Install deps: `pip install -r requirements.txt`
3. Create a bot in the Discord Developer Portal and copy the token
4. Create `token.env` in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token_here
# Optional: sync commands to a single guild for instant availability
DISCORD_GUILD_ID=your_guild_id_here
# Optional: clear global commands after guild sync (1/true to enable)
CLEAR_GLOBAL_COMMANDS=1
```

5. Invite the bot (scopes: `bot`, `applications.commands`; perms: Send Messages, Embed Links, Read Message History)
6. Run: `python bot.py`

## Bot usage

- For full bot setup, commands, character flow, and features, see [BOT_README.md](BOT_README.md).

## Data & Persistence

- Game data lives in `data/static/` as JSON: `factions.json`, `professions.json`, `positive_traits.json`, `negative_traits.json`, `mixed_traits.json`
- Characters are saved to `data/db/characters.db` via `storage/character_repo.py`

## Architecture

- `bot.py` loads extensions and manages slash command sync (supports guild-scoped sync via `DISCORD_GUILD_ID` and optional clearing of globals via `CLEAR_GLOBAL_COMMANDS`).
- `cogs/character_creation.py`: core user-facing flow and UI
- `cogs/admin.py`: moderation tools for listing/deleting characters
- `storage/character_repo.py`: async SQLite access via thread pool

## Repo Layout

- `bot.py`
- `cogs/`
  - `__init__.py`
  - `character_creation.py`
  - `admin.py`
- `storage/`
  - `character_repo.py`
- `data/`
  - `db/`
    - `characters.db` (created on first run)
  - `static/`
    - `factions.json`
    - `professions.json`
    - `positive_traits.json`
    - `negative_traits.json`
    - `mixed_traits.json`
- `docs/`
  - `character_creation.md`
  - `mega_doc.md`
  - `nation_authoring_spec.md`
  - `nations_and_control_points.md`
- `requirements.txt`
- `BOT_README.md`

## Further Reading

- Detailed bot guide: [BOT_README.md](BOT_README.md)
- Game design docs: [docs/](docs/)
