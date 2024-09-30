import discord
from discord.ext import commands
import docker

# Attempt to connect to Docker socket
try:
    client = docker.from_env()
except docker.errors.DockerException as e:
    client = None  # Handlign docker socket connection error
    print(f"Error connecting to Docker: {e}")

class Container(commands.Cog):
    """A cog for interacting with Docker containers."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ps"])
    async def docker_ps(self, ctx):
        """Lists all running Docker containers."""
        if client is None:
            await ctx.send("❌ Error: Docker client is not available. Please check Docker connection.")
            return

        try:
            # List running containers
            containers = client.containers.list()
            if not containers:
                await ctx.send("🛑 No containers are currently running.")
            else:
                # Format container names for display
                container_list = "\n".join([f"- {c.name} ({c.status})" for c in containers])
                await ctx.send(f"🟢 **Running containers:**\n{container_list}")
        except docker.errors.APIError as e:
            await ctx.send(f"❌ Docker API error: {e}")
        except docker.errors.DockerException as e:
            await ctx.send(f"❌ Docker error: {e}")
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

    # (You can add more Docker-related commands here, e.g., starting/stopping containers)

async def setup(bot):
    await bot.add_cog(Container(bot))
