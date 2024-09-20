import discord
from discord.ext import commands
import subprocess


class Docker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  # Restrict to bot owner for security
    async def restart_container(self, ctx, container_name: str):
        """Restarts the specified Docker container."""
        try:
            # Run the 'docker restart' command
            result = subprocess.run(
                ["docker", "restart", container_name],
                capture_output=True,
                text=True,
                check=True,
            )

            # Success message
            await ctx.send(f"Successfully restarted container: `{container_name}`")

        except subprocess.CalledProcessError as e:
            # Error message if restarting failed
            await ctx.send(
                f"Error restarting container: `{container_name}`\nError: {e.stderr}"
            )
            print(f"Error: {e.stderr}")

    @commands.command(aliases=["dockerps"])
    @commands.is_owner()  # Restrict to bot owner for security
    async def list_containers(self, ctx):
        """Lists all running Docker containers."""
        try:
            # Run the 'docker ps' command to list running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}} - {{.Status}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse and send the list of containers
            running_containers = result.stdout.strip()
            if running_containers:
                await ctx.send(f"**Running containers:**\n```{running_containers}```")
            else:
                await ctx.send("No running containers found.")

        except subprocess.CalledProcessError as e:
            # Error message if there's an issue fetching the containers
            await ctx.send(f"Error fetching running containers.\nError: {e.stderr}")
            print(f"Error: {e.stderr}")


async def setup(bot):
    await bot.add_cog(Docker(bot))
