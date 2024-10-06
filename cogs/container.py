import discord
from discord.ext import commands
import docker
from datetime import datetime, timezone
from bot import COMMAND_PREFIX
from decorators import delete_command_message, delete_bot_response


class Container(commands.Cog):
    """A cog for interacting with Docker containers."""

    def __init__(self, bot):
        self.bot = bot
        # Attempt to connect to Docker socket
        try:
            self.client = docker.from_env()
        except docker.errors.DockerException as e:
            self.client = None  # Handling Docker socket connection error
            print(f"Error connecting to Docker: {e}")

    @commands.command(aliases=["ps"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=15)
    async def docker_ps(self, ctx):
        f"""Lists all Docker containers with detailed information.
        *Usage:* `{COMMAND_PREFIX}docker_ps`"""
        if self.client is None:
            await ctx.send(
                "❌ Docker client is not available. Please check Docker connection."
            )
            return
        try:
            # Get lists of running and stopped containers
            running_containers = self.client.containers.list()
            all_containers = self.client.containers.list(all=True)
            stopped_containers = [
                c for c in all_containers if c not in running_containers
            ]

            # Prepare the container info
            running_info = [
                self.format_container_info(container, running=True)
                for container in running_containers
            ]
            stopped_info = [
                self.format_container_info(container, running=False)
                for container in stopped_containers
            ]

            # Combine running and stopped containers
            all_info = running_info + stopped_info

            # Paginate the output
            embeds = self.create_embeds(
                all_info,
                title="📦 Docker Containers",
                footer=f"Total Containers: {len(all_containers)}",
            )

            for embed in embeds:
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

    def format_container_info(self, container, running=True):
        """Formats container information for display."""
        # Get container details
        name = container.name
        image = (
            container.image.tags[0]
            if container.image.tags
            else container.image.short_id
        )
        status = container.status.capitalize()
        uptime = self.get_uptime(container)
        emoji = "🟢" if running else "🔴"
        info = (
            f"{emoji} **Name:** `{name}`\n"
            f"**Image:** `{image}`\n"
            f"**Uptime:** `{uptime}`\n"
            f"**Status:** `{status}`\n"
            "----------------------------------\n"
        )
        return info

    def get_uptime(self, container):
        """Calculates the uptime of the container."""
        try:
            started_at_str = container.attrs["State"]["StartedAt"].replace(
                "Z", "+00:00"
            )
            started_at = datetime.fromisoformat(started_at_str)
            now = datetime.now(timezone.utc)
            delta = now - started_at

            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            uptime = f"{days}d {hours}h {minutes}m"
            return uptime
        except Exception:
            return "N/A"

    def create_embeds(self, info_list, title, footer):
        """Creates a list of embeds to paginate the container info."""
        embeds = []
        embed = discord.Embed(title=title, color=discord.Color.blue())
        description = ""

        for info in info_list:
            if len(description) + len(info) > 2048:
                # If adding the next info exceeds the limit, start a new embed
                embed.description = description
                embed.set_footer(text=footer)
                embeds.append(embed)
                embed = discord.Embed(title=title, color=discord.Color.blue())
                description = info
            else:
                description += info

        # Add the last embed
        if description:
            embed.description = description
            embed.set_footer(text=footer)
            embeds.append(embed)

        return embeds

    @commands.command(aliases=["start"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def docker_start(self, ctx):
        """Starts a stopped Docker container interactively."""
        await self.manage_container(ctx, action="start")

    @commands.command(aliases=["stop"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def docker_stop(self, ctx):
        """Stops a running Docker container interactively."""
        await self.manage_container(ctx, action="stop")

    @commands.command(aliases=["restart"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def docker_restart(self, ctx):
        """Restarts a Docker container interactively."""
        await self.manage_container(ctx, action="restart")

    @commands.command(aliases=["rm", "remove"])
    @delete_command_message(delay=0)
    @delete_bot_response(delay=10)
    async def docker_rm(self, ctx):
        """Removes a Docker container interactively."""
        await self.manage_container(ctx, action="remove")

    async def manage_container(self, ctx, action):
        """Helper method to manage containers interactively using select menus."""
        if self.client is None:
            await ctx.send(
                "❌ Docker client is not available. Please check Docker connection."
            )
            return

        # Determine the status filter based on action
        if action == "start":
            containers = self.client.containers.list(
                all=True, filters={"status": "exited"}
            )
        else:
            containers = self.client.containers.list()

        if not containers:
            await ctx.send(f"🛑 No containers available to {action}.")
            return

        # Sort containers by name
        containers.sort(key=lambda x: x.name)

        # Create select options
        options = [
            discord.SelectOption(
                label=f"{container.name} ({container.status})", value=container.name
            )
            for container in containers
        ]

        # Limit options to 25 (Discord's limit per select menu)
        if len(options) > 25:
            options = options[:25]

        # Define the view with a select menu
        class ContainerSelectView(discord.ui.View):
            def __init__(self, options, client, action, ctx, timeout=60):
                super().__init__(timeout=timeout)
                self.container_name = None
                self.client = client
                self.action = action
                self.ctx = ctx

                self.select = discord.ui.Select(
                    placeholder=f"Select a container to {action.capitalize()}",
                    options=options,
                    min_values=1,
                    max_values=1,
                )
                self.select.callback = self.select_callback
                self.add_item(self.select)

            async def select_callback(self, interaction: discord.Interaction):
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "❌ You are not authorized to perform this action.",
                        ephemeral=True,
                    )
                    return
                self.container_name = self.select.values[0]
                await interaction.response.defer()
                container = self.client.containers.get(self.container_name)
                try:
                    if self.action == "start":
                        container.start()
                        await interaction.followup.send(
                            f"▶️ Container `{container.name}` has been started.",
                            ephemeral=False,
                        )
                    elif self.action == "stop":
                        container.stop()
                        await interaction.followup.send(
                            f"⏹️ Container `{container.name}` has been stopped.",
                            ephemeral=False,
                        )
                    elif self.action == "restart":
                        container.restart()
                        await interaction.followup.send(
                            f"🔄 Container `{container.name}` has been restarted.",
                            ephemeral=False,
                        )
                    elif self.action == "remove":
                        container.remove(force=True)
                        await interaction.followup.send(
                            f"🗑️ Container `{container.name}` has been removed.",
                            ephemeral=False,
                        )
                except Exception as e:
                    await interaction.followup.send(
                        f"⚠️ An error occurred: {e}", ephemeral=False
                    )
                self.stop()  # Stop the view after the operation

        view = ContainerSelectView(options, self.client, action, ctx)
        embed = discord.Embed(
            title=f"Select a container to {action.capitalize()}",
            color=discord.Color.blue(),
        )
        message = await ctx.send(embed=embed, view=view)

        await view.wait()
        if view.container_name is None:
            await message.delete()
            await ctx.send(
                "⏰ You took too long to respond. Please try again.", delete_after=5
            )
        else:
            await message.delete()


async def setup(bot):
    await bot.add_cog(Container(bot))
