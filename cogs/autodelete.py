import discord
from discord.ext import commands
import asyncio


class AutoDelete(commands.Cog):
    """A cog that automatically deletes command messages and bot responses after a delay."""

    def __init__(self, bot):
        self.bot = bot
        self.response_delete_delay = 30

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener to delete command messages immediately after they're sent."""
        if message.author.bot:
            return  # Ignore messages from bots

        # Check if the message is a valid command
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            # Ensure the bot has permission to manage messages
            if (
                message.guild
                and message.channel.permissions_for(message.guild.me).manage_messages
            ):
                try:
                    # Delete the command message instantly
                    await message.delete()
                except discord.errors.NotFound:
                    pass  # Message was already deleted, possibly manually
                except discord.errors.Forbidden:
                    print(f"⚠️ No permission to delete message in {message.channel}")
                except Exception as e:
                    print(f"Unexpected error when deleting a message: {e}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Listener to delete bot responses after a delay once a command completes successfully."""
        # Ignore cases where the command failed
        if ctx.command_failed:
            return

        # Check if the bot has permission to delete messages in the current channel
        if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await asyncio.sleep(0.5)  # Short delay to ensure the bot's response is sent

            # Find the bot's latest response after the user's command
            async for response in ctx.channel.history(limit=1, after=ctx.message):
                if response.author == self.bot.user:
                    try:
                        await asyncio.sleep(
                            self.response_delete_delay
                        )  # Wait for the set delay
                        await response.delete()  # Delete the bot's response
                    except discord.errors.NotFound:
                        pass  # The message was already deleted
                    except discord.errors.Forbidden:
                        print(
                            f"⚠️ No permission to delete bot response in {response.channel}"
                        )
                    except Exception as e:
                        print(f"Unexpected error while deleting bot response: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def set_response_delay(self, ctx, seconds: int):
        """Sets the delay (in seconds) before bot responses are automatically deleted."""
        if seconds < 5:
            await ctx.send("⏱️ Delay must be at least 5 seconds.", delete_after=10)
            return
        self.response_delete_delay = seconds
        await ctx.send(
            f"🕒 Bot response auto-delete delay set to {seconds} seconds.",
            delete_after=10,
        )


async def setup(bot):
    await bot.add_cog(AutoDelete(bot))


import discord
from discord.ext import commands
import asyncio


class AutoDelete(commands.Cog):
    """A cog that automatically deletes command messages and bot responses after a delay."""

    def __init__(self, bot):
        self.bot = bot
        self.response_delete_delay = 30  # Default delay for bot responses (in seconds)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener to delete command messages immediately after they're sent."""
        if message.author.bot:
            return  # Ignore messages from bots

        # Check if the message is a valid command
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            # Ensure the bot has permission to manage messages
            if (
                message.guild
                and message.channel.permissions_for(message.guild.me).manage_messages
            ):
                try:
                    # Delete the command message instantly
                    await message.delete()
                except discord.errors.NotFound:
                    pass  # Message was already deleted, possibly manually
                except discord.errors.Forbidden:
                    print(f"⚠️ No permission to delete message in {message.channel}")
                except Exception as e:
                    print(f"Unexpected error when deleting a message: {e}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Listener to delete bot responses after a delay once a command completes successfully."""
        # Ignore cases where the command failed
        if ctx.command_failed:
            return

        # Check if the bot has permission to delete messages in the current channel
        if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await asyncio.sleep(0.5)  # Short delay to ensure the bot's response is sent

            # Find the bot's latest response after the user's command
            async for response in ctx.channel.history(limit=1, after=ctx.message):
                if response.author == self.bot.user:
                    try:
                        await asyncio.sleep(
                            self.response_delete_delay
                        )  # Wait for the set delay
                        await response.delete()  # Delete the bot's response
                    except discord.errors.NotFound:
                        pass  # The message was already deleted
                    except discord.errors.Forbidden:
                        print(
                            f"⚠️ No permission to delete bot response in {response.channel}"
                        )
                    except Exception as e:
                        print(f"Unexpected error while deleting bot response: {e}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def set_response_delay(self, ctx, seconds: int):
        """Sets the delay (in seconds) before bot responses are automatically deleted."""
        if seconds < 5:
            await ctx.send("⏱️ Delay must be at least 5 seconds.", delete_after=10)
            return
        self.response_delete_delay = seconds
        await ctx.send(
            f"🕒 Bot response auto-delete delay set to {seconds} seconds.",
            delete_after=10,
        )


async def setup(bot):
    await bot.add_cog(AutoDelete(bot))
