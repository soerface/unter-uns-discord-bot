import discord
from redis import Redis
import re
from jinja2 import Template

import settings

HELP_TEMPLATE = """{{ game_description }}
Du kannst folgende Befehle in diesem Channel verwenden:
{% for command in commands -%}
- **{{ command_prefix }}{{ command.cmd }}**: {{ command.description }}
{% endfor %}
"""


class BaseGame:
    """Du kannst als Entwickler deine Klasse mit einem docstring versehen. Das sieht dann etwa so aus:
```python
from .base import BaseGame

class MyGame(BaseGame):
    ""\"Dieses Spiel ist sehr gut. Es tut gute Dinge.""\"
```
Dadurch tritt deine Spielbeschreibung an diese Stelle. Mit deinen `on_CMD_command` Methoden kannst du dasselbe tun.
Probier's doch mal aus, viel Spaß!"""

    def __init__(self, client: discord.Client, db: Redis):
        self.client = client
        self.db = db

    async def on_help_command(self, message: discord.Message):
        """Gibt diese Hilfeseite zurück"""

        commands = [
            {
                "cmd": (cmd := m.group(1)),
                "description": get_command_help(self, cmd),
            } for x in dir(self) if (m := re.match(r"^on_(\w+)_command$", x))
        ]
        template = Template(HELP_TEMPLATE)
        response = template.render(
            commands=commands,
            command_prefix=settings.CMD_PREFIX,
            game_description=self.__doc__ or BaseGame.__doc__,
        )
        await message.channel.send(response)


def get_command_help(obj, cmd):
    docstring = getattr(obj, f"on_{cmd}_command").__doc__
    return docstring or f"TODO: Füge einen Hilfetext als *docstring* in deiner `on_{cmd}_command` Methode ein"
