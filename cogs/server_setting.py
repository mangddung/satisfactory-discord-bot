import discord
from discord import app_commands
from discord.ext import commands
from db import *
from utils import *

class ServerSettingCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._server_task = None

    @app_commands.command(
        name="initial-setup", 
        description="Configure the Satisfactory server (IP address, password, privilege)."
    )
    @app_commands.default_permissions(administrator=True)
    async def server_setting(self, interaction: discord.Interaction):
        await interaction.response.send_modal(InitialSettingModal())
        pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = get_session()
        try:
            deleted = (
                db.query(ServerSettings)
                .filter(
                    ServerSettings.guild_id == channel.guild.id,
                    ServerSettings.channel_id == channel.id
                )
                .delete(synchronize_session=False)
            )
            db.commit()
            # bot_event_logger.info("ServerSettings rows deleted", extra={"extra_fields": {"deleted": deleted, "guild_id": channel.guild.id, "channel_id": channel.id}})
        except Exception:
            db.rollback()
            # bot_event_logger.error("Failed to delete ServerSettings", exc_info=True)
        finally:
            db.close()

    @commands.Cog.listener()
    async def on_ready(self):
        if self._server_task is None or self._server_task.done():
            self._server_task = asyncio.create_task(
                periodic_server_check(self.bot)
            )
            print('task_start')

    def cog_unload(self):
        if self._server_task and not self._server_task.done():
            self._server_task.cancel()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerSettingCommands(bot))