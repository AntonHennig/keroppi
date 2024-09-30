import discord
from discord.ext import commands
import docker
import io

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

    @commands.command(aliases=["log"])
    async def docker_log(self, ctx,container_name: str):
        """Fetch Docker logs and send them as a file."""
        try:
            client = docker.from_env()
            container = client.containers.get(container_name)
            logs = container.logs(timestamps=True, tail=100).decode('utf-8')
            
            with io.StringIO() as file:
                file.write(logs)
                file.seek(0)
                
                await ctx.send(file=discord.File(file, f"{container_name}_logs.txt"))
            
        except docker.errors.NotFound as e:
            await ctx.send(f"❌ {container_name} not found")
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Container(bot))
