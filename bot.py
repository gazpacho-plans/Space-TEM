import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from typing import Optional, Dict, Any
import asyncio

from dotenv import load_dotenv
from storage.character_repo import CharacterRepository

load_dotenv('token.env')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global variables for character creation flow
active_creations: Dict[int, Dict[str, Any]] = {}  # user_id -> creation_state
character_repo = CharacterRepository()

class CharacterCreationState:
    def __init__(self, user_id: int, character_name: str):
        self.user_id = user_id
        self.character_name = character_name
        self.faction = None
        self.profession = None
        self.step = "faction_selection"  # faction_selection, profession_selection, confirmation
        self.message = None  # Store the message for updating
        self.timeout_task = None

# Load game data
def load_game_data():
    """Load all game data from JSON files"""
    data = {}
    
    # Load factions
    with open('data/factions.json', 'r') as f:
        data['factions'] = json.load(f)
    
    # Load professions
    with open('data/professions.json', 'r') as f:
        data['professions'] = json.load(f)
    
    # Load traits
    with open('data/positive_traits.json', 'r') as f:
        data['positive_traits'] = json.load(f)
    
    with open('data/negative_traits.json', 'r') as f:
        data['negative_traits'] = json.load(f)
    
    with open('data/mixed_traits.json', 'r') as f:
        data['mixed_traits'] = json.load(f)
    
    return data

# Global game data
GAME_DATA = load_game_data()

# Core professions from GDD
CORE_PROFESSIONS = [
    "Diplomat",
    "Spy", 
    "Executive",
    "Activist",
    "Hacker",
    "Operative"
]

# Profession emojis
PROFESSION_EMOJIS = {
    "Diplomat": "🤝",
    "Spy": "👁️",
    "Executive": "👔",
    "Activist": "🗣️",
    "Hacker": "💻",
    "Operative": "💥"
}

# Attribute emojis
ATTRIBUTE_EMOJIS = {
    "Persuasion": "📢",
    "Investigation": "🔎",
    "Espionage": "🕶️",
    "Command": "🎖️",
    "Security": "🔐",
    "Science": "⚛️",
    "Administration": "🏢"
}

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="create_councillor", description="Create a new Councillor character")
async def create_councillor(interaction: discord.Interaction, name: str):
    """Start the character creation process"""
    user_id = interaction.user.id
    
    # Check if user already has an active creation
    if user_id in active_creations:
        await interaction.response.send_message(
            "You already have a character creation in progress. Please complete or cancel it first.",
            ephemeral=True
        )
        return
    
    # Check if name is valid (basic validation)
    if len(name.strip()) < 2 or len(name.strip()) > 50:
        await interaction.response.send_message(
            "Character name must be between 2 and 50 characters long.",
            ephemeral=True
        )
        return
    
    # Initialize creation state
    creation_state = CharacterCreationState(user_id, name.strip())
    active_creations[user_id] = creation_state
    
    # Create faction selection embed
    embed = create_faction_selection_embed()
    
    # Create faction selection view
    view = FactionSelectionView(creation_state)
    
    # Send the initial message
    response = await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    creation_state.message = response
    
    # Set up timeout
    creation_state.timeout_task = asyncio.create_task(creation_timeout(user_id))

def create_faction_selection_embed():
    """Create the faction selection embed"""
    embed = discord.Embed(
        title="Choose Your Faction",
        description="Select the faction your Councillor will belong to:",
        color=discord.Color.blue()
    )
    
    for faction in GAME_DATA['factions']:
        embed.add_field(
            name=faction['name'],
            value=faction['description'],
            inline=False
        )
    
    embed.set_footer(text="You have 5 minutes to make your selection")
    return embed

def create_profession_selection_embed(faction_name: str):
    """Create the profession selection embed"""
    embed = discord.Embed(
        title="Choose Your Profession",
        description=f"Faction: **{faction_name}**\n\nSelect your Councillor's profession:",
        color=discord.Color.green()
    )
    
    # Add only core profession options
    for prof_name in CORE_PROFESSIONS:
        prof_data = GAME_DATA['professions'][prof_name]
        missions_text = ", ".join(prof_data['missions'])  # Show all missions
        
        emoji = PROFESSION_EMOJIS.get(prof_name, "")
        embed.add_field(
            name=f"{emoji} {prof_name}",
            value=f"{prof_data['description']}\n**Available Missions:** {missions_text}",
            inline=False
        )
    
    embed.set_footer(text="You have 5 minutes to make your selection")
    return embed

