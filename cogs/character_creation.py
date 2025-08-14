import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
from typing import Optional, Dict, Any
from storage.character_repo import CharacterRepository


# -----------------------------
# Game Data Loading
# -----------------------------
def load_game_data() -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    with open('data/static/factions.json', 'r') as f:
        data['factions'] = json.load(f)

    with open('data/static/professions.json', 'r') as f:
        data['professions'] = json.load(f)

    with open('data/static/positive_traits.json', 'r') as f:
        data['positive_traits'] = json.load(f)

    with open('data/static/negative_traits.json', 'r') as f:
        data['negative_traits'] = json.load(f)

    with open('data/static/mixed_traits.json', 'r') as f:
        data['mixed_traits'] = json.load(f)

    return data


# Load once at module import for static UI options
GAME_DATA: Dict[str, Any] = load_game_data()


# -----------------------------
# Constants
# -----------------------------
CORE_PROFESSIONS = [
    "Diplomat",
    "Spy",
    "Executive",
    "Activist",
    "Hacker",
    "Operative",
]

PROFESSION_EMOJIS = {
    "Diplomat": "🤝",
    "Spy": "👁️",
    "Executive": "👔",
    "Activist": "🗣️",
    "Hacker": "💻",
    "Operative": "💥",
}

ATTRIBUTE_EMOJIS = {
    "Persuasion": "📢",
    "Investigation": "🔎",
    "Espionage": "🕶️",
    "Command": "🎖️",
    "Security": "🔐",
    "Science": "⚛️",
    "Administration": "🏢",
}


# -----------------------------
# State
# -----------------------------
class CharacterCreationState:
    def __init__(self, user_id: int, character_name: str):
        self.user_id: int = user_id
        self.character_name: str = character_name
        self.faction: Optional[str] = None
        self.profession: Optional[str] = None
        self.step: str = "faction_selection"  # faction_selection, profession_selection, confirmation
        self.message: Optional[discord.Message] = None
        self.timeout_task: Optional[asyncio.Task] = None


# -----------------------------
# Embeds
# -----------------------------
def create_faction_selection_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Choose Your Faction",
        description="Select the faction your Councillor will belong to:",
        color=discord.Color.blue(),
    )

    for faction in GAME_DATA['factions']:
        embed.add_field(name=faction['name'], value=faction['description'], inline=False)

    embed.set_footer(text="You have 5 minutes to make your selection")
    return embed


def create_profession_selection_embed(faction_name: str) -> discord.Embed:
    embed = discord.Embed(
        title="Choose Your Profession",
        description=f"Faction: **{faction_name}**\n\nSelect your Councillor's profession:",
        color=discord.Color.green(),
    )

    for prof_name in CORE_PROFESSIONS:
        prof_data = GAME_DATA['professions'][prof_name]
        missions_text = ", ".join(prof_data['missions'])
        emoji = PROFESSION_EMOJIS.get(prof_name, "")
        embed.add_field(
            name=f"{emoji} {prof_name}",
            value=f"{prof_data['description']}\n**Available Missions:** {missions_text}",
            inline=False,
        )

    embed.set_footer(text="You have 5 minutes to make your selection")
    return embed


def create_confirmation_embed(creation_state: 'CharacterCreationState') -> discord.Embed:
    embed = discord.Embed(
        title="Confirm Character Creation",
        description="Review your character details:",
        color=discord.Color.gold(),
    )

    embed.add_field(name="Name", value=creation_state.character_name, inline=True)
    embed.add_field(name="Faction", value=creation_state.faction or "-", inline=True)

    prof_emoji = PROFESSION_EMOJIS.get(creation_state.profession or "", "")
    embed.add_field(name="Profession", value=f"{prof_emoji} {creation_state.profession}", inline=True)

    profession_data = GAME_DATA['professions'][creation_state.profession]  # type: ignore[index]
    attr_ranges_text = ""
    for attr_name, attr_range in profession_data.items():
        if attr_name in ['description', 'missions', 'XP_Cost']:
            continue
        if isinstance(attr_range, list) and len(attr_range) == 2:
            min_val, max_val = attr_range
            attr_emoji = ATTRIBUTE_EMOJIS.get(attr_name, "")
            attr_ranges_text += f"{attr_emoji} **{attr_name}:** {min_val}-{max_val}\n"
    if attr_ranges_text:
        embed.add_field(name="Attribute Ranges", value=attr_ranges_text, inline=False)

    missions_text = ", ".join(profession_data['missions'])
    embed.add_field(
        name=f"Available Missions ({prof_emoji} {creation_state.profession})",
        value=missions_text,
        inline=False,
    )

    embed.set_footer(text="Click Create to confirm or Cancel to start over")
    return embed


