import discord
from discord.ext import commands
import aiohttp
import asyncio


class Ip(commands.Cog):
    """Cog to fetch and display the server's public IP address."""

    def __init__(self, bot):
        self.bot = bot

    async def get_public_ip(self):
        """Asynchronously fetches the current public IP."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://api.ipify.org?format=json", timeout=5
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("ip")
                    else:
                        return (
                            f"Error: Received unexpected status code {response.status}"
                        )
            except asyncio.TimeoutError:
                return "Error: Timeout when trying to fetch the public IP."
            except aiohttp.ClientError as e:
                return f"Error fetching public IP: {e}"

    @commands.command(aliases=["ip"])
    async def get_ip(self, ctx):
        """Returns the server's public IP."""
        public_ip = await self.get_public_ip()

        content = f"**Public IP:**\n`{public_ip}`"

        # Send the message
        await ctx.send(content)


async def setup(bot):
    await bot.add_cog(Ip(bot))
