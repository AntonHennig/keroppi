import discord
from discord.ext import commands
import asyncio

class AutoDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_delete_delay = 30  # Default delay for bot responses in seconds

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore messages from bots

        # Check if the message is a command
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            # Instantly delete the command message
            if message.guild and message.channel.permissions_for(message.guild.me).manage_messages:
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass  # Message was already deleted
                except discord.errors.Forbidden:
                    print(f"No permission to delete message in {message.channel}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command_failed:
            return  # Don't delete error messages

        if ctx.guild and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await asyncio.sleep(0.5)  # Short delay to allow the bot's response to be sent
            async for response in ctx.channel.history(limit=1, after=ctx.message):
                if response.author == self.bot.user:
                    await asyncio.sleep(self.response_delete_delay)
                    try:
                        await response.delete()
                    except discord.errors.NotFound:
                        pass  # Message was already deleted
                    except discord.errors.Forbidden:
                        print(f"No permission to delete message in {response.channel}")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def set_response_delay(self, ctx, seconds: int):
        """Set the delay for auto-deletion of bot responses."""
        if seconds < 5:
            await ctx.send("Delay must be at least 5 seconds.", delete_after=10)
            return
        self.response_delete_delay = seconds
        await ctx.send(f"Bot response auto-delete delay set to {seconds} seconds.", delete_after=10)

async def setup(bot):
    await bot.add_cog(AutoDelete(bot))