def create_character_sheet_embed(character: Dict[str, Any]) -> discord.Embed:
    embed = discord.Embed(
        title=f"Character Created: {character['name']}",
        description=f"**Faction:** {character['faction']}\n**Profession:** {character['profession']}",
        color=discord.Color.green(),
    )

    attr_text = ""
    for attr_name, attr_value in character['attributes'].items():
        attr_emoji = ATTRIBUTE_EMOJIS.get(attr_name, "")
        attr_text += f"{attr_emoji} **{attr_name}:** {attr_value}\n"
    embed.add_field(name="Attributes", value=attr_text, inline=True)

    if character['traits']:
        traits_text = "\n".join([f"• {trait}" for trait in character['traits']])
        embed.add_field(name="Traits", value=traits_text, inline=True)
    else:
        embed.add_field(name="Traits", value="None", inline=True)

    income_text = ""
    for resource, amount in character['income'].items():
        if amount > 0:
            income_text += f"**{resource.title()}:** {amount}/month\n"
    if income_text:
        embed.add_field(name="Income", value=income_text, inline=False)

    profession_data = GAME_DATA['professions'][character['profession']]
    missions_text = ", ".join(profession_data['missions'])
    prof_emoji = PROFESSION_EMOJIS.get(character['profession'], "")
    embed.add_field(
        name=f"Available Missions ({prof_emoji} {character['profession']})",
        value=missions_text,
        inline=False,
    )

    embed.set_footer(text="Character creation complete!")
    return embed


# -----------------------------
# Character Generation Logic
# -----------------------------
def generate_character(creation_state: 'CharacterCreationState') -> Dict[str, Any]:
    import random

    profession_data = GAME_DATA['professions'][creation_state.profession]  # type: ignore[index]

    attributes: Dict[str, int] = {}
    for attr_name, attr_range in profession_data.items():
        if attr_name in ['description', 'missions', 'XP_Cost']:
            continue
        if isinstance(attr_range, list) and len(attr_range) == 2:
            min_val, max_val = attr_range
            attributes[attr_name] = random.randint(min_val, max_val)
        else:
            attributes[attr_name] = attr_range  # type: ignore[assignment]

    traits = []
    free_traits = [trait for trait in GAME_DATA['positive_traits'] if trait['xp_cost'] == 0]
    if free_traits:
        traits.append(random.choice(free_traits)['name'])

    if random.random() < 0.2:
        all_traits = (
            [trait['name'] for trait in GAME_DATA['negative_traits']] +
            [trait['name'] for trait in GAME_DATA['mixed_traits']]
        )
        if all_traits:
            traits.append(random.choice(all_traits))

    income = calculate_income(attributes, traits)

    return {
        'name': creation_state.character_name,
        'faction': creation_state.faction,
        'profession': creation_state.profession,
        'attributes': attributes,
        'traits': traits,
        'income': income,
        'xp': 0,
        'location': 'Earth',
        'controlled_orgs': [],
    }


def calculate_income(attributes: Dict[str, int], traits: list) -> Dict[str, int]:
    income = {
        'money': 0,
        'influence': 0,
        'operations': 0,
        'research': 0,
        'boost': 0,
    }

    income['research'] = attributes.get('Science', 0)

    for trait_name in traits:
        for trait in GAME_DATA['positive_traits']:
            if trait['name'] == trait_name:
                effects = trait.get('effects', {})
                for effect_type, effect_data in effects.items():
                    if effect_type == 'monthly_money_income':
                        income['money'] += effect_data
                    elif effect_type == 'monthly_influence_income':
                        income['influence'] += effect_data
                    elif effect_type == 'monthly_research_income':
                        income['research'] += effect_data
                break

        for trait in GAME_DATA['mixed_traits']:
            if trait['name'] == trait_name:
                effects = trait.get('effects', {})
                for effect_type, effect_data in effects.items():
                    if effect_type == 'monthly_money_income':
                        income['money'] += effect_data
                    elif effect_type == 'monthly_influence_income':
                        income['influence'] += effect_data
                    elif effect_type == 'monthly_research_income':
                        income['research'] += effect_data
                break

    return income


# -----------------------------
# Views
# -----------------------------
class FactionSelectionView(discord.ui.View):
    def __init__(self, cog: 'CharacterCreation', creation_state: 'CharacterCreationState'):
        super().__init__(timeout=300)
        self.cog = cog
        self.creation_state = creation_state

    @discord.ui.select(
        placeholder="Choose a faction...",
        options=[discord.SelectOption(label=faction['name']) for faction in GAME_DATA['factions']],
    )
    async def faction_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return

        try:
            self.creation_state.faction = select.values[0]
            self.creation_state.step = "profession_selection"

            embed = create_profession_selection_embed(self.creation_state.faction)
            view = ProfessionSelectionView(self.cog, self.creation_state)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as exc:
            await interaction.response.send_message(f"Error handling selection: {exc}", ephemeral=True)


