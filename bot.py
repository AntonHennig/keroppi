import os
import sys
import logging
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import discord
import json

# Configure logging to output to the console
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Check if the token is provided in the .env file
if not TOKEN:
    logging.error("DISCORD_TOKEN not found in environment variables.")
    sys.exit("Missing DISCORD_TOKEN. Please check your .env file.")

# Set up the required bot intents
intents = discord.Intents.default()
intents.message_content = True  # Enable access to message content

# Define the command prefix for the bot
COMMAND_PREFIX = "!"

# Create bot instance
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is now online and ready.")


# List of cogs that should always be loaded and cannot be unloaded
PROTECTED_COGS = ["cogs.core", "cogs.help"]

# Path to the cogs configuration file
CONFIG_DIR = "./config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "cogs_config.json")


async def load_extensions():
    """Load bot extensions (cogs)."""

    # Ensure the config directory exists
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Always load protected cogs
    for cog in PROTECTED_COGS:
        try:
            await bot.load_extension(cog)
            logging.info(f"Successfully loaded protected cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load protected cog {cog}: {e}")
            # Since these are protected cogs, exit if they fail to load
            sys.exit(f"Error loading protected cog {cog}. Exiting.")

    # Load other cogs from the configuration file
    loaded_cogs = []

    # Try to read the configuration file
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            loaded_cogs = data.get("loaded_cogs", [])
            # Exclude protected cogs if they are somehow in the list
            loaded_cogs = [cog for cog in loaded_cogs if cog not in PROTECTED_COGS]
    except FileNotFoundError:
        # If the config file is missing, create it with an empty list
        with open(CONFIG_FILE, "w") as f:
            json.dump({"loaded_cogs": []}, f, indent=4)
        logging.info("Created new cogs configuration file.")
    except json.JSONDecodeError as e:
        logging.error(f"Error reading cogs configuration file: {e}")
        # Reset the config file due to error
        with open(CONFIG_FILE, "w") as f:
            json.dump({"loaded_cogs": []}, f, indent=4)
        logging.info("Reset cogs configuration file due to error.")

    # Now load the cogs from the configuration file
    for cog in loaded_cogs:
        try:
            await bot.load_extension(cog)
            logging.info(f"Successfully loaded cog: {cog}")
        except Exception as e:
            logging.error(f"Failed to load cog {cog}: {e}")
            # Continue loading other cogs even if one fails


async def main():
    """Main entry point for the bot."""
    await load_extensions()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logging.info("Bot shutdown requested by user.")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
    finally:
        pass  # No action needed here


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"An error occurred in the main event loop: {e}")
