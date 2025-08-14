import os
import logging
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from utils.logging import setup_logging, get_logger, ctx_from_interaction


load_dotenv('token.env')
setup_logging()
logger = get_logger("space_tem.bot")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")
    try:
        guild_id = os.getenv('DISCORD_GUILD_ID')
        clear_globals = os.getenv('CLEAR_GLOBAL_COMMANDS') in {"1", "true", "True"}
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            # Copy current global command definitions to the guild for instant availability
            bot.tree.copy_global_to(guild=guild)
            guild_synced = await bot.tree.sync(guild=guild)
            logger.info("Synced %d guild command(s) to guild %s", len(guild_synced), guild_id)
            if clear_globals:
                before = len(await bot.tree.sync())
                logger.info("Global commands before clear: %d", before)
                bot.tree.clear_commands(guild=None)
                after_synced = await bot.tree.sync()
                logger.info("Cleared global commands, now %d global command(s)", len(after_synced))
        else:
            synced = await bot.tree.sync()
            logger.info("Synced %d global command(s)", len(synced))
    except Exception as e:
        logger.exception("Failed to sync commands")


async def load_extensions():
    try:
        await bot.load_extension('cogs.character_creation')
        logger.info('Loaded extension: cogs.character_creation')
        await bot.load_extension('cogs.admin')
        logger.info('Loaded extension: cogs.admin')
    except Exception as e:
        logger.exception('Failed to load extensions')


async def main():
    await load_extensions()
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('Please set the DISCORD_TOKEN environment variable')
        raise SystemExit(1)
    await bot.start(token)


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    logger = get_logger("space_tem.app")
    logger.exception("app_command_error", extra={"ctx": ctx_from_interaction(interaction)})
    try:
        msg = "Something went wrong while running that command."
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_error(event_method: str, *args, **kwargs):
    elogger = get_logger("space_tem.events")
    try:
        # Try to enrich with interaction context if present in args
        ctx = {"event": event_method}
        for arg in args:
            if isinstance(arg, discord.Interaction):
                ctx.update(ctx_from_interaction(arg))
                break
        elogger.exception("unhandled_event_error", extra={"ctx": ctx})
    except Exception:
        elogger.exception("unhandled_event_error")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
