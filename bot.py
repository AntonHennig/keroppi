import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import logging
import sys

# Configure logging to output to the console
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Check if the token is provided in the .env file
if not TOKEN:
    logging.error("DISCORD_TOKEN not found in environment variables.")
    sys.exit("Missing DISCORD_TOKEN. Please check your .env file.")

# Set up the required bot intents
intents = discord.Intents.default()
intents.message_content = True

# Define the command prefix for the bot
command_prefix = "!"

# Create bot instance
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

# Bot ready message
@bot.event
async def on_ready():
    logging.info(f"{bot.user} is now online and ready.")

default_cogs = ["cogs.core", "cogs.help"]

async def load_extensions():
    for cog in default_cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"Successfully loaded {cog}.")
        except Exception as e:
            logging.error(f"Failed to load core cog: {e}")
            sys.exit("Error loading core cog. Exiting.")

async def main():
    await load_extensions()
    try:
        await bot.start(TOKEN)
    except discord.DiscordException as e:
        logging.error(f"Failed to start the bot: {e}")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
    finally:
        # Graceful shutdown if something goes wrong or the bot is interrupted
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested by user.")
    except Exception as e:
        logging.critical(f"An error occurred in the main event loop: {e}")
