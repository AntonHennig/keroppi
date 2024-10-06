import discord
from discord.ext import commands
from discord import ui
import asyncio
import aiohttp
import platform
from decorators import delete_command_message, delete_bot_response


class Ip(
    commands.Cog,
    description="Commands to fetch and display the server's public IP address.",
):
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

    @commands.command(name="get_ip", aliases=["ip"])
    @commands.is_owner()
    @delete_command_message(delay=0)
    @delete_bot_response(delay=60)
    async def get_ip(self, ctx):
        """Returns the server's public IP address.

        **Usage:**
        `!get_ip`

        **Example:**
        `!get_ip`

        This command fetches and displays the public IP address of the server the bot is running on.
        """
        public_ip = await self.get_public_ip()

        if public_ip.startswith("Error"):
            # Send an error message
            await ctx.send(f"❌ {public_ip}", delete_after=10)
        else:
            # Send the public IP address
            embed = discord.Embed(
                title="🌐 Server Public IP Address",
                description=f"`{public_ip}`",
                color=discord.Color.blue(),
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )
            await ctx.send(embed=embed)

    @commands.command(name="ip_info", aliases=["ipinfo"])
    @commands.is_owner()
    @delete_command_message(delay=0)
    @delete_bot_response(delay=60)
    async def ip_info(self, ctx):
        """Displays detailed information about the server's public IP.

        **Usage:**
        `!ip_info`

        **Example:**
        `!ip_info`

        This command fetches and displays detailed geolocation and network information about the server's public IP address.
        """
        public_ip = await self.get_public_ip()

        if public_ip.startswith("Error"):
            await ctx.send(f"❌ {public_ip}", delete_after=10)
            return

        # Fetch detailed IP information
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"http://ip-api.com/json/{public_ip}?fields=status,message,country,regionName,city,isp,org,as,query",
                    timeout=5,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "success":
                            embed = discord.Embed(
                                title="🌐 Server Public IP Information",
                                color=discord.Color.blue(),
                            )
                            embed.add_field(
                                name="IP Address",
                                value=f"`{data.get('query')}`",
                                inline=False,
                            )
                            embed.add_field(
                                name="Country",
                                value=data.get("country", "N/A"),
                                inline=True,
                            )
                            embed.add_field(
                                name="Region",
                                value=data.get("regionName", "N/A"),
                                inline=True,
                            )
                            embed.add_field(
                                name="City", value=data.get("city", "N/A"), inline=True
                            )
                            embed.add_field(
                                name="ISP", value=data.get("isp", "N/A"), inline=False
                            )
                            embed.add_field(
                                name="Organization",
                                value=data.get("org", "N/A"),
                                inline=False,
                            )
                            embed.add_field(
                                name="ASN", value=data.get("as", "N/A"), inline=False
                            )
                            embed.set_footer(
                                text=f"Requested by {ctx.author.display_name}",
                                icon_url=ctx.author.display_avatar.url,
                            )
                            await ctx.send(embed=embed)
                        else:
                            error_message = data.get(
                                "message", "Unknown error occurred."
                            )
                            await ctx.send(
                                f"❌ Error fetching IP information: {error_message}",
                                delete_after=10,
                            )
                    else:
                        await ctx.send(
                            f"❌ Error: Received unexpected status code {response.status} when fetching IP information.",
                            delete_after=10,
                        )
            except asyncio.TimeoutError:
                await ctx.send(
                    "❌ Error: Timeout when trying to fetch IP information.",
                    delete_after=10,
                )
            except aiohttp.ClientError as e:
                await ctx.send(
                    f"❌ Error fetching IP information: {e}", delete_after=10
                )

    @commands.command(name="ping")
    @commands.has_permissions(send_messages=True)
    @delete_command_message(delay=0)
    async def ping(self, ctx):
        """Displays the bot's latency and provides additional ping options.

        **Usage:**
        `!ping`

        After invoking the command, you'll be presented with options to view bot latency, ping a website, or view system information.
        """

        class PingOptionsView(ui.View):
            def __init__(self, bot, ctx, timeout=60):
                super().__init__(timeout=timeout)
                self.bot = bot
                self.ctx = ctx
                self.response = None

            @ui.button(label="Bot Latency", style=discord.ButtonStyle.primary)
            async def bot_latency(
                self, interaction: discord.Interaction, button: ui.Button
            ):
                latency = round(self.bot.latency * 1000)  # Convert to milliseconds
                embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
                embed.add_field(name="Bot Latency", value=f"{latency} ms")
                embed.set_footer(
                    text=f"Requested by {self.ctx.author}",
                    icon_url=self.ctx.author.avatar.url,
                )
                await interaction.response.edit_message(embed=embed, view=self)
                self.response = True

            # @ui.button(label="Ping a Website", style=discord.ButtonStyle.secondary)
            # async def ping_website(
            #     self, interaction: discord.Interaction, button: ui.Button
            # ):
            #     await interaction.response.send_message(
            #         "🌐 Please enter the website URL (e.g., `https://www.google.com`):",
            #         ephemeral=True,
            #     )

            #     def check(m):
            #         return m.author == self.ctx.author and m.channel == self.ctx.channel

            #     try:
            #         msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            #         url = msg.content.strip()
            #         await msg.delete()

            #         # Start pinging the website
            #         await interaction.followup.send(
            #             f"🔎 Pinging `{url}`...", ephemeral=True
            #         )

            #         # Use aiohttp to send a HEAD request
            #         import aiohttp

            #         start_time = time.perf_counter()
            #         async with aiohttp.ClientSession() as session:
            #             async with session.head(url) as response:
            #                 end_time = time.perf_counter()
            #                 duration = (
            #                     end_time - start_time
            #                 ) * 1000  # Convert to milliseconds

            #                 embed = discord.Embed(
            #                     title="🌐 Website Ping Result",
            #                     color=discord.Color.blue(),
            #                 )
            #                 embed.add_field(name="URL", value=url)
            #                 embed.add_field(name="Status", value=response.status)
            #                 embed.add_field(
            #                     name="Response Time", value=f"{round(duration)} ms"
            #                 )
            #                 embed.set_footer(
            #                     text=f"Requested by {self.ctx.author}",
            #                     icon_url=self.ctx.author.avatar.url,
            #                 )
            #                 await interaction.followup.send(embed=embed, ephemeral=True)
            #     except asyncio.TimeoutError:
            #         await interaction.followup.send(
            #             "❌ Timed out waiting for your response.", ephemeral=True
            #         )
            #     except Exception as e:
            #         await interaction.followup.send(
            #             f"❌ An error occurred: {e}", ephemeral=True
            #         )

            @ui.button(label="System Information", style=discord.ButtonStyle.secondary)
            async def system_info(
                self, interaction: discord.Interaction, button: ui.Button
            ):
                uname = platform.uname()
                embed = discord.Embed(
                    title="💻 System Information", color=discord.Color.purple()
                )
                embed.add_field(name="System", value=uname.system)
                embed.add_field(name="Node Name", value=uname.node)
                embed.add_field(name="Release", value=uname.release)
                embed.add_field(name="Version", value=uname.version)
                embed.add_field(name="Machine", value=uname.machine)
                embed.add_field(name="Processor", value=uname.processor)
                embed.set_footer(
                    text=f"Requested by {self.ctx.author}",
                    icon_url=self.ctx.author.avatar.url,
                )
                await interaction.response.edit_message(embed=embed, view=self)
                self.response = True

            @ui.button(label="Cancel", style=discord.ButtonStyle.danger)
            async def cancel(self, interaction: discord.Interaction, button: ui.Button):
                await interaction.response.edit_message(
                    content="❌ Ping operation cancelled.", embed=None, view=None
                )
                self.stop()

        embed = discord.Embed(
            title="Ping Options",
            description="Please choose an option below:",
            color=discord.Color.gold(),
        )
        view = PingOptionsView(self.bot, ctx)
        message = await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.response is None:
            await message.edit(content="⏳ Operation timed out.", embed=None, view=None)


async def setup(bot):
    await bot.add_cog(Ip(bot))
