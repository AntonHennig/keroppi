import os
import json
import discord
from discord.ext import commands


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_cog_config(self):
        """writes changes to JSON File"""
        loaded_cogs = [
        
            f"cogs.{cog.__class__.__name__.lower()}" for cog in self.bot.cogs.values()
        ]
        with open("cogs_config.json", "w") as f:
            json.dump(loaded_cogs, f)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension):
        """^^"""
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Loaded {extension}")
        except Exception as e:
            await ctx.send(f"Error loading {extension}: {e}")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """^^"""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Unloaded {extension}")
        except Exception as e:
            await ctx.send(f"Error unloading {extension}: {e}")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Reload"""
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            self.update_cog_config()
            await ctx.send(f"Reloaded {extension}")
        except Exception as e:
            await ctx.send(f"Error reloading {extension}: {e}")

    def load_cogs_from_config(self):
        """Loads the cogs from the JSON file."""
        try:
            with open("cogs_config.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
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
    await bot.add_cog(Core(bot))
