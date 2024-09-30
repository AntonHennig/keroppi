import discord
from discord.ext import commands
import docker

# Connect to the Docker client
try:
    client = docker.from_env()
except docker.errors.DockerException as e:
    client = None  # Handle the case where Docker client fails to initialize


class Container(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["ps"])
    async def docker_ps(self, ctx):
        """Lists running Docker containers."""
        if client is None:
            await ctx.send("Error: Docker client is not available.")
            return

        try:
            containers = client.containers.list()
            if not containers:
                await ctx.send("No containers are running.")
            else:
                container_list = "\n".join([f"- {c.name}" for c in containers])
                await ctx.send(f"Running containers:\n{container_list}")
        except docker.errors.DockerException as e:
            await ctx.send(f"Docker error: {e}")


async def setup(bot):
    await bot.add_cog(Container(bot))
