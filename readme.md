🎉 Discord Bot (For Private Use Only) 🎉
🚀 Overview
Hey there!
This is my first take on a Discord bot, built with discord.py just for learning purposes.

Note: This bot is intended for personal use only. Feel free to explore and customize it for your own projects!

🌟 Features Include
🔄 Auto-Delete: Automatically delete messages after a specified duration to keep your channels clean.
📦 Container Management: Manage Docker containers directly from Discord commands.
🌐 Public IP Retrieval: Quickly fetch your server's public IP address with a simple command.
📌 Sticky Messages: Pin important messages in your channels with ease.
🛠️ Core Management: Dynamically load and manage bot extensions (cogs) for modular functionality.
❓ Help Command: Comprehensive help command to navigate and understand available features.
🛠️ Installation (Docker Compose Recommended)
📋 Prerequisites
Docker: Ensure Docker is installed on your system. Get Docker
Discord Account: A Discord account with a Bot Token and a server where you have permission to add bots.
🖥️ Setup with Docker
Volumes:
/Path/To/Your/config:/app/config: This is where the bot stores its configuration files. Replace /Path/To/Your/config with the absolute path to a directory on your host where the bot can persist data.

Optional Volume
/var/run/docker.sock:/var/run/docker.sock: This allows the bot to interact with Docker on the host system, necessary for Docker-related commands within the bot. This volume can be removed if not needed, as it only affects the Container cog, which you can leave unloaded if desired.

Run the Bot with Docker Compose:
Create a .env file in your project directory and add your Discord bot token as shown in the example files.

Create a compose.yml file in your project directory and add the following content:

yaml
Code kopieren
services:
  discord-bot:
    image: slxyyz/keroppi:latest
    container_name: Discord-Bot
    environment:
      DISCORD_TOKEN: ${DISCORD_TOKEN}
      COMMAND_PREFIX: ${COMMAND_PREFIX}
      TIMEZONE: ${TIMEZONE}
    volumes:
      - /Path/To/Your/config:/app/config
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
Then run the bot with:

bash
Code kopieren
docker compose up -d
Or, you can use this command directly:

arduino
Code kopieren
```bash
docker run -d --name Discord-Bot \
  -e DISCORD_TOKEN=your-bot-token \
  -e COMMAND_PREFIX=! \
  -e TIMEZONE=Europe/Berlin \
  -v /Path/To/Your/config:/app/config \
  -v /var/run/docker.sock:/var/run/docker.sock \
  slxyyz/keroppi:latest
```
Customizing Environment Variables
You can adjust the bot's behavior by setting these environment variables:

COMMAND_PREFIX: Set your desired command prefix. Default: !
TIMEZONE: Set your timezone for timestamped messages. Default: Europe/Berlin
Add these to your .env file or pass them as environment variables in your Docker setup.

📚 Usage
Once the bot is up and running, only the core and help cogs will be loaded. Use !help to view available commands and usage examples.

!help: Displays the help menu with all available commands and their descriptions.
🎨 Customization
Feel free to dive into the code and customize the bot to better fit your needs! Whether it's adding new features, tweaking existing ones, or just experimenting, I hope you have as much fun with it as I did creating it.

📬 Contact
If you have any questions or just want to say hi, feel free to reach out!

Thank you for checking out my Discord bot! Critique is always welcome (just keep in mind that this project is purely for practice and was never intended for general use). Happy Discording! 🎉
