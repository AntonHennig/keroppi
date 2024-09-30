import os
import json
from discord.ext import commands

# Directory and file for storing cog configurations
CONFIG_DIR = "/app/config"
CONFIG_FILE = os.path.join(
    CONFIG_DIR, "cogs_config.json"
)  # Full path to the cogs config file


class Core(commands.Cog):
    """Core cog for managing the loading, unloading, and listing of other cogs."""

    def __init__(self, bot):
        self.bot = bot
        # Ensure the config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Load cogs from the config on initialization
        self.loaded_cogs = self.load_cogs_from_config()

    def update_cog_config(self):
        # Update the config file with the loaded cogs
        loaded_cogs = [
            f"cogs.{cog.__class__.__name__.lower()}" for cog in self.bot.cogs.values()
        ]
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"loaded_cogs": loaded_cogs}, f, indent=4)
        except Exception as e:
            print(f"Error writing to config file: {e}")

    def load_cogs_from_config(self):
        # Load the cogs from the config file
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("loaded_cogs", [])
        except FileNotFoundError:
            # If the config file is missing, create it with an empty list
            with open(CONFIG_FILE, "w") as f:
                json.dump({"loaded_cogs": []}, f, indent=4)
            return []
        except json.JSONDecodeError as e:
            print(f"Error reading config file: {e}")
            return []

    def get_all_cogs(self):
        # Get a list of all cogs in the cogs folder
        cogs_folder = "./cogs"  # Directory where the cogs are stored
        cogs = []
        try:
            for filename in os.listdir(cogs_folder):
                if filename.endswith(".py"):  # Only Python files are considered cogs
                    cogs.append(f"cogs.{filename[:-3]}")  # Strip the ".py" extension
        except FileNotFoundError:
            print(f"Cogs folder '{cogs_folder}' not found.")
        return cogs

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, *extension: str):
        """Load cogs by name."""
        for cog in extension:
            try:
                await self.bot.load_extension(f"cogs.{cog}")
                self.update_cog_config()
                await ctx.send(f"✅ Loaded cog: {cog}")
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(f"⚠️ The cog `{cog}` is already loaded.")
            except Exception as e:
                await ctx.send(f"❌ Error loading cog `{cog}`: {e}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, *extension: str):
        """Unload cogs by name."""
        for cog in extension:
            try:
                await self.bot.unload_extension(f"cogs.{cog}")
                self.update_cog_config()
                await ctx.send(f"✅ Unloaded cog: {cog}")
            except commands.ExtensionNotLoaded:
                await ctx.send(f"⚠️ The cog `{cog}` is not loaded.")
            except Exception as e:
                await ctx.send(f"❌ Error unloading cog `{cog}`: {e}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *extension: str):
        """Reload a cog by name."""
        for cog in extension:
            try:
                await self.bot.reload_extension(f"cogs.{cog}")
                self.update_cog_config()
                await ctx.send(f"🔄 Reloaded cog: {cog}")
            except commands.ExtensionNotLoaded:
                await ctx.send(
                    f"⚠️ The cog `{cog}` is not loaded, so cannot be reloaded."
                )
            except Exception as e:
                await ctx.send(f"❌ Error reloading cog `{cog}`: {e}")

    @commands.command()
    async def list_cogs(self, ctx):
        """List all loaded and unloaded cogs."""
        loaded_cogs = self.load_cogs_from_config()
        all_cogs = self.get_all_cogs()

        # Determine which cogs are loaded and which are not
        currently_loaded = [cog for cog in all_cogs if cog in loaded_cogs]
        unloaded_cogs = [cog for cog in all_cogs if cog not in loaded_cogs]

        # Format the loaded and unloaded cogs for output
        loaded_text = ", ".join([cog[5:] for cog in currently_loaded]) or "None"
        unloaded_text = ", ".join([cog[5:] for cog in unloaded_cogs]) or "None"

        # Send the result to the Discord channel
        await ctx.send(
            f"**Loaded Cogs:** {loaded_text}\n**Unloaded Cogs:** {unloaded_text}"
        )

async def setup(bot):
    core_cog = Core(bot)
    await bot.add_cog(core_cog)
    core_cog.update_cog_config()
