import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def k_help(self, ctx, command=None):
        """Display help information for commands."""
        if command is None:
            # List all commands
            embed = discord.Embed(title="Bot Commands", description="Here are the available commands:", color=discord.Color.blue())
            for cmd in self.bot.commands:
                if not cmd.hidden:
                    embed.add_field(name=cmd.name, value=cmd.help or "No description available", inline=False)
            await ctx.send(embed=embed)
        else:
            # Display help for a specific command
            cmd = self.bot.get_command(command)
            if cmd:
                embed = discord.Embed(title=f"Help: {cmd.name}", description=cmd.help or "No description available", color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Command '{command}' not found.")

async def setup(bot):
    await bot.add_cog(Help(bot))