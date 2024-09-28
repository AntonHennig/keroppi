import discord
from discord.ext import commands
import docker

# connect to docker socket
client = docker.from_env()

class Container(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["ps"])
    async def docker_ps(self, ctx):
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