def create_confirmation_embed(creation_state: CharacterCreationState):
    """Create the confirmation embed"""
    embed = discord.Embed(
        title="Confirm Character Creation",
        description="Review your character details:",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="Name", value=creation_state.character_name, inline=True)
    embed.add_field(name="Faction", value=creation_state.faction, inline=True)
    
    # Add profession with emoji
    prof_emoji = PROFESSION_EMOJIS.get(creation_state.profession, "")
    embed.add_field(name="Profession", value=f"{prof_emoji} {creation_state.profession}", inline=True)
    
    # Add profession attribute ranges
    profession_data = GAME_DATA['professions'][creation_state.profession]
    attr_ranges_text = ""
    
    for attr_name, attr_range in profession_data.items():
        if attr_name in ['description', 'missions', 'XP_Cost']:
            continue
        
        if isinstance(attr_range, list) and len(attr_range) == 2:
            min_val, max_val = attr_range
            emoji = ATTRIBUTE_EMOJIS.get(attr_name, "")
            attr_ranges_text += f"{emoji} **{attr_name}:** {min_val}-{max_val}\n"
    
    if attr_ranges_text:
        embed.add_field(name="Attribute Ranges", value=attr_ranges_text, inline=False)
    
    # Add available missions
    missions_text = ", ".join(profession_data['missions'])
    prof_emoji = PROFESSION_EMOJIS.get(creation_state.profession, "")
    embed.add_field(name=f"Available Missions ({prof_emoji} {creation_state.profession})", value=missions_text, inline=False)
    
    embed.set_footer(text="Click Create to confirm or Cancel to start over")
    return embed

class FactionSelectionView(discord.ui.View):
    def __init__(self, creation_state: CharacterCreationState):
        super().__init__(timeout=300)
        self.creation_state = creation_state
    
    @discord.ui.select(
        placeholder="Choose a faction...",
        options=[
            discord.SelectOption(label=faction['name'])
            for faction in GAME_DATA['factions']
        ]
    )
    async def faction_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return
        
        # Store selected faction
        self.creation_state.faction = select.values[0]
        self.creation_state.step = "profession_selection"
        
        # Create profession selection embed
        embed = create_profession_selection_embed(self.creation_state.faction)
        
        # Create profession selection view
        view = ProfessionSelectionView(self.creation_state)
        
        # Update the message
        await interaction.response.edit_message(embed=embed, view=view)

class ProfessionSelectionView(discord.ui.View):
    def __init__(self, creation_state: CharacterCreationState):
        super().__init__(timeout=300)
        self.creation_state = creation_state
    
    @discord.ui.select(
        placeholder="Choose a profession...",
        options=[
            discord.SelectOption(
                label=f"{PROFESSION_EMOJIS.get(prof_name, '')} {prof_name}", 
                value=prof_name
            )
            for prof_name in CORE_PROFESSIONS
        ]
    )
    async def profession_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return
        
        # Store selected profession
        self.creation_state.profession = select.values[0]
        self.creation_state.step = "confirmation"
        
        # Create confirmation embed
        embed = create_confirmation_embed(self.creation_state)
        
        # Create confirmation view
        view = ConfirmationView(self.creation_state)
        
        # Update the message
        await interaction.response.edit_message(embed=embed, view=view)

class ConfirmationView(discord.ui.View):
    def __init__(self, creation_state: CharacterCreationState):
        super().__init__(timeout=60)
        self.creation_state = creation_state
    
    @discord.ui.button(label="Create Character", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return
        
        # Generate character attributes and traits
        character = generate_character(self.creation_state)
        character['user_id'] = self.creation_state.user_id
        
        # Persist character
        try:
            saved_id = await character_repo.save_character(character)
        except Exception as e:
            await interaction.response.send_message(f"Failed to save character: {e}", ephemeral=True)
            return
        
        # Create character sheet embed
        embed = create_character_sheet_embed(character, saved_id)
        
        # Clean up creation state
        cleanup_creation_state(self.creation_state.user_id)
        
        # Send final character sheet
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.creation_state.user_id:
            await interaction.response.send_message("This is not your character creation.", ephemeral=True)
            return
        
        # Clean up creation state
        cleanup_creation_state(self.creation_state.user_id)
        
        await interaction.response.edit_message(
            content="Character creation cancelled.",
            embed=None,
            view=None
        )

def generate_character(creation_state: CharacterCreationState):
    """Generate character attributes and traits based on profession"""
    import random
    
    profession_data = GAME_DATA['professions'][creation_state.profession]
    
    # Generate attributes
    attributes = {}
    for attr_name, attr_range in profession_data.items():
        if attr_name in ['description', 'missions', 'XP_Cost']:
            continue
        
        if isinstance(attr_range, list) and len(attr_range) == 2:
            min_val, max_val = attr_range
            attributes[attr_name] = random.randint(min_val, max_val)
        else:
            attributes[attr_name] = attr_range
    
    # Generate traits
    traits = []
    
    # One random positive trait (0 XP cost)
    free_traits = [trait for trait in GAME_DATA['positive_traits'] if trait['xp_cost'] == 0]
    if free_traits:
        traits.append(random.choice(free_traits)['name'])
    
    # 20% chance for additional negative/mixed trait
    if random.random() < 0.2:
        all_traits = []
        for trait in GAME_DATA['negative_traits']:
            all_traits.append(trait['name'])
        for trait in GAME_DATA['mixed_traits']:
            all_traits.append(trait['name'])
        
        if all_traits:
            traits.append(random.choice(all_traits))
    
    # Calculate income
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
        'controlled_orgs': []
    }

