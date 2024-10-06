import discord
from discord.ext import commands
from decorators import delete_command_message, delete_bot_response


class Help(commands.Cog):
    """Provides help information for all commands."""

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command("help")  # Remove the default help command

    @commands.command(name="help", aliases=["h"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=300)  # Keep the help message for 5 minutes
    async def help(self, ctx, *, command_name: str = None):
        """Displays help information for commands and cogs.

        **Usage:**
        `!help` - Shows this help message.
        `!help <command>` - Shows detailed help for the specified command.
        """
        if command_name is None:
            # Show the general help message
            await self.general_help(ctx)
        else:
            # Show detailed help for a specific command
            await self.command_help(ctx, command_name)

    async def general_help(self, ctx):
        """Displays the general help message with aliases included."""
        prefix = ctx.clean_prefix
        cogs = [cog for cog in self.bot.cogs.values() if cog.get_commands()]
        cogs.sort(key=lambda c: c.qualified_name)

        embeds = []

        for cog in cogs:
            embed = discord.Embed(
                title=f"📖 Help - {cog.qualified_name} Cog",
                description=cog.description or "No description provided.",
                color=discord.Color.blue(),
            )
            command_list = ""
            for cmd in cog.get_commands():
                if not cmd.hidden:
                    # Include command names and aliases
                    command_names = [cmd.name] + cmd.aliases
                    command_names_str = ", ".join(
                        f"`{prefix}{name}`" for name in command_names
                    )
                    entry = f"{command_names_str} - {cmd.short_doc}\n"
                    # Ensure field value doesn't exceed 1024 characters
                    if len(command_list) + len(entry) > 1024:
                        embed.add_field(
                            name="Commands",
                            value=command_list,
                            inline=False,
                        )
                        command_list = entry
                    else:
                        command_list += entry
            if command_list:
                embed.add_field(
                    name="Commands",
                    value=command_list,
                    inline=False,
                )
            embeds.append(embed)

        # Handle uncategorized commands
        uncategorized_commands = [
            cmd for cmd in self.bot.commands if not cmd.cog and not cmd.hidden
        ]
        if uncategorized_commands:
            embed = discord.Embed(
                title="📖 Help - Uncategorized Commands",
                description="Commands not grouped under any cog.",
                color=discord.Color.blue(),
            )
            command_list = ""
            for cmd in uncategorized_commands:
                # Include command names and aliases
                command_names = [cmd.name] + cmd.aliases
                command_names_str = ", ".join(
                    f"`{prefix}{name}`" for name in command_names
                )
                entry = f"{command_names_str} - {cmd.short_doc}\n"
                # Ensure field value doesn't exceed 1024 characters
                if len(command_list) + len(entry) > 1024:
                    embed.add_field(
                        name="Commands",
                        value=command_list,
                        inline=False,
                    )
                    command_list = entry
                else:
                    command_list += entry
            if command_list:
                embed.add_field(
                    name="Commands",
                    value=command_list,
                    inline=False,
                )
            embeds.append(embed)

        # Send the embeds
        for embed in embeds:
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )
            await ctx.send(embed=embed)

    async def command_help(self, ctx, command_name):
        """Displays detailed help for a specific command."""
        prefix = ctx.clean_prefix
        command = self.bot.get_command(command_name)
        if command and not command.hidden:
            embed = discord.Embed(
                title=f"📄 Help - {command.qualified_name}",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Description",
                value=command.help or "No description available.",
                inline=False,
            )
            embed.add_field(
                name="Usage",
                value=f"`{prefix}{command.qualified_name} {command.signature}`",
                inline=False,
            )
            if command.aliases:
                aliases_str = ", ".join(f"`{alias}`" for alias in command.aliases)
                embed.add_field(
                    name="Aliases",
                    value=aliases_str,
                    inline=False,
                )
            # Check for subcommands
            if isinstance(command, commands.Group) and command.commands:
                subcommands = [
                    f"`{prefix}{cmd.qualified_name}` - {cmd.short_doc}"
                    for cmd in command.commands
                    if not cmd.hidden
                ]
                subcommand_text = "\n".join(subcommands)
                embed.add_field(
                    name="Subcommands",
                    value=subcommand_text,
                    inline=False,
                )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )
            await ctx.send(embed=embed)
        else:
            # Command not found
            await ctx.send(
                f"❌ Command `{command_name}` not found. Use `{prefix}help` to see the available commands.",
                delete_after=10,
            )


async def setup(bot):
    await bot.add_cog(Help(bot))
