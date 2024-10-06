import discord
from discord.ext import commands
from discord import ui
import asyncio
import datetime
from typing import List
from decorators import delete_command_message, delete_bot_response
import os
import pytz

# Read the TIMEZONE from environment variable or default to 'Europe/Berlin'
TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin")
user_tz = pytz.timezone(TIMEZONE)


class ScheduledMessage:

    _id_counter = 1  # Class variable for assigning unique IDs

    def __init__(self, author_id, channel_id, schedule_time, content):
        self.id = ScheduledMessage._id_counter
        ScheduledMessage._id_counter += 1

        self.author_id = author_id
        self.channel_id = channel_id
        self.schedule_time = schedule_time
        self.content = content

        self.task = None  # Will hold the asyncio task


class Msg(
    commands.Cog,
    description="Commands for managing messages, including purging, saving, pinning, and scheduling.",
):
    def __init__(self, bot):
        self.bot = bot
        self.archive_channel = None  # archive chnanel object
        self.sticky_messages = {}  # Dictionary of syicky messages per channel
        self.scheduled_messages: List[ScheduledMessage] = (
            []
        )  # List to store scheduled messages

    # --------------------------------------
    # Archive commands
    # --------------------------------------
    @commands.command(name="set_archive_channel", aliases=["set_archive"])
    @commands.has_permissions(manage_channels=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def set_archive_channel(self, ctx, channel: discord.TextChannel = None):
        """Sets the archive channel where saved messages will be stored.

        **Usage:**
        `!set_archive_channel <channel>`

        **Example:**
        `!set_archive_channel #archive`
        """
        if channel is None:
            await ctx.send(
                "❌ Please mention a channel to set as the archive channel.",
                delete_after=10,
            )
            return

        self.archive_channel = channel
        await ctx.send(f"✅ Archive channel set to {channel.mention}", delete_after=10)

    @commands.command(name="save_msg", aliases=["archive_msg"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def save_message(self, ctx, message_id: int = None):
        """Saves a message by its ID to the configured archive channel.

        **Usage:**
        `!save_message <message_id>`

        **Example:**
        `!save_message 123456789012345678`
        """
        if message_id is None:
            await ctx.send("❌ Please provide a message ID to save.", delete_after=10)
            return

        if not self.archive_channel:
            await ctx.send(
                "❌ Archive channel is not set. Use `!set_archive_channel <channel>`.",
                delete_after=10,
            )
            return

        try:
            # Fetch the message from the current channel
            message = await ctx.channel.fetch_message(message_id)

            # Create an embed to represent the saved message
            embed = discord.Embed(
                description=message.content or "[No Text Content]",
                timestamp=message.created_at,
                color=discord.Color.blue(),
            )
            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )
            embed.set_footer(text=f"Saved from #{ctx.channel.name}")

            # Include attachments if any
            if message.attachments:
                embed.add_field(
                    name="Attachments",
                    value="\n".join(
                        attachment.url for attachment in message.attachments
                    ),
                    inline=False,
                )

            # Send the embed to the archive channel
            await self.archive_channel.send(embed=embed)
            await ctx.send(
                f"📌 Message saved to {self.archive_channel.mention}.",
                delete_after=10,
            )
        except discord.NotFound:
            await ctx.send(
                "❌ Message not found. Please ensure the ID is correct and the message is in this channel.",
                delete_after=10,
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to access that message or channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {e}", delete_after=10)

    @commands.command(name="pin_msg", aliases=["pin"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def pin_message(self, ctx, message_id: int = None):
        """Pins or unpins a message by its ID.

        **Usage:**
        `!pin_message <message_id>`

        **Example:**
        `!pin_message 123456789012345678`

        """
        if message_id is None:
            await ctx.send(
                "❌ Please provide a message ID to pin or unpin.", delete_after=10
            )
            return

        try:
            message = await ctx.channel.fetch_message(message_id)
            if message.pinned:
                await message.unpin()
                await ctx.send(f"📌 Message unpinned.", delete_after=10)
            else:
                await message.pin()
                await ctx.send(f"📌 Message pinned.", delete_after=10)
        except discord.NotFound:
            await ctx.send(
                "❌ Message not found. Please ensure the ID is correct and the message is in this channel.",
                delete_after=10,
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to pin messages in this channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {e}", delete_after=10)

    # --------------------------------------
    # Sticky Commands
    # --------------------------------------
    @commands.command(name="sticky_msg", aliases=["sticky", "stepbro"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def sticky_message(self, ctx, message_id: int = None):
        """Keeps a specified message at the bottom of the channel by deleting and reposting it.

        **Usage:**
        `!sticky_message <message_id>`

        **Example:**
        `!sticky_message 123456789012345678`
        """
        if message_id is None:
            await ctx.send(
                "❌ Please provide the message ID of the message you want to make sticky.",
                delete_after=10,
            )
            return

        channel = ctx.channel

        # Check if there's already a sticky message in this channel
        if channel.id in self.sticky_messages:
            await ctx.send(
                "⚠️ A sticky message is already active in this channel. Use `!stop_sticky` to stop it first.",
                delete_after=10,
            )
            return

        try:
            # Fetch the message to make sticky
            original_message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send(
                "❌ Message not found. Please ensure the ID is correct and the message is in this channel.",
                delete_after=10,
            )
            return
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to access that message.", delete_after=10
            )
            return
        except discord.HTTPException as e:
            await ctx.send(f"❌ An error occurred: {e}", delete_after=10)
            return

        # Send the initial sticky message
        try:
            sticky_msg = await channel.send(
                content=original_message.content, embeds=original_message.embeds
            )
        except discord.HTTPException as e:
            await ctx.send(
                f"❌ Failed to send the sticky message: {e}", delete_after=10
            )
            return

        self.sticky_messages[channel.id] = sticky_msg

        def check(message):
            return message.channel == channel and message.id != sticky_msg.id

        try:
            while True:
                # Wait for any new message in the channel
                await self.bot.wait_for("message", check=check)
                try:
                    # Delete the old sticky message and resend it
                    await sticky_msg.delete()
                    sticky_msg = await channel.send(
                        content=original_message.content, embeds=original_message.embeds
                    )
                    self.sticky_messages[channel.id] = sticky_msg
                except discord.HTTPException as e:
                    print(f"Error updating sticky message: {e}")
                    break
        except asyncio.CancelledError:
            # Cleanup when the sticky message is stopped
            await sticky_msg.delete()
            del self.sticky_messages[channel.id]
        except Exception as e:
            print(f"Unexpected error in sticky message: {e}")
            await sticky_msg.delete()
            del self.sticky_messages[channel.id]

    @commands.command(name="stop_sticky", aliases=["unsticky"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def stop_sticky(self, ctx):
        """Stops the sticky message in the current channel.

        **Usage:**
        `!stop_sticky`

        **Example:**
        `!stop_sticky`
        """
        channel = ctx.channel
        if channel.id in self.sticky_messages:
            await self.sticky_messages[channel.id].delete()
            del self.sticky_messages[channel.id]
            await ctx.send("✅ Sticky message stopped.", delete_after=10)
        else:
            await ctx.send(
                "❌ No sticky message is active in this channel.", delete_after=10
            )

    # --------------------------------------
    # Broadcast and schedule commands
    # --------------------------------------
    @commands.command(name="bulk_msg", aliases=["broadcast"])
    @commands.has_permissions(manage_channels=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def bulk_message(
        self, ctx, message_content: str = None, *channels: discord.TextChannel
    ):
        """Sends a predefined message to multiple channels.

        **Usage:**
        `!bulk_message <message_content> <channel1> [channel2] ...`

        **Example:**
        `!bulk_message "Server maintenance at 10 PM" #general #announcements`
        """
        if message_content is None:
            await ctx.send(
                "❌ Please provide the message content to send.", delete_after=10
            )
            return

        if not channels:
            await ctx.send("❌ Please specify at least one channel.", delete_after=10)
            return

        for channel in channels:
            try:
                await channel.send(message_content)
            except discord.Forbidden:
                await ctx.send(
                    f"❌ I don't have permission to send messages in {channel.mention}.",
                    delete_after=10,
                )
            except discord.HTTPException as e:
                await ctx.send(
                    f"❌ An error occurred in {channel.mention}: {e}", delete_after=10
                )

        await ctx.send(f"✅ Message sent to {len(channels)} channels.", delete_after=10)

    @commands.command(name="schedule_msg", aliases=["schedule"])
    @commands.has_permissions(manage_channels=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=15)
    async def schedule_message(self, ctx):
        """Schedules a message to be sent to a channel at a specific time.

        **Usage:**
        `!schedule_message`
        """
        # Step 1: Select Channel
        channels = [
            channel
            for channel in ctx.guild.text_channels
            if channel.permissions_for(ctx.author).send_messages
        ]
        if not channels:
            await ctx.send(
                "❌ You don't have permission to send messages in any channels.",
                delete_after=10,
            )
            return

        class ChannelSelectView(ui.View):
            def __init__(self, channels, timeout=60):
                super().__init__(timeout=timeout)
                self.channel_id = None

                options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in channels[:25]
                ]

                self.select = ui.Select(
                    placeholder="Select a channel...", options=options
                )
                self.select.callback = self.select_callback
                self.add_item(self.select)

            async def select_callback(self, interaction: discord.Interaction):
                self.channel_id = int(self.select.values[0])
                self.stop()
                await interaction.response.defer()

        channel_select_view = ChannelSelectView(channels)
        channel_select_message = await ctx.send(
            "📢 Please select a channel to send the message in:",
            view=channel_select_view,
        )
        await channel_select_view.wait()

        if channel_select_view.channel_id is None:
            await channel_select_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return

        target_channel = self.bot.get_channel(channel_select_view.channel_id)
        await channel_select_message.edit(
            content=f"Selected channel: {target_channel.mention}", view=None
        )

        # Step 2: Select Date
        class DateSelectView(ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.selected_date = None

                today = datetime.datetime.now(user_tz).date()
                options = [
                    discord.SelectOption(
                        label=(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d"),
                        value=(today + datetime.timedelta(days=i)).isoformat(),
                    )
                    for i in range(7)  # Next 7 days
                ]

                self.select = ui.Select(placeholder="Select a date...", options=options)
                self.select.callback = self.select_callback
                self.add_item(self.select)

            async def select_callback(self, interaction: discord.Interaction):
                self.selected_date = self.select.values[0]
                self.stop()
                await interaction.response.defer()

        date_select_view = DateSelectView()
        date_select_message = await ctx.send(
            f"📅 Please select a date (Time Zone: {TIMEZONE}):", view=date_select_view
        )
        await date_select_view.wait()

        if date_select_view.selected_date is None:
            await date_select_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return

        selected_date = date_select_view.selected_date
        await date_select_message.edit(
            content=f"Selected date: {selected_date}", view=None
        )

        # Step 3: Select Hour
        class HourSelectView(ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.selected_hour = None

                options = [
                    discord.SelectOption(label=f"{hour:02d}:00", value=str(hour))
                    for hour in range(24)
                ]

                self.select = ui.Select(
                    placeholder=f"Select an hour ({TIMEZONE})...", options=options
                )
                self.select.callback = self.select_callback
                self.add_item(self.select)

            async def select_callback(self, interaction: discord.Interaction):
                self.selected_hour = int(self.select.values[0])
                self.stop()
                await interaction.response.defer()

        hour_select_view = HourSelectView()
        hour_select_message = await ctx.send(
            f"⏰ Please select an hour ({TIMEZONE}):", view=hour_select_view
        )
        await hour_select_view.wait()

        if hour_select_view.selected_hour is None:
            await hour_select_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return

        selected_hour = hour_select_view.selected_hour
        await hour_select_message.edit(
            content=f"Selected hour: {selected_hour:02d}:00 {TIMEZONE}", view=None
        )

        # Step 4: Select Minute
        class MinuteSelectView(ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.selected_minute = None

                options = [
                    discord.SelectOption(
                        label=f"{minute:02d} minutes", value=str(minute)
                    )
                    for minute in [0, 15, 30, 45]
                ]

                self.select = ui.Select(
                    placeholder="Select minutes...", options=options
                )
                self.select.callback = self.select_callback
                self.add_item(self.select)

            async def select_callback(self, interaction: discord.Interaction):
                self.selected_minute = int(self.select.values[0])
                self.stop()
                await interaction.response.defer()

        minute_select_view = MinuteSelectView()
        minute_select_message = await ctx.send(
            "⏰ Please select minutes:", view=minute_select_view
        )
        await minute_select_view.wait()

        if minute_select_view.selected_minute is None:
            await minute_select_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return

        selected_minute = minute_select_view.selected_minute
        await minute_select_message.edit(
            content=f"Selected time: {selected_hour:02d}:{selected_minute:02d} {TIMEZONE}",
            view=None,
        )

        # Step 5: Enter Message Content
        await ctx.send("💬 Please enter the message content:", delete_after=300)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            message_content_msg = await self.bot.wait_for(
                "message", timeout=300.0, check=check
            )
            message_content = message_content_msg.content
            await message_content_msg.delete()
        except asyncio.TimeoutError:
            await ctx.send("⏳ Operation cancelled due to timeout.", delete_after=10)
            return

        # Step 6: Confirm Scheduling
        class ConfirmScheduleView(ui.View):
            def __init__(self, timeout=60):
                super().__init__(timeout=timeout)
                self.value = None

            @ui.button(label="Confirm", style=discord.ButtonStyle.success)
            async def confirm(
                self, interaction: discord.Interaction, button: ui.Button
            ):
                self.value = True
                self.stop()
                await interaction.response.defer()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction: discord.Interaction, button: ui.Button):
                self.value = False
                self.stop()
                await interaction.response.defer()

        confirm_view = ConfirmScheduleView()
        scheduled_time_str = f"{selected_hour:02d}:{selected_minute:02d}"
        confirm_message = await ctx.send(
            f"📋 **Please confirm the scheduled message:**\n"
            f"**Channel:** {target_channel.mention}\n"
            f"**Date:** {selected_date}\n"
            f"**Time:** {scheduled_time_str} {TIMEZONE}\n"
            f"**Message:** {message_content}",
            view=confirm_view,
        )
        await confirm_view.wait()

        if confirm_view.value is None:
            await confirm_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return
        elif confirm_view.value is False:
            await confirm_message.edit(content="❌ Scheduling cancelled.", view=None)
            return

        await confirm_message.edit(content="⏳ Message scheduled.", view=None)

        # Step 7: Schedule the Message
        try:
            schedule_datetime_str = f"{selected_date} {scheduled_time_str}"
            # Parse the scheduled time in user's timezone
            schedule_time = datetime.datetime.strptime(
                schedule_datetime_str, "%Y-%m-%d %H:%M"
            )
            schedule_time = user_tz.localize(schedule_time)
            # Convert to UTC for storage and calculation
            schedule_time_utc = schedule_time.astimezone(pytz.utc)
            current_time_utc = datetime.datetime.now(pytz.utc)
            delay = (schedule_time_utc - current_time_utc).total_seconds()

            if delay <= 0:
                await ctx.send(
                    "❌ The scheduled time is in the past or too soon.", delete_after=10
                )
                return

            # Create a ScheduledMessage instance
            scheduled_message = ScheduledMessage(
                author_id=ctx.author.id,
                channel_id=target_channel.id,
                schedule_time=schedule_time_utc,
                content=message_content,
            )

            # Schedule the message
            scheduled_message.task = self.bot.loop.create_task(
                self.send_scheduled_message(scheduled_message)
            )

            # Add to the list of scheduled messages
            self.scheduled_messages.append(scheduled_message)

            await ctx.send(
                f"⏳ Message scheduled for {schedule_time.strftime('%Y-%m-%d %H:%M %Z')} with ID `{scheduled_message.id}`.",
                delete_after=10,
            )

        except Exception as e:
            await ctx.send(f"❌ An unexpected error occurred: {e}", delete_after=10)

    async def send_scheduled_message(self, scheduled_message: ScheduledMessage):
        """Sends the scheduled message at the appropriate time."""
        delay = (
            scheduled_message.schedule_time - datetime.datetime.now(pytz.utc)
        ).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)

        channel = self.bot.get_channel(scheduled_message.channel_id)
        if channel:
            try:
                await channel.send(scheduled_message.content)
                # Remove the scheduled message after sending
                self.scheduled_messages.remove(scheduled_message)
            except Exception as e:
                print(
                    f"Failed to send scheduled message ID {scheduled_message.id}: {e}"
                )
        else:
            print(f"Channel with ID {scheduled_message.channel_id} not found.")

    @commands.command(name="show_scheduled_msgs", aliases=["list_scheduled_msgs"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def show_scheduled_msgs(self, ctx):
        """Shows the list of scheduled messages.

        **Usage:**
        `!show_scheduled_msgs`
        """
        if not self.scheduled_messages:
            await ctx.send("ℹ️ There are no scheduled messages.", delete_after=10)
            return

        # Create a list of messages to display
        message_lines = []
        for msg in self.scheduled_messages:
            author = self.bot.get_user(msg.author_id)
            channel = self.bot.get_channel(msg.channel_id)
            # Convert schedule_time from UTC to user's timezone
            time_in_user_tz = msg.schedule_time.astimezone(user_tz)
            time_str = time_in_user_tz.strftime(f"%Y-%m-%d %H:%M {TIMEZONE}")
            message_lines.append(
                f"**ID:** `{msg.id}` | **Time:** {time_str} | **Channel:** {channel.mention if channel else 'Unknown'} | **Author:** {author.mention if author else 'Unknown'}"
            )

        # Combine messages into chunks within Discord's character limit
        max_length = 2000
        chunks = []
        current_chunk = ""
        for line in message_lines:
            if len(current_chunk) + len(line) + 1 > max_length:
                chunks.append(current_chunk)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk)

        # Send the chunks
        for chunk in chunks:
            await ctx.send(chunk)

    @commands.command(
        name="cancel_scheduled_message", aliases=["cancel_scheduled", "cancel_message"]
    )
    @commands.has_permissions(manage_channels=True)
    @delete_command_message(delay=0)
    async def cancel_scheduled_message(self, ctx, message_id: int = None):
        """Cancels a scheduled message by its ID.

        **Usage:**
        `!cancel_scheduled_message <message_id>`

        **Example:**
        `!cancel_scheduled_message 1`
        """
        if message_id is None:
            await ctx.send(
                "❌ Please provide the ID of the scheduled message to cancel.",
                delete_after=10,
            )
            return

        # Find the scheduled message
        scheduled_message = next(
            (msg for msg in self.scheduled_messages if msg.id == message_id), None
        )

        if scheduled_message is None:
            await ctx.send(
                f"❌ No scheduled message found with ID `{message_id}`.",
                delete_after=10,
            )
            return

        # Cancel the task
        scheduled_message.task.cancel()
        self.scheduled_messages.remove(scheduled_message)
        await ctx.send(
            f"✅ Scheduled message with ID `{message_id}` has been cancelled.",
            delete_after=10,
        )

    # --------------------------------------
    # Purge Commands
    # --------------------------------------

    @commands.command(name="purge_channel", aliases=["clear_channel", "clear"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def purge_channel(self, ctx, channel: discord.TextChannel = None):
        """Deletes all messages in the specified channel.

        **Usage:**
        `!purge_channel [channel]`

        **Example:**
        `!purge_channel #general`
        """
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

        if str(reaction.emoji) == "❌":
            await confirm_message.delete()
            await ctx.send("❌ Purge operation cancelled.", delete_after=10)
            return

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
                if len(deleted) < 1000:
                    break

            await status_message.delete()
            await ctx.send(
                f"✅ Successfully deleted {deleted_count} messages in {target_channel.mention}.",
                delete_after=10,
            )
        except discord.Forbidden:
            await status_message.delete()
            await ctx.send(
                "❌ I don't have permission to delete messages in that channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await status_message.delete()
            await ctx.send(
                f"❌ An error occurred while trying to delete messages: {e}",
                delete_after=10,
            )

    @commands.command(name="purge_channel", aliases=["clear_channel", "clear"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def purge_channel(self, ctx, channel: discord.TextChannel = None):
        """Deletes all messages in the specified channel.

        **Usage:**
        `!purge_channel [channel]`

        **Example:**
        `!purge_channel #general`
        """
        target_channel = channel or ctx.channel

        # Confirm the purge action with the user using buttons
        class ConfirmPurgeView(ui.View):
            def __init__(self, timeout=30):
                super().__init__(timeout=timeout)
                self.value = None

            @ui.button(label="Confirm", style=discord.ButtonStyle.danger)
            async def confirm(
                self, button: ui.Button, interaction: discord.Interaction
            ):
                self.value = True
                self.stop()
                await interaction.response.defer()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button: ui.Button, interaction: discord.Interaction):
                self.value = False
                self.stop()
                await interaction.response.defer()

        confirm_view = ConfirmPurgeView()

        confirm_message = await ctx.send(
            f"⚠️ Are you sure you want to delete **all messages** in {target_channel.mention}? This action **cannot be undone**.",
            view=confirm_view,
        )

        # Wait for the user's response
        await confirm_view.wait()

        if confirm_view.value is None:
            await confirm_message.edit(
                content="⏳ Purge operation cancelled due to timeout.", view=None
            )
            return
        elif confirm_view.value is False:
            await confirm_message.edit(
                content="❌ Purge operation cancelled.", view=None
            )
            return

        # Proceed with the purge
        await confirm_message.edit(content="🔄 Purging all messages...", view=None)

        try:
            # Bulk delete messages
            deleted_count = 0
            while True:
                deleted = await target_channel.purge(limit=1000)
                deleted_count += len(deleted)
                if len(deleted) < 1000:
                    break

            await confirm_message.edit(
                content=f"✅ Successfully deleted {deleted_count} messages in {target_channel.mention}."
            )
        except discord.Forbidden:
            await confirm_message.edit(
                content="❌ I don't have permission to delete messages in that channel."
            )
        except discord.HTTPException as e:
            await confirm_message.edit(
                content=f"❌ An error occurred while trying to delete messages: {e}"
            )

    # --------------------------------------
    # Command: purge_messages
    # --------------------------------------
    @commands.command(name="purge_messages", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def purge_messages(self, ctx):
        """Deletes a specified number of messages in the current channel.

        **Usage:**
        `!purge_messages`

        **Example:**
        `!purge_messages`

        After invoking the command, you'll be prompted to enter the number of messages to delete.
        """

        # Ask the user for the number of messages to delete
        await ctx.send(
            "📝 Please enter the number of messages to delete:", delete_after=30
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            amount = int(msg.content)
            await msg.delete()

            if amount <= 0:
                await ctx.send(
                    "❌ Please specify a positive number of messages to delete.",
                    delete_after=10,
                )
                return

            # Confirm the purge action with the user using buttons
            class ConfirmPurgeView(ui.View):
                def __init__(self, timeout=30):
                    super().__init__(timeout=timeout)
                    self.value = None

                @ui.button(label="Confirm", style=discord.ButtonStyle.danger)
                async def confirm(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = True
                    self.stop()
                    await interaction.response.defer()

                @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = False
                    self.stop()
                    await interaction.response.defer()

            confirm_view = ConfirmPurgeView()

            confirm_message = await ctx.send(
                f"⚠️ Are you sure you want to delete the last **{amount} messages** in {ctx.channel.mention}?",
                view=confirm_view,
            )

            # Wait for the user's response
            await confirm_view.wait()

            if confirm_view.value is None:
                await confirm_message.edit(
                    content="⏳ Purge operation cancelled due to timeout.", view=None
                )
                return
            elif confirm_view.value is False:
                await confirm_message.edit(
                    content="❌ Purge operation cancelled.", view=None
                )
                return

            # Proceed with the purge
            await confirm_message.edit(content="🔄 Purging messages...", view=None)

            deleted = await ctx.channel.purge(
                limit=amount + 2
            )  # +2 to include command messages
            await ctx.send(f"✅ Deleted {len(deleted) - 2} messages.", delete_after=10)
        except asyncio.TimeoutError:
            await ctx.send("⏳ Operation cancelled due to timeout.", delete_after=10)
        except ValueError:
            await ctx.send(
                "❌ Invalid number. Please enter a valid integer.", delete_after=10
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to delete messages in this channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await ctx.send(
                f"❌ An error occurred while trying to delete messages: {e}",
                delete_after=10,
            )

    # --------------------------------------
    # Command: purge_user_messages
    # --------------------------------------
    @commands.command(name="purge_user", aliases=["purge_by_user"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def purge_user_messages(self, ctx):
        """Deletes messages from a specific user in the current channel.

        **Usage:**
        `!purge_user`

        **Example:**
        `!purge_user`

        After invoking the command, you'll be prompted to select a user and specify the number of messages to delete.
        """

        # Get the list of members who have sent messages in the channel
        messages = await ctx.channel.history(limit=100).flatten()
        users = list({msg.author for msg in messages})

        if not users:
            await ctx.send("❌ No users found in the recent messages.", delete_after=10)
            return

        # Create a select menu for users
        options = [
            discord.SelectOption(label=user.display_name, value=str(user.id))
            for user in users[:25]  # Max options for select menu is 25
        ]

        class UserSelectView(ui.View):
            def __init__(self, timeout=30):
                super().__init__(timeout=timeout)
                self.user_id = None

            @ui.select(
                placeholder="Select a user to purge messages from...", options=options
            )
            async def select_user(
                self, select: ui.Select, interaction: discord.Interaction
            ):
                self.user_id = int(select.values[0])
                self.stop()
                await interaction.response.defer()

        user_select_view = UserSelectView()

        select_message = await ctx.send(
            "👤 Please select a user:", view=user_select_view
        )
        await user_select_view.wait()

        if user_select_view.user_id is None:
            await select_message.edit(
                content="⏳ Operation cancelled due to timeout.", view=None
            )
            return

        # Get the selected user
        user = ctx.guild.get_member(user_select_view.user_id)
        await select_message.edit(content=f"Selected user: {user.mention}", view=None)

        # Ask for the amount
        await ctx.send(
            "📝 Please enter the number of messages to delete from this user:",
            delete_after=30,
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            amount_msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            amount = int(amount_msg.content)
            await amount_msg.delete()

            if amount <= 0:
                await ctx.send(
                    "❌ Please specify a positive number of messages to delete.",
                    delete_after=10,
                )
                return

            # Confirm the purge action with the user using buttons
            class ConfirmPurgeView(ui.View):
                def __init__(self, timeout=30):
                    super().__init__(timeout=timeout)
                    self.value = None

                @ui.button(label="Confirm", style=discord.ButtonStyle.danger)
                async def confirm(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = True
                    self.stop()
                    await interaction.response.defer()

                @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = False
                    self.stop()
                    await interaction.response.defer()

            confirm_view = ConfirmPurgeView()

            confirm_message = await ctx.send(
                f"⚠️ Are you sure you want to delete the last **{amount} messages** from {user.mention} in {ctx.channel.mention}?",
                view=confirm_view,
            )

            # Wait for the user's response
            await confirm_view.wait()

            if confirm_view.value is None:
                await confirm_message.edit(
                    content="⏳ Purge operation cancelled due to timeout.", view=None
                )
                return
            elif confirm_view.value is False:
                await confirm_message.edit(
                    content="❌ Purge operation cancelled.", view=None
                )
                return

            # Proceed with the purge
            await confirm_message.edit(content="🔄 Purging messages...", view=None)

            def message_check(msg):
                return msg.author == user

            deleted = await ctx.channel.purge(limit=amount, check=message_check)
            await ctx.send(
                f"✅ Deleted {len(deleted)} messages from {user.mention}.",
                delete_after=10,
            )
        except asyncio.TimeoutError:
            await ctx.send("⏳ Operation cancelled due to timeout.", delete_after=10)
        except ValueError:
            await ctx.send(
                "❌ Invalid number. Please enter a valid integer.", delete_after=10
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to delete messages in this channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await ctx.send(
                f"❌ An error occurred while trying to delete messages: {e}",
                delete_after=10,
            )

    # --------------------------------------
    # Command: purge_contains
    # --------------------------------------
    @commands.command(name="purge_contains", aliases=["purge_keyword"])
    @commands.has_permissions(manage_messages=True)
    @delete_command_message(delay=0)
    async def purge_contains(self, ctx):
        """Deletes messages containing a specific keyword in the current channel.

        **Usage:**
        `!purge_contains`

        **Example:**
        `!purge_contains`

        After invoking the command, you'll be prompted to enter the keyword and specify the number of messages to search.
        """

        # Ask for the keyword
        await ctx.send("🔍 Please enter the keyword to search for:", delete_after=30)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            keyword_msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            keyword = keyword_msg.content.strip()
            await keyword_msg.delete()

            if not keyword:
                await ctx.send("❌ Please provide a valid keyword.", delete_after=10)
                return

            # Ask for the amount
            await ctx.send(
                "📝 Please enter the number of messages to search:", delete_after=30
            )

            amount_msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            amount = int(amount_msg.content)
            await amount_msg.delete()

            if amount <= 0:
                await ctx.send(
                    "❌ Please specify a positive number of messages to search.",
                    delete_after=10,
                )
                return

            # Confirm the purge action with the user using buttons
            class ConfirmPurgeView(ui.View):
                def __init__(self, timeout=30):
                    super().__init__(timeout=timeout)
                    self.value = None

                @ui.button(label="Confirm", style=discord.ButtonStyle.danger)
                async def confirm(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = True
                    self.stop()
                    await interaction.response.defer()

                @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
                async def cancel(
                    self, button: ui.Button, interaction: discord.Interaction
                ):
                    self.value = False
                    self.stop()
                    await interaction.response.defer()

            confirm_view = ConfirmPurgeView()

            confirm_message = await ctx.send(
                f"⚠️ Are you sure you want to delete messages containing `{keyword}` in the last {amount} messages in {ctx.channel.mention}?",
                view=confirm_view,
            )

            # Wait for the user's response
            await confirm_view.wait()

            if confirm_view.value is None:
                await confirm_message.edit(
                    content="⏳ Purge operation cancelled due to timeout.", view=None
                )
                return
            elif confirm_view.value is False:
                await confirm_message.edit(
                    content="❌ Purge operation cancelled.", view=None
                )
                return

            # Proceed with the purge
            await confirm_message.edit(content="🔄 Purging messages...", view=None)

            def message_check(msg):
                return keyword.lower() in msg.content.lower()

            deleted = await ctx.channel.purge(limit=amount, check=message_check)
            await ctx.send(
                f"✅ Deleted {len(deleted)} messages containing `{keyword}`.",
                delete_after=10,
            )
        except asyncio.TimeoutError:
            await ctx.send("⏳ Operation cancelled due to timeout.", delete_after=10)
        except ValueError:
            await ctx.send(
                "❌ Invalid number. Please enter a valid integer.", delete_after=10
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ I don't have permission to delete messages in this channel.",
                delete_after=10,
            )
        except discord.HTTPException as e:
            await ctx.send(
                f"❌ An error occurred while trying to delete messages: {e}",
                delete_after=10,
            )


async def setup(bot):
    await bot.add_cog(Msg(bot))