def calculate_income(attributes: Dict[str, int], traits: list):
    """Calculate character's income based on attributes and traits"""
    income = {
        'money': 0,
        'influence': 0,
        'operations': 0,
        'research': 0,
        'boost': 0
    }
    
    # Base income from attributes (placeholder - adjust as needed)
    income['research'] = attributes.get('Science', 0)
    
    # Trait bonuses
    for trait_name in traits:
        # Check positive traits
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
        
        # Check mixed traits
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

def create_character_sheet_embed(character: Dict[str, Any], saved_id: Optional[int] = None):
    """Create the final character sheet embed"""
    embed = discord.Embed(
        title=f"Character Created: {character['name']}",
        description=f"**Faction:** {character['faction']}\n**Profession:** {character['profession']}",
        color=discord.Color.green()
    )
    
    # Attributes
    attr_text = ""
    for attr_name, attr_value in character['attributes'].items():
        emoji = ATTRIBUTE_EMOJIS.get(attr_name, "")
        attr_text += f"{emoji} **{attr_name}:** {attr_value}\n"
    embed.add_field(name="Attributes", value=attr_text, inline=True)
    
    # Traits
    if character['traits']:
        traits_text = "\n".join([f"• {trait}" for trait in character['traits']])
        embed.add_field(name="Traits", value=traits_text, inline=True)
    else:
        embed.add_field(name="Traits", value="None", inline=True)
    
    # Income
    income_text = ""
    for resource, amount in character['income'].items():
        if amount > 0:
            income_text += f"**{resource.title()}:** {amount}/month\n"
    if income_text:
        embed.add_field(name="Income", value=income_text, inline=False)
    
    # Available missions
    profession_data = GAME_DATA['professions'][character['profession']]
    missions_text = ", ".join(profession_data['missions'])
    prof_emoji = PROFESSION_EMOJIS.get(character['profession'], "")
    embed.add_field(name=f"Available Missions ({prof_emoji} {character['profession']})", value=missions_text, inline=False)
    
    if saved_id is not None:
        embed.set_footer(text=f"Character creation complete! ID: {saved_id}")
    else:
        embed.set_footer(text="Character creation complete!")
    return embed

def cleanup_creation_state(user_id: int):
    """Clean up character creation state"""
    if user_id in active_creations:
        creation_state = active_creations[user_id]
        if creation_state.timeout_task:
            creation_state.timeout_task.cancel()
        del active_creations[user_id]

async def creation_timeout(user_id: int):
    """Handle character creation timeout"""
    await asyncio.sleep(300)  # 300 second timeout (5 minutes)
    
    if user_id in active_creations:
        creation_state = active_creations[user_id]
        if creation_state.message:
            try:
                await creation_state.message.edit(
                    content="Character creation timed out. Please try again.",
                    embed=None,
                    view=None
                )
            except:
                pass  # Message might have been deleted
        
        cleanup_creation_state(user_id)

@bot.tree.command(name="cancel_creation", description="Cancel your active character creation")
async def cancel_creation(interaction: discord.Interaction):
    """Cancel active character creation"""
    user_id = interaction.user.id
    
    if user_id not in active_creations:
        await interaction.response.send_message("You don't have an active character creation.", ephemeral=True)
        return
    
    cleanup_creation_state(user_id)
    await interaction.response.send_message("Character creation cancelled.", ephemeral=True)

@bot.tree.command(name="my_character", description="View your most recently saved character")
async def my_character(interaction: discord.Interaction):
    user_id = interaction.user.id
    character = await character_repo.get_character_by_user(user_id)
    if character is None:
        await interaction.response.send_message("You have no saved characters.", ephemeral=True)
        return
    embed = create_character_sheet_embed(character)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="my_characters", description="List all your saved characters")
async def my_characters(interaction: discord.Interaction):
    user_id = interaction.user.id
    characters = await character_repo.list_characters_by_user(user_id)
    if not characters:
        await interaction.response.send_message("You have no saved characters.", ephemeral=True)
        return
    embed = discord.Embed(title="Your Saved Characters", color=discord.Color.blurple())
    for ch in characters:
        embed.add_field(
            name=f"ID {ch['id']}: {ch['name']}",
            value=f"Faction: {ch['faction']} | Profession: {ch['profession']} | XP: {ch['xp']}",
            inline=False
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="delete_character", description="Delete one of your saved characters by ID")
@app_commands.describe(character_id="The ID of the character to delete (see /my_characters)")
async def delete_character(interaction: discord.Interaction, character_id: int):
    user_id = interaction.user.id
    try:
        deleted = await character_repo.delete_character(user_id, character_id)
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete character: {e}", ephemeral=True)
        return
    if deleted:
        await interaction.response.send_message(f"Deleted character ID {character_id}.", ephemeral=True)
    else:
        await interaction.response.send_message("Character not found or not owned by you.", ephemeral=True)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    print(f"Command error: {error}")
    await ctx.send(f"An error occurred: {error}")

# Run the bot
if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Please set the DISCORD_TOKEN environment variable")
        exit(1)
    
    bot.run(token)
