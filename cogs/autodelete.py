import discord
from discord.ext import commands
import asyncio
from decorators import delete_command_message, delete_bot_response


class AutoDelete(
    commands.Cog,
    description="Automatically deletes command messages and bot responses after specified delays.",):
    """A cog that automatically deletes command messages and bot responses."""

    def __init__(self, bot):
        self.bot = bot
        self.default_command_delete_delay = None  # Default is not to delete commands
        self.default_response_delete_delay = None  # Default is not to delete responses

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener to delete command messages based on per-command settings."""
        if message.author.bot:
            return  # Ignore messages from bots

        # Check if the message is a valid command
        ctx = await self.bot.get_context(message)
        if ctx.valid and ctx.command:
            # Get the delete delay from the command's attribute
            delay = getattr(
                ctx.command.callback,
                "_delete_command_delay",
                self.default_command_delete_delay,
            )
            if delay is not None:
                # Ensure the bot has permission to manage messages
                if (
                    message.guild
                    and message.channel.permissions_for(
                        message.guild.me
                    ).manage_messages
                ):
                    try:
                        # Delete the command message after the specified delay
                        await asyncio.sleep(delay)
                        await message.delete()
                    except discord.errors.NotFound:
                        pass  # Message was already deleted
                    except discord.errors.Forbidden:
                        print(f"⚠️ No permission to delete message in {message.channel}")
                    except Exception as e:
                        print(f"Unexpected error when deleting a message: {e}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Listener to delete bot responses based on per-command settings."""
        # Ignore cases where the command failed
        if ctx.command_failed:
            return

        # Get the delete delay from the command's attribute
        delay = getattr(
            ctx.command.callback,
            "_delete_response_delay",
            self.default_response_delete_delay,
        )
        if delay is not None:
            # Check if the bot has permission to delete messages in the current channel
            if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await asyncio.sleep(
                    0.5
                )  # Short delay to ensure the bot's response is sent

                # Find the bot's latest response after the user's command
                async for response in ctx.channel.history(limit=5, after=ctx.message):
                    if response.author == self.bot.user:
                        try:
                            await asyncio.sleep(delay)  # Wait for the specified delay
                            await response.delete()  # Delete the bot's response
                        except discord.errors.NotFound:
                            pass  # The message was already deleted
                        except discord.errors.Forbidden:
                            print(
                                f"⚠️ No permission to delete bot response in {response.channel}"
                            )
                        except Exception as e:
                            print(f"Unexpected error while deleting bot response: {e}")
                        break  # Stop after deleting the first response


async def setup(bot):
    await bot.add_cog(AutoDelete(bot))
