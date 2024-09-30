Simple Discord bot for personal use, currently configured for some random stuff and Docker Container Management on a Unraid Server.

Feature List 
  - Container Management
  - Public IP retrieval
  - ...

Example compose file avalaible
Just create a .env in the bot folder and run it with
  - ```docker compose up -d```

Example run command

        docker run -d --name discord_bot \
        -e DISCORD_TOKEN=your-bot-token \
        -v /mnt/user/appdata/keroppi/config:/app/config \
        -v /var/run/docker.sock:/var/run/docker.sock \
        slxyyz/keroppi:latest
