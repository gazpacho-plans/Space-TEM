import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from storage.character_repo import CharacterRepository
from utils.logging import get_logger, ctx_from_interaction, with_command_logging


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repo = CharacterRepository()
        self.logger = get_logger(__name__)

    def cog_unload(self) -> None:
        self.repo.close()

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="list", description="Admin: List saved Councillors (optionally filter by user)")
    @with_command_logging
    async def list_councillors(self, interaction: discord.Interaction, user: Optional[discord.User] = None, limit: Optional[int] = 20):
        try:
            if user is not None:
                characters = await self.repo.list_characters_by_user(user.id)
            else:
                safe_limit = 1 if (limit is None or limit <= 0) else min(limit, 50)
                characters = await self.repo.list_all_characters(limit=safe_limit)
        except Exception as exc:
            self.logger.exception("Failed to list characters", extra={"ctx": ctx_from_interaction(interaction)})
            await interaction.response.send_message(f"Failed to list characters: {exc}", ephemeral=True)
            return

        if not characters:
            await interaction.response.send_message("No saved Councillors found.", ephemeral=True)
            return

        lines = []
        for ch in characters:
            owner = f"<@{ch['user_id']}>"
            lines.append(f"ID {ch['id']}: {ch['name']} — {ch['faction']} / {ch['profession']} (owner {owner})")

        output = "\n".join(lines)
        if len(output) > 1800:
            output = output[:1797] + "..."

        await interaction.response.send_message(output, ephemeral=True)

    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.command(name="delete_councillor", description="Admin: Delete a Councillor by ID")
    @with_command_logging
    async def delete_councillor(self, interaction: discord.Interaction, character_id: int):
        try:
            ok = await self.repo.delete_character_by_id(character_id)
        except Exception as exc:
            self.logger.exception("Failed to delete character", extra={"ctx": ctx_from_interaction(interaction)})
            await interaction.response.send_message(f"Failed to delete character: {exc}", ephemeral=True)
            return

        if ok:
            await interaction.response.send_message(f"Deleted Councillor ID {character_id}.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No Councillor found with ID {character_id}.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))


