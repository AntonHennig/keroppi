import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import logging
import sys

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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
    logging.info(f"{bot.user} is Online")

async def main():
    await bot.load_extension("cogs.core")
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
