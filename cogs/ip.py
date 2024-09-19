import discord
from discord.ext import commands
import requests
import os
import asyncio


class Ip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_public_ip(self):
        """Fetches the current public IP."""
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            response.raise_for_status()  # Will raise an exception if the status code is not 200
            return response.json().get("ip")
        except requests.exceptions.Timeout:
            return "Error: Timeout when trying to fetch the public IP."
        except requests.exceptions.RequestException as e:
            return f"Error fetching public IP: {e}"

    @commands.command(aliases=["ip"])
    async def get_ip(self, ctx):
        """returns public IP"""
        public_ip = self.get_public_ip()

        content = f"**Public IP:**\n**`{public_ip}`**"

        # Send the message (not ephemeral)
        bot_message = await ctx.send(content)

        # Wait for 30 seconds
        await asyncio.sleep(30)

        # Delete the user's command and the bot's response
        try:
            await ctx.message.delete()
            await bot_message.delete()
        except discord.errors.NotFound:
            # Message might have been deleted already, ignore this error
            pass


async def setup(bot) -> None:
    await bot.add_cog(Ip(bot))
