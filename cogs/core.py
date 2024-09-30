import os
import json
from discord.ext import commands

CONFIG_DIR = "/app/config"  # Same as in bot.py
CONFIG_FILE = os.path.join(CONFIG_DIR, "cogs_config.json")  # Full path to the config file


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ensure the config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # Load cogs from config on initialization
        self.loaded_cogs = self.load_cogs_from_config()

    def update_cog_config(self):
        """Writes the currently loaded cogs to the JSON file."""
        loaded_cogs = [
            f"cogs.{cog.__class__.__name__.lower()}" for cog in self.bot.cogs.values()
        ]
        with open(CONFIG_FILE, "w") as f:
            json.dump({"loaded_cogs": loaded_cogs}, f, indent=4)

    def load_cogs_from_config(self):
        """Loads the cogs from the JSON configuration file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("loaded_cogs", [])
        except FileNotFoundError:
            # Create the config file if it doesn't exist and return an empty list
            with open(CONFIG_FILE, "w") as f:
                json.dump({"loaded_cogs": []}, f, indent=4)
            return []

    def get_all_cogs(self):
        """Returns a list of all cogs in the cogs folder."""
        cogs_folder = "./cogs"  # The folder where your cogs are stored
        cogs = []
        for filename in os.listdir(cogs_folder):
            if filename.endswith(".py"):  # Only include Python files
                cogs.append(f"cogs.{filename[:-3]}")  # Remove the ".py"
        return cogs

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        """Load a cog."""
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Loaded {extension}")
        except Exception as e:
            await ctx.send(f"Error loading {extension}: {e}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """Unload a cog."""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Unloaded {extension}")
        except Exception as e:
            await ctx.send(f"Error unloading {extension}: {e}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Reload a cog."""
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Reloaded {extension}")
        except Exception as e:
            await ctx.send(f"Error reloading {extension}: {e}")

    @commands.command()
    async def list_cogs(self, ctx):
        """Lists loaded and unloaded cogs."""
        loaded_cogs = self.load_cogs_from_config()
        all_cogs = self.get_all_cogs()

        # Cogs that are currently loaded
        currently_loaded = [cog for cog in all_cogs if cog in loaded_cogs]
        # Cogs that are not loaded
        unloaded_cogs = [cog for cog in all_cogs if cog not in loaded_cogs]

        # Formatting the output for readability
        loaded_text = ", ".join([cog[5:] for cog in currently_loaded]) or "None"
        unloaded_text = ", ".join([cog[5:] for cog in unloaded_cogs]) or "None"

        # Send the message with loaded and unloaded cogs
        await ctx.send(
            f"**Loaded Cogs:** {loaded_text}\n**Unloaded Cogs:** {unloaded_text}"
        )


async def setup(bot):
    core_cog = Core(bot)
    await bot.add_cog(core_cog)
    core_cog.update_cog_config()
