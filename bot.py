import os
import json
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

command_prefix = "!"

# Create bot instance
bot = commands.Bot(command_prefix, intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


# Function to load cogs from the configuration file
def load_cogs_from_config():
    try:
        with open("cogs_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file doesn't exist, create it with default cogs
        default_cogs = ["cogs.core"]
        with open("cogs_config.json", "w") as f:
            json.dump(default_cogs, f)
        return default_cogs


async def main():
    cogs_to_load = load_cogs_from_config()

    loaded_ext = []
    failed_ext = []

    for extension in cogs_to_load:
        try:
            await bot.load_extension(extension)
            loaded_ext.append(
                extension[5:] if extension.startswith("cogs.") else extension
            )
        except Exception as e:
            failed_ext.append((extension, str(e)))

    print("Loaded extensions:")
    for ext in loaded_ext:
        print(f"- {ext}")

    if failed_ext:
        print("Failed to load extensions:")
        for ext in failed_ext:
            print(f"- {ext}")

    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
