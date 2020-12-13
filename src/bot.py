import logging
import os

import discord
import redis
import games

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")))

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):
    CMD_PREFIX = "!"

    def __init__(self, *args, **kwargs):
        super(DiscordClient, self).__init__(*args, **kwargs)
        self.db = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.games = {
            "insider": games.Insider
        }

    async def on_ready(self):
        logger.info("Ready")

    async def on_message(self, message: discord.Message):
        logger.info(f"Received message: {message}")
        if message.channel.type.name == "private":
            await games.Insider(self, self.db).on_player_message(message)
            return
        game_class = self.games.get(message.channel.name)
        if not game_class:
            return
        if not message.clean_content.startswith(DiscordClient.CMD_PREFIX):
            return
        cmd = message.clean_content.replace(DiscordClient.CMD_PREFIX, "", 1).lower()
        game = game_class(self, self.db)
        method = getattr(game, f"on_{cmd}_command", None)
        if not method:
            await message.channel.send("Den Befehl kenne ich leider nicht :(")
            return
        await method(message)

    async def handle_start_command(self, message: discord.Message):
        # self.db.put(f"game:{message}")
        await message.channel.send("Let's start")


client = DiscordClient()
client.run(os.environ.get("TOKEN", ""))
