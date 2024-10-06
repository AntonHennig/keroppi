Simple Discord bot for personal use, currently configured for some random stuff and Docker Container Management on a Unraid Server.

Feature List 
  - Container Management
  - Public IP retrieval
  - ...

Example compose and .env file avalaible

  Volume Explanation:

  `/Path/To/Your/config:/app/config:` This is where the bot stores its configuration files. Replace /Path/To/Your/config with the absolute path to a directory on your host where the bot can persist data.
  `/var/run/docker.sock:/var/run/docker.sock:` This allows the bot to interact with Docker on the host system (necessary for Docker-related commands within the bot).

Example run command

        docker run -d --name Discord-Bot \
        -e DISCORD_TOKEN=your-bot-token \
        -v /Path/To/Your/config:/app/config \
        -v /var/run/docker.sock:/var/run/docker.sock \
        slxyyz/keroppi:latest

Optional
  You can pass in your Timezone and desired Command_prefix
  by adding
        -e COMMAND_PREFIX=!         # defaults to !
        -e TIMEZONE=Europe/Berlin   # defaults to Europe/Berlin