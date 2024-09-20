import discord
from discord.ext import commands
import asyncio


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge_channel", aliases=["clear_channel", "clear", "del"])
    @commands.has_permissions(manage_messages=True)
    async def purge_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Deletes all messages in the specified channel.
        Usage: !purge_channel [channel_name or channel_id]
        If no channel is specified, it will target the current channel.
        """
        # If no channel is provided, use the current channel
        target_channel = channel or ctx.channel

        # Confirm action with the user
        confirm_message = await ctx.send(
            f"Are you sure you want to delete all messages in {target_channel.mention}? "
            f"This action cannot be undone. React with ✅ to confirm or ❌ to cancel."
        )
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message == confirm_message
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=30.0, check=check
            )
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.send("Purge operation cancelled due to timeout.", delete_after=10)
            return

        if str(reaction.emoji) == "❌":
            await confirm_message.delete()
            await ctx.send("Purge operation cancelled.", delete_after=10)
            return

        await confirm_message.delete()

        # Inform the user that the purge is starting
        status_message = await ctx.send(
            f"Starting to purge all messages in {target_channel.mention}. This may take a while..."
        )

        deleted_count = 0
        try:
            while True:
                deleted = await target_channel.purge(limit=100)
                deleted_count += len(deleted)
                if len(deleted) < 100:
                    break

            await status_message.delete()
            await ctx.send(
                f"Successfully deleted {deleted_count} messages in {target_channel.mention}.",
                delete_after=10,
            )

        except discord.errors.Forbidden:
            await status_message.delete()
            await ctx.send(
                "I don't have permission to delete messages in that channel.",
                delete_after=10,
            )
        except discord.errors.HTTPException as e:
            await status_message.delete()
            await ctx.send(
                f"An error occurred while trying to delete messages: {str(e)}",
                delete_after=10,
            )


async def setup(bot):
    await bot.add_cog(Purge(bot))
