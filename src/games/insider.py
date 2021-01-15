import random

import discord
from .base import BaseGame


class Insider(BaseGame):
    """Der Spielleiter überlegt sich ein Wort, das Team stellt Ja-Nein Fragen um das Wort in 5 Minuten zu erraten.
Findet danach den Insider - er wusste von Anfang an Bescheid! 😱
    """

    async def on_private_message(self, message: discord.Message):
        player_name, player_id = message.author.display_name, message.author.id
        master = self.db.get("insider:master")
        insider = self.db.get("insider:insider")
        if not master or not insider:
            return
        master_name, master_id = master.split(":")
        master_id = int(master_id)
        if player_id == master_id:
            insider_user = await self.client.fetch_user(insider.split(":")[1])
            await insider_user.send(f"Das Wort ist: {message.content}")
            await message.author.send("Danke für dein Wort, ich hab es dem Insider geschickt!")

    async def on_start_command(self, message: discord.Message):
        current_state = self.db.get("insider:game_state")
        # if current_state == "started":
            # await message.channel.send("Aber es läuft doch schon ein Spiel. Abbrechen mit !cancel")
            # return
        players_raw = self.db.get("insider:players")
        players = players_raw.split(",") if players_raw else []
        if len(players) < 4:
            await message.channel.send(f"Es fehlen noch {4 - len(players)} Spieler. Beitreten mit !join")
            return
        self.db.set("insider:game_state", "started")
        master, insider = random.sample(players, k=2)
        self.db.set("insider:master", master)
        self.db.set("insider:insider", insider)
        master_user = await self.client.fetch_user(master.split(":")[1])
        insider_user = await self.client.fetch_user(insider.split(":")[1])
        await master_user.send("Du bist der Spielleiter! Sende mir ein Wort")
        await insider_user.send("Du bist der Insider! Ich verrate dir gleich das Wort")
        await message.channel.send(f"Los geht's! Euer Spielleiter ist heute {master}")
        await message.channel.send(f"Es spielen mit: {', '.join(players)}")

    async def on_cancel_command(self, message: discord.Message):
        self.db.set("insider:game_state", "")
        self.db.set("insider:players", "")
        self.db.set("insider:master", "")
        self.db.set("insider:insider", "")
        await message.channel.send("Spiel abgebrochen")

    async def on_join_command(self, message: discord.Message):
        players_raw = (self.db.get("insider:players") or "")
        players = players_raw.split(",") if players_raw else []
        new_player = ":".join([message.author.display_name, str(message.author.id)])
        if new_player not in players:
            players.append(new_player)
        self.db.set("insider:players", ",".join(players))
        await message.channel.send(f"Es spielen mit: {', '.join(players)}")
