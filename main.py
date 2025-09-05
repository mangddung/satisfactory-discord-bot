import discord
from discord.ext import commands
import os
from config import BOT_PREFIX, BOT_TOKEN, BOT_STATUS_MESSAGE
from db import *
from db.session import init_db

# Discord bot intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.guilds = True
intents.guild_messages = True
intents.members = True

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=BOT_PREFIX,
            intents=intents,
            help_command=None,
        )

    async def load_cogs(self) -> None:
        cmds_path = os.path.join(os.path.dirname(__file__), "cogs")
        for file in os.listdir(cmds_path):
            if not file.endswith(".py") or file == "__init__.py":
                continue
            ext = file[:-3]
            module = f"cogs.{ext}"
            try:
                await self.load_extension(module)
                print(f"✔ Loaded extension {module}")
            except Exception as e:
                print(f"✖ Failed to load {module}: {type(e).__name__}: {e}")

    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.tree.sync()

    async def on_ready(self) -> None:
        await self.change_presence(activity=discord.Game(name=BOT_STATUS_MESSAGE))

init_db()
bot = DiscordBot()
bot.run(BOT_TOKEN)