import os
import json
import discord
from discord.ext import commands
import asyncio
from decorators import delete_command_message, delete_bot_response

# Directory and file for storing cog configurations
CONFIG_DIR = "./config"
CONFIG_FILE = os.path.join(
    CONFIG_DIR, "cogs_config.json"
)  # Full path to the cogs config file

# List of cogs that should not be manipulated
PROTECTED_COGS = ["cogs.core", "cogs.help"]


class Core(
    commands.Cog, description="Commands for managing the bot's cogs (extensions)."
):
    """Core cog for managing the loading, unloading, and listing of other cogs."""

    def __init__(self, bot):
        self.bot = bot
        # Ensure the config directory exists
        os.makedirs(CONFIG_DIR, exist_ok=True)
        # Load cogs from the config on initialization
        self.loaded_cogs = self.load_cogs_from_config()
        # Remove protected cogs from the config if they exist
        self.loaded_cogs = [
            cog for cog in self.loaded_cogs if cog not in PROTECTED_COGS
        ]

    def update_cog_config(self):
        """Update the config file with the loaded cogs, excluding protected cogs."""
        loaded_cogs = [
            f"cogs.{cog.__class__.__name__.lower()}" for cog in self.bot.cogs.values()
        ]
        # Exclude protected cogs
        loaded_cogs = [cog for cog in loaded_cogs if cog not in PROTECTED_COGS]
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"loaded_cogs": loaded_cogs}, f, indent=4)
        except Exception as e:
            print(f"Error writing to config file: {e}")

    def load_cogs_from_config(self):
        """Load the cogs from the config file, excluding protected cogs."""
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded_cogs = json.load(f).get("loaded_cogs", [])
                # Exclude protected cogs
                loaded_cogs = [cog for cog in loaded_cogs if cog not in PROTECTED_COGS]
                return loaded_cogs
        except FileNotFoundError:
            # If the config file is missing, create it with an empty list
            with open(CONFIG_FILE, "w") as f:
                json.dump({"loaded_cogs": []}, f, indent=4)
            return []
        except json.JSONDecodeError as e:
            print(f"Error reading config file: {e}")
            return []

    def get_all_cogs(self):
        """Get a list of all cogs in the cogs folder, excluding protected cogs."""
        cogs_folder = "./cogs"  # Directory where the cogs are stored
        cogs = []
        try:
            for filename in os.listdir(cogs_folder):
                if (
                    filename.endswith(".py") and filename != "__init__.py"
                ):  # Exclude __init__.py
                    cog_name = f"cogs.{filename[:-3]}"  # Strip the ".py" extension
                    if cog_name not in PROTECTED_COGS:
                        cogs.append(cog_name)
        except FileNotFoundError:
            print(f"Cogs folder '{cogs_folder}' not found.")
        return cogs

    @commands.command()
    @commands.is_owner()
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def load(self, ctx):
        """Load cogs interactively.

        **Usage:**
        `!load
        """
        await self.manage_cogs(ctx, action="load")

    @commands.command()
    @commands.is_owner()
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def unload(self, ctx):
        """Unload cogs interactively."""
        await self.manage_cogs(ctx, action="unload")

    @commands.command()
    @commands.is_owner()
    @delete_command_message(delay=0)
    @delete_bot_response(delay=5)
    async def reload(self, ctx):
        """Reload cogs interactively.

        **Usage:**
        `!reload
        """
        await self.manage_cogs(ctx, action="reload")

    async def manage_cogs(self, ctx, action):
        """Helper method to interactively manage cogs using select menus."""
        if action == "load":
            available_cogs = [
                cog for cog in self.get_all_cogs() if cog not in self.bot.extensions
            ]
        elif action in ["unload", "reload"]:
            available_cogs = [
                cog for cog in self.bot.extensions.keys() if cog not in PROTECTED_COGS
            ]
        else:
            await ctx.send("❌ Invalid action.", delete_after=5)
            return

        if not available_cogs:
            await ctx.send(f"🛑 No cogs available to {action}.", delete_after=5)
            return

        # Sort cogs alphabetically
        available_cogs.sort()

        # Create select options
        options = [
            discord.SelectOption(label=cog[5:], value=cog) for cog in available_cogs
        ]

        # Handle options exceeding 25 limit
        option_chunks = [options[i : i + 25] for i in range(0, len(options), 25)]

        selected_cogs = []

        for chunk_index, option_chunk in enumerate(option_chunks):
            embed = discord.Embed(
                title=f"Select cogs to {action.capitalize()}",
                description=f"Page {chunk_index + 1} of {len(option_chunks)}",
                color=discord.Color.blue(),
            )
            view = discord.ui.View()
            select = discord.ui.Select(
                placeholder=f"Select cogs to {action.capitalize()}",
                options=option_chunk,
                min_values=1,
                max_values=len(option_chunk),
            )
            view.add_item(select)

            message = await ctx.send(embed=embed, view=view)

            async def select_callback(interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message(
                        "❌ You are not authorized to perform this action.",
                        ephemeral=True,
                    )
                    return
                selected_cogs.extend(select.values)
                await interaction.response.defer()
                await message.delete()
                # After selection, perform the action on the selected cogs
                await self.perform_cog_action(ctx, action, selected_cogs)

            select.callback = select_callback

            # Wait for interaction
            def check(interaction):
                return (
                    interaction.user == ctx.author
                    and interaction.message.id == message.id
                )

            try:
                await self.bot.wait_for("interaction", timeout=60.0, check=check)
                # Break after processing
                break
            except asyncio.TimeoutError:
                await message.delete()
                await ctx.send(
                    "⏰ You took too long to respond. Please try again.", delete_after=5
                )
                return

    async def perform_cog_action(self, ctx, action, cogs):
        """Performs the specified action on the list of cogs."""
        for cog in cogs:
            try:
                if action == "load":
                    await self.bot.load_extension(cog)
                    await ctx.send(f"✅ Loaded cog: `{cog[5:]}`", delete_after=5)
                elif action == "unload":
                    await self.bot.unload_extension(cog)
                    await ctx.send(f"✅ Unloaded cog: `{cog[5:]}`", delete_after=5)
                elif action == "reload":
                    await self.bot.reload_extension(cog)
                    await ctx.send(f"🔄 Reloaded cog: `{cog[5:]}`", delete_after=5)
                self.update_cog_config()
            except commands.ExtensionAlreadyLoaded:
                await ctx.send(
                    f"⚠️ The cog `{cog[5:]}` is already loaded.", delete_after=5
                )
            except commands.ExtensionNotLoaded:
                await ctx.send(f"⚠️ The cog `{cog[5:]}` is not loaded.", delete_after=5)
            except Exception as e:
                await ctx.send(
                    f"❌ Error {action}ing cog `{cog[5:]}`: {e}", delete_after=5
                )

    @commands.command(aliases=["cogs"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=30)
    async def list_cogs(self, ctx):
        """List all loaded and unloaded cogs."""
        loaded_cogs = [
            cog for cog in self.bot.extensions.keys() if cog not in PROTECTED_COGS
        ]
        all_cogs = self.get_all_cogs()

        # Determine which cogs are loaded and which are not
        currently_loaded = [cog for cog in all_cogs if cog in loaded_cogs]
        unloaded_cogs = [cog for cog in all_cogs if cog not in loaded_cogs]

        # Format the loaded and unloaded cogs for output
        loaded_text = (
            "\n".join([f"✅ `{cog[5:]}`" for cog in currently_loaded]) or "None"
        )
        unloaded_text = (
            "\n".join([f"❌ `{cog[5:]}`" for cog in unloaded_cogs]) or "None"
        )

        # Create an embed with beautiful design
        embed = discord.Embed(title="📜 Cog List", color=discord.Color.green())
        embed.add_field(name="Loaded Cogs", value=loaded_text, inline=True)
        embed.add_field(name="Unloaded Cogs", value=unloaded_text, inline=True)
        embed.set_footer(text=f"Total Cogs: {len(all_cogs)}")
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx, error):
        """Handle errors for commands in this cog."""
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                "❌ You do not have permission to use this command.", delete_after=5
            )
        else:
            await ctx.send(f"⚠️ An error occurred: {error}", delete_after=5)


async def setup(bot):
    await bot.add_cog(Core(bot))
