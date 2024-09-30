import discord
from discord.ext import commands


class Help(commands.Cog):
    """Cog for the custom help command."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")  # Remove the default help command

    @commands.command(name="help", aliases=["h"])
    async def k_help(self, ctx, *, command_name: str = None):
        """Display help information for commands and cogs."""
        if command_name is None:
            # Show a general help message listing all commands grouped by cog
            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the available commands:",
                color=discord.Color.blue(),
            )
            for cog in self.bot.cogs:
                cog_commands = self.bot.get_cog(cog).get_commands()
                command_list = [
                    f"`{cmd.name}`" for cmd in cog_commands if not cmd.hidden
                ]
                if command_list:
                    embed.add_field(
                        name=f"**{cog}**", value=", ".join(command_list), inline=False
                    )

            # List commands not in a cog
            uncogged_commands = [
                f"`{cmd.name}`"
                for cmd in self.bot.commands
                if not cmd.cog and not cmd.hidden
            ]
            if uncogged_commands:
                embed.add_field(
                    name="**Uncategorized Commands**",
                    value=", ".join(uncogged_commands),
                    inline=False,
                )

            embed.set_footer(
                text="Use !help <command> for more info on a specific command."
            )
            await ctx.send(embed=embed)
        else:
            # Show detailed help for a specific command or cog
            cmd = self.bot.get_command(command_name)
            if cmd:
                # Display help for the specific command
                embed = discord.Embed(
                    title=f"Help: {cmd.name}",
                    description=cmd.help or "No description available.",
                    color=discord.Color.green(),
                )
                if cmd.aliases:
                    embed.add_field(
                        name="Aliases",
                        value=", ".join([f"`{alias}`" for alias in cmd.aliases]),
                        inline=False,
                    )
                embed.add_field(
                    name="Usage",
                    value=f"`{ctx.prefix}{cmd.name} {cmd.signature}`",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                # Command not found
                await ctx.send(
                    f"❌ Command `{command_name}` not found. Use `!help` to see the available commands."
                )


async def setup(bot):
    await bot.add_cog(Help(bot))
