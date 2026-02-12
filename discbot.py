import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Inventory file path
INVENTORY_FILE = "inventory.json"

# Load inventory from JSON file
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open('inventory.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Create default structure if file doesn't exist
        default_inventory = {   
            "streaming": [],
            "gaming": [],
            "vpn": [],
            "accounts": [],
            "codes": [],
            "outofstock": []
        }
        save_inventory(default_inventory)
        return default_inventory

# Save inventory to JSON file
def save_inventory(inventory):
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=4)

# Create embed for displaying items
def create_item_embed(category, items):
    # Emoji mapping for categories
    emoji_map = {
        "streaming": "📺",
        "gaming": "🎮",
        "vpn": "🔒",
        "accounts": "👤",
        "codes": "🎟️",
        "outofstock": "❌"
    }
    
    emoji = emoji_map.get(category, "📦")
    
    embed = discord.Embed(
        title=f"{emoji} {category.upper().replace('_', ' ')}",
        description=f"Available {category} items",
        color=discord.Color.blue() if category != "outofstock" else discord.Color.red()
    )
    
    if not items:
        embed.add_field(
            name="No items available",
            value="Check back later!",
            inline=False
        )
    else:
        for idx, item in enumerate(items, 1):
            price_display = f"${item['price']}" if item['price'] > 0 else "Price TBA"
            embed.add_field(
                name=f"#{idx} - {item['name']}",
                value=f"💰 {price_display}",
                inline=True
            )
    
    embed.set_footer(text=f"Total items: {len(items)}")
    return embed

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# --- VIEW COMMANDS ---

