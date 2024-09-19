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
            
    @commands.command()
    async def list(self, ctx, extension):
        """list all available cogs"""
        
    


async def setup(bot):
    await bot.add_cog(Core(bot))
