import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv('token.env')


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    try:
        guild_id = os.getenv('DISCORD_GUILD_ID')
        clear_globals = os.getenv('CLEAR_GLOBAL_COMMANDS') in {"1", "true", "True"}
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            # Copy current global command definitions to the guild for instant availability
            bot.tree.copy_global_to(guild=guild)
            guild_synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(guild_synced)} guild command(s) to guild {guild_id}")
            if clear_globals:
                before = len(await bot.tree.sync())
                print(f"Global commands before clear: {before}")
                bot.tree.clear_commands(guild=None)
                after_synced = await bot.tree.sync()
                print(f"Cleared global commands, now {len(after_synced)} global command(s)")
        else:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} global command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def load_extensions():
    try:
        await bot.load_extension('cogs.character_creation')
        print('Loaded extension: cogs.character_creation')
        await bot.load_extension('cogs.admin')
        print('Loaded extension: cogs.admin')
    except Exception as e:
        print(f'Failed to load extensions: {e}')


async def main():
    await load_extensions()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('Please set the DISCORD_TOKEN environment variable')
        raise SystemExit(1)
    await bot.start(token)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