class ProfessionSelectionView(discord.ui.View):
    def __init__(self, cog: 'CharacterCreation', creation_state: 'CharacterCreationState'):
        super().__init__(timeout=300)
        self.cog = cog
        self.creation_state = creation_state

    @discord.ui.select(
        placeholder="Choose a profession...",
        options=[
            discord.SelectOption(
                label=f"{PROFESSION_EMOJIS.get(prof_name, '')} {prof_name}", value=prof_name
            )
            for prof_name in CORE_PROFESSIONS
        ],
    )
    async def profession_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return

        try:
            self.creation_state.profession = select.values[0]
            self.creation_state.step = "confirmation"

            embed = create_confirmation_embed(self.creation_state)
            view = ConfirmationView(self.cog, self.creation_state)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as exc:
            await interaction.response.send_message(f"Error handling selection: {exc}", ephemeral=True)


class ConfirmationView(discord.ui.View):
    def __init__(self, cog: 'CharacterCreation', creation_state: 'CharacterCreationState'):
        super().__init__(timeout=60)
        self.cog = cog
        self.creation_state = creation_state

    @discord.ui.button(label="Create Character", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return

        character = generate_character(self.creation_state)
        character["user_id"] = interaction.user.id

        try:
            character_id = await self.cog.repo.save_character(character)
            embed = create_character_sheet_embed(character)
            embed.set_footer(text=f"Character creation complete! Saved as ID {character_id}")
            cleanup_creation_state(self.cog, self.creation_state.user_id)
            await interaction.response.edit_message(embed=embed, view=None)
        except Exception as exc:
            cleanup_creation_state(self.cog, self.creation_state.user_id)
            await interaction.response.edit_message(content=f"Failed to save character: {exc}", embed=None, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return

        cleanup_creation_state(self.cog, self.creation_state.user_id)
        await interaction.response.edit_message(content="Character creation cancelled.", embed=None, view=None)


# -----------------------------
# Cleanup/Timeout Utilities
# -----------------------------
def cleanup_creation_state(cog: 'CharacterCreation', user_id: int) -> None:
    if user_id in cog.active_creations:
        creation_state = cog.active_creations[user_id]
        if creation_state.timeout_task:
            creation_state.timeout_task.cancel()
        del cog.active_creations[user_id]


async def creation_timeout(cog: 'CharacterCreation', user_id: int) -> None:
    await asyncio.sleep(300)
    if user_id in cog.active_creations:
        creation_state = cog.active_creations[user_id]
        if creation_state.message:
            try:
                await creation_state.message.edit(
                    content="Character creation timed out. Please try again.",
                    embed=None,
                    view=None,
                )
            except Exception:
                pass
        cleanup_creation_state(cog, user_id)


# -----------------------------
# Cog
# -----------------------------
class CharacterCreation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_creations: Dict[int, CharacterCreationState] = {}
        self.repo = CharacterRepository()

    def cog_unload(self) -> None:
        # Best-effort cleanup of background executor
        self.repo.close()

    @app_commands.command(name="create_councillor", description="Create a new Councillor character")
    async def create_councillor(self, interaction: discord.Interaction, name: str):
        user_id = interaction.user.id

        if user_id in self.active_creations:
            await interaction.response.send_message(
                "You already have a character creation in progress. Please complete or cancel it first.",
                ephemeral=True,
            )
            return

        if len(name.strip()) < 2 or len(name.strip()) > 50:
            await interaction.response.send_message(
                "Character name must be between 2 and 50 characters long.",
                ephemeral=True,
            )
            return

        creation_state = CharacterCreationState(user_id, name.strip())
        self.active_creations[user_id] = creation_state

        embed = create_faction_selection_embed()
        view = FactionSelectionView(self, creation_state)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        try:
            creation_state.message = await interaction.original_response()
        except Exception:
            creation_state.message = None

        creation_state.timeout_task = asyncio.create_task(creation_timeout(self, user_id))

    @app_commands.command(name="cancel_creation", description="Cancel your active character creation")
    async def cancel_creation(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id not in self.active_creations:
            await interaction.response.send_message("You don't have an active character creation.", ephemeral=True)
            return
        cleanup_creation_state(self, user_id)
        await interaction.response.send_message("Character creation cancelled.", ephemeral=True)

    @app_commands.command(name="my_councillor", description="Show your most recently saved Councillor")
    async def my_councillor(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        try:
            character = await self.repo.get_character_by_user(user_id)
        except Exception as exc:
            await interaction.response.send_message(f"Failed to load character: {exc}", ephemeral=True)
            return

        if not character:
            await interaction.response.send_message(
                "You don't have a saved Councillor yet. Use /create_councillor to create one.",
                ephemeral=True,
            )
            return

        embed = create_character_sheet_embed(character)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterCreation(bot))