@bot.tree.command(name="streaming", description="View available Streaming services")
async def streaming(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("streaming", [])
    embed = create_item_embed("streaming", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gaming", description="View available Gaming items")
async def gaming(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("gaming", [])
    embed = create_item_embed("gaming", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="vpn", description="View available VPN services")
async def vpn(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("vpn", [])
    embed = create_item_embed("vpn", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="accounts", description="View available Accounts")
async def accounts(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("accounts", [])
    embed = create_item_embed("accounts", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="codes", description="View available Codes")
async def codes(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("codes", [])
    embed = create_item_embed("codes", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="outofstock", description="View out of stock items")
async def outofstock(interaction: discord.Interaction):
    inventory = load_inventory()
    items = inventory.get("outofstock", [])
    embed = create_item_embed("outofstock", items)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="all", description="View all available items")
async def all_items(interaction: discord.Interaction):
    inventory = load_inventory()
    embed = discord.Embed(
        title="🏪 All Available Items",
        description="Complete inventory",
        color=discord.Color.gold()
    )
    
    category_emojis = {
        "streaming": "📺",
        "gaming": "🎮",
        "vpn": "🔒",
        "accounts": "👤",
        "codes": "🎟️",
        "outofstock": "❌"
    }
    
    total = 0
    for category, items in inventory.items():
        if items:
            emoji = category_emojis.get(category, "📦")
            item_list = "\n".join([f"• {item['name']}" + (f" - ${item['price']}" if item['price'] > 0 else " - Price TBA") for item in items[:5]])
            if len(items) > 5:
                item_list += f"\n... and {len(items) - 5} more"
            embed.add_field(
                name=f"{emoji} {category.upper()} ({len(items)} items)",
                value=item_list,
                inline=False
            )
            total += len(items)
    
    embed.set_footer(text=f"Total items in stock: {total}")
    await interaction.response.send_message(embed=embed)

# --- ADMIN COMMANDS ---

@bot.tree.command(name="add", description="Add an item to inventory (Admin only)")
@app_commands.describe(
    category="Category (streaming, gaming, vpn, accounts, codes, outofstock)",
    name="Item name",
    price="Price in USD (use 0 for TBA)"
)
async def add_item(interaction: discord.Interaction, category: str, name: str, price: float):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    category = category.lower()
    inventory = load_inventory()
    
    if category not in inventory:
        inventory[category] = []
    
    new_item = {"name": name, "price": price}
    inventory[category].append(new_item)
    save_inventory(inventory)
    
    embed = discord.Embed(
        title="✅ Item Added Successfully",
        description=f"Added to {category.upper()} category",
        color=discord.Color.green()
    )
    embed.add_field(name="Item", value=name, inline=True)
    embed.add_field(name="Price", value=f"${price}" if price > 0 else "Price TBA", inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="remove", description="Remove an item from inventory (Admin only)")
@app_commands.describe(
    category="Category (streaming, gaming, vpn, accounts, codes, outofstock)",
    name="Item name to remove"
)
async def remove_item(interaction: discord.Interaction, category: str, name: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    category = category.lower()
    inventory = load_inventory()
    
    if category not in inventory:
        await interaction.response.send_message(f"❌ Category '{category}' not found!", ephemeral=True)
        return
    
    original_length = len(inventory[category])
    inventory[category] = [item for item in inventory[category] if item['name'] != name]
    
    if len(inventory[category]) == original_length:
        await interaction.response.send_message(f"❌ Item '{name}' not found in {category}!", ephemeral=True)
        return
    
    save_inventory(inventory)
    
    embed = discord.Embed(
        title="✅ Item Removed Successfully",
        description=f"Removed '{name}' from {category.upper()}",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="edit", description="Edit item price (Admin only)")
@app_commands.describe(
    category="Category (streaming, gaming, vpn, accounts, codes, outofstock)",
    name="Item name",
    new_price="New price in USD (use 0 for TBA)"
)
async def edit_item(interaction: discord.Interaction, category: str, name: str, new_price: float):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    category = category.lower()
    inventory = load_inventory()
    
    if category not in inventory:
        await interaction.response.send_message(f"❌ Category '{category}' not found!", ephemeral=True)
        return
    
    found = False
    for item in inventory[category]:
        if item['name'] == name:
            old_price = item['price']
            item['price'] = new_price
            found = True
            break
    
    if not found:
        await interaction.response.send_message(f"❌ Item '{name}' not found in {category}!", ephemeral=True)
        return
    
    save_inventory(inventory)
    
    embed = discord.Embed(
        title="✅ Item Updated Successfully",
        description=f"Updated '{name}' in {category.upper()}",
        color=discord.Color.blue()
    )
    old_display = f"${old_price}" if old_price > 0 else "Price TBA"
    new_display = f"${new_price}" if new_price > 0 else "Price TBA"
    embed.add_field(name="Old Price", value=old_display, inline=True)
    embed.add_field(name="New Price", value=new_display, inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="reload", description="Reload inventory from file (Admin only)")
async def reload_inventory(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return
    
    load_inventory()
    await interaction.response.send_message("✅ Inventory reloaded from file!", ephemeral=True)

# --- NEW COMMAND: LIST EMOJIS ---

@bot.tree.command(name="list_emojis", description="Get the codes for all server emojis (Admin only)")
async def list_emojis(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)
        return

    emojis = interaction.guild.emojis
    
    if not emojis:
        await interaction.response.send_message("This server has no custom emojis.", ephemeral=True)
        return

    emoji_strings = [f"**{e.name}**: `{str(e)}`" for e in emojis]
    full_message = "\n".join(emoji_strings)
    
    if len(full_message) > 1900:
        with open("emojis.txt", "w", encoding="utf-8") as f:
            f.write("\n".join([f"{e.name}: {str(e)}" for e in emojis]))
        
        await interaction.response.send_message("The list is too long, so I've attached it as a file:", file=discord.File("emojis.txt"))
        os.remove("emojis.txt") 
    else:
        embed = discord.Embed(
            title="Custom Server Emojis",
            description=full_message,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

# --- EXECUTION ---

if __name__ == "__main__":

    TOKEN = "MTQ3MTA1NzYzNzM1NjQ3NDUwMg.GVPo_X._f0bYQDEBtj4fRNIqNI5j5pqpEiCiH5NPBdTfs" 
    bot.run(TOKEN)