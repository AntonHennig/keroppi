import discord
from discord.ext import commands
import docker
import asyncio
from datetime import datetime, timezone


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
    async def docker_ps(self, ctx):
        """Lists all Docker containers with detailed information."""
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

            embed = discord.Embed(
                title="📦 Docker Containers", color=discord.Color.blue()
            )

            if running_containers:
                running_info = ""
                for container in running_containers:
                    running_info += self.format_container_info(container)
                embed.add_field(
                    name="🟢 Running Containers", value=running_info, inline=False
                )
            else:
                embed.add_field(
                    name="🟢 Running Containers", value="None", inline=False
                )

            if stopped_containers:
                stopped_info = ""
                for container in stopped_containers:
                    stopped_info += self.format_container_info(container)
                embed.add_field(
                    name="🔴 Stopped Containers", value=stopped_info, inline=False
                )
            else:
                embed.add_field(
                    name="🔴 Stopped Containers", value="None", inline=False
                )

            embed.set_footer(text=f"Total Containers: {len(all_containers)}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

    def format_container_info(self, container):
        """Formats container information for display."""
        # Get container details
        name = container.name
        image = (
            container.image.tags[0]
            if container.image.tags
            else container.image.short_id
        )

        # Correctly parse the 'Created' timestamp
        created_str = container.attrs["Created"].replace("Z", "+00:00")
        created = datetime.fromisoformat(created_str)

        uptime = self.get_uptime(container)

        info = (
            f"**📦 Name:** `{name}`\n"
            #f"**🖼️ Image:** `{image}`\n"
            #f"**📅 Created:** `{created.strftime('%Y-%m-%d %H:%M:%S %Z')}`\n"
            f"**🕒 Uptime:** `{uptime}`"
            "\n`----------------------------------`\n"
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
        except Exception as e:
            return "N/A"

    @commands.command(aliases=["start"])
    async def docker_start(self, ctx):
        """Starts a stopped Docker container interactively."""
        await self.manage_container(ctx, action="start")

    @commands.command(aliases=["stop"])
    async def docker_stop(self, ctx):
        """Stops a running Docker container interactively."""
        await self.manage_container(ctx, action="stop")

    @commands.command(aliases=["restart"])
    async def docker_restart(self, ctx):
        """Restarts a Docker container interactively."""
        await self.manage_container(ctx, action="restart")

    @commands.command(aliases=["rm", "remove"])
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

        # Handle options exceeding 25 limit
        option_chunks = [options[i : i + 25] for i in range(0, len(options), 25)]

        for chunk_index, option_chunk in enumerate(option_chunks):
            embed = discord.Embed(
                title=f"Select a container to {action.capitalize()}",
                description=f"Page {chunk_index + 1} of {len(option_chunks)}",
                color=discord.Color.blue(),
            )
            view = discord.ui.View()
            select = discord.ui.Select(
                placeholder=f"Select a container to {action.capitalize()}",
                options=option_chunk,
                min_values=1,
                max_values=1,
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
                selected_name = select.values[0]
                container = self.client.containers.get(selected_name)
                try:
                    if action == "start":
                        container.start()
                        await ctx.send(
                            f"▶️ Container `{container.name}` has been started.",
                            delete_after=5,
                        )
                    elif action == "stop":
                        container.stop()
                        await ctx.send(
                            f"⏹️ Container `{container.name}` has been stopped.",
                            delete_after=5,
                        )
                    elif action == "restart":
                        container.restart()
                        await ctx.send(
                            f"🔄 Container `{container.name}` has been restarted.",
                            delete_after=5,
                        )
                    elif action == "remove":
                        container.remove(force=True)
                        await ctx.send(
                            f"🗑️ Container `{container.name}` has been removed.",
                            delete_after=5,
                        )
                except Exception as e:
                    await ctx.send(f"⚠️ An error occurred: {e}", delete_after=5)
                await message.delete()

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


async def setup(bot):
    await bot.add_cog(Container(bot))
