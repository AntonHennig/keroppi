# 🎉 Personal Discord Bot 🎉

## 🚀 Overview

Hey there! 
  This is a first take on a discord bot written with discord.py, just for learning purposes.
> **Note:** This bot is intended for **personal use only**. Feel free to explore and customize it for your own projects!

---

## 🌟 Features

- **🔄 Auto-delete:** Automatically delete messages after a specified duration to keep your channels clean.
- **📦 Container Management:** Easily manage Docker containers directly from Discord commands.
- **🌐 Public IP Retrieval:** Quickly fetch your server's public IP address with a simple command.
- **📌 Sticky Messages:** Keep important messages pinned in your channels with ease.
- **🛠️ Core Management:** Dynamically load and manage bot extensions (cogs) for modular functionality.
- **❓ Help Command:** Comprehensive help command to navigate and understand available features.

---

## 🛠️ Installation (I recommend Docker Compose)

### 📋 Prerequisites

- **Docker:** Ensure you have Docker installed on your system. [Get Docker](https://docs.docker.com/get-docker/)
- **Discord Account:** A Discord account and a server where you have permissions to add bots.

### 🖥️ Setup with Docker

  /Path/To/Your/config:/app/config:
  This is where the bot stores its configuration files. Replace /Path/To/Your/config with the absolute path to a directory on your host where the bot can persist data.

  /var/run/docker.sock:/var/run/docker.sock:
  This allows the bot to interact with Docker on the host system, which is necessary for Docker-related commands within the bot.

  Run the Bot  with Docker Compose:

  **create `.env` file** in the root of your project directory and add your Discord bot token as in the provided example files. 

  Create a compose.yml in your project directory and add the following content


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

  Then run with docker compose up -d

  Or use this run command:

    docker run -d --name Discord-Bot \
      -e DISCORD_TOKEN=your-bot-token \
      -e COMMAND_PREFIX=! \
      -e TIMEZONE=Europe/Berlin \
      -v /Path/To/Your/config:/app/config \
      -v /var/run/docker.sock:/var/run/docker.sock \
      slxyyz/keroppi:latest


  You can customize the bot's behavior by setting the following environment variables:

  COMMAND_PREFIX
  Set your desired command prefix.
  Defaults to: !

  TIMEZONE
  Set your timezone for timestamped messages.
  Defaults to: Europe/Berlin

  Add these to your .env file or pass them as environment variables in your Docker setup.

📚 Usage
Once the bot is up and running, only the core and help cog will be loaded. Feel free to use !help to see available commands and usage exmaples.

!help
Displays the help menu with all available commands and their descriptions.

🎨 Customization
Feel free to dive into the code and customize the bot to better fit your needs! Whether it's adding new features, tweaking existing ones, or just playing around, I hope you have as much fun with it as I did creating it.

🤝 Contributing
This project is for personal use, but if you have suggestions or improvements, feel free to open an issue or submit a pull request!

📬 Contact
If you have any questions or just want to say hi, feel free to reach out!

Thank you for checking out my Discord bot! Critique is always welcome (but do keep in mind that this project is just for practicing and was never intended to be used other than by myself). Happy Discording! 🎉