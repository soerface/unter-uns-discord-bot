import logging
import os

import discord
import redis
import games
import settings

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO")))

logger = logging.getLogger(__name__)


class DiscordClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super(DiscordClient, self).__init__(*args, **kwargs)
        self.db = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.games = {
            "insider": games.Insider
        }

    async def on_ready(self):
        P = discord.Permissions
        permissions_to_ask_for = P(P.text().value | P.voice().value)
        oauth_url = discord.utils.oauth_url(self.user.id, permissions_to_ask_for)
        logger.info(f"Ready. Add me to your server with this link: {oauth_url}")

    async def on_message(self, message: discord.Message):
        logger.info(f"Received message: {message}")
        if message.channel.type.name == "private":
            # TODO: determine to which gameclass to send it to
            await games.Insider(self, self.db).on_private_message(message)
            return
        GameClass = self.games.get(message.channel.name)
        if not GameClass:
            return
        if not message.clean_content.startswith(settings.CMD_PREFIX):
            return
        cmd = message.clean_content.replace(settings.CMD_PREFIX, "", 1).lower()
        game = GameClass(self, self.db)
        method = getattr(game, f"on_{cmd}_command", None)
        if not method:
            await message.channel.send("Unbekannter Befehl.")
            method = game.on_help_command
        await method(message)


client = DiscordClient()
client.run(os.environ.get("TOKEN", ""))
