import discord
from discord.ext import commands
import asyncio


class Purge(commands.Cog):
    """Cog to purge messages from a specific channel."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge_channel", aliases=["clear_channel", "clear"])
    @commands.has_permissions(manage_messages=True)
    async def purge_channel(self, ctx, channel: discord.TextChannel = None):
        """
        Deletes all messages in the specified channel.
        If no channel is specified, it purges the current channel.
        Usage: !purge_channel [channel_name or channel_id]
        """
        # Target the current channel if no channel is specified
        target_channel = channel or ctx.channel

        # Confirm the purge action with the user
        confirm_message = await ctx.send(
            f"⚠️ Are you sure you want to delete all messages in {target_channel.mention}? "
            "This action **cannot be undone**. React with ✅ to confirm or ❌ to cancel."
        )
        await confirm_message.add_reaction("✅")
        await confirm_message.add_reaction("❌")

        # Function to check for the user's reaction
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in ["✅", "❌"]
                and reaction.message.id == confirm_message.id
            )

        try:
            # Wait for the confirmation reaction
            reaction, _ = await self.bot.wait_for(
                "reaction_add", timeout=30.0, check=check
            )
        except asyncio.TimeoutError:
            await confirm_message.delete()
            await ctx.send(
                "⏳ Purge operation cancelled due to timeout.", delete_after=10
            )
            return

        # Cancel the purge if the user reacted with ❌
        if str(reaction.emoji) == "❌":
            await confirm_message.delete()
            await ctx.send("❌ Purge operation cancelled.", delete_after=10)
            return

        # Proceed with the purge if the user reacted with ✅
        await confirm_message.delete()

        # Notify the user that the purge is starting
        status_message = await ctx.send(
            f"🔄 Starting to purge all messages in {target_channel.mention}. This may take some time..."
        )

        deleted_count = 0
        try:
            # Purge messages in batches until all are deleted
            while True:
                deleted = await target_channel.purge(limit=1000)
                deleted_count += len(deleted)
                if len(deleted) < 1000:  # Less than 1000 means no more messages left
                    break

            # Inform the user that the purge was successful
            await status_message.delete()
            await ctx.send(
                f"✅ Successfully deleted {deleted_count} messages in {target_channel.mention}.",
                delete_after=10,
            )

        except discord.errors.Forbidden:
            await status_message.delete()
            await ctx.send(
                "❌ I don't have permission to delete messages in that channel.",
                delete_after=10,
            )
        except discord.errors.HTTPException as e:
            await status_message.delete()
            await ctx.send(
                f"❌ An error occurred while trying to delete messages: {str(e)}",
                delete_after=10,
            )


async def setup(bot):
    await bot.add_cog(Purge(bot))
