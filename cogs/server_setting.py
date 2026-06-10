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

    @app_commands.command(
        name="add-member",
        description="특정 멤버에게 서버 시작/정지 권한을 부여합니다."
    )
    @app_commands.default_permissions(administrator=True)
    async def add_member(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        member: discord.Member,
        can_start: bool,
        can_stop: bool,
    ):
        db = get_session()
        setting = db.query(ServerSettings).filter(
            ServerSettings.guild_id == str(interaction.guild.id),
            ServerSettings.channel_id == str(channel.id),
        ).first()

        if not setting:
            await interaction.response.send_message("해당 채널에 등록된 서버가 없습니다.", ephemeral=True)
            db.close()
            return

        if str(interaction.user.id) != str(setting.owner_id):
            await interaction.response.send_message("채널 소유자만 권한을 설정할 수 있습니다.", ephemeral=True)
            db.close()
            return

        privilege = db.query(ServerControlPrivilege).filter(
            ServerControlPrivilege.server_uuid == setting.uuid,
            ServerControlPrivilege.privilege_type == 'member',
            ServerControlPrivilege.principal_id == str(member.id),
        ).first()

        if privilege:
            privilege.control_start = can_start
            privilege.control_stop = can_stop
        else:
            privilege = ServerControlPrivilege(
                server_uuid=setting.uuid,
                guild_id=str(interaction.guild.id),
                channel_id=str(channel.id),
                privilege_type='member',
                principal_id=str(member.id),
                principal_name=member.display_name,
                control_start=can_start,
                control_stop=can_stop,
            )
            db.add(privilege)

        try:
            db.commit()
            await interaction.response.send_message(
                f"**{member.display_name}** 권한 설정 완료\n시작: `{can_start}` / 정지: `{can_stop}`",
                ephemeral=True
            )
        except Exception as ex:
            db.rollback()
            await interaction.response.send_message(f"저장 실패: {ex}", ephemeral=True)
        finally:
            db.close()

    @app_commands.command(
        name="add-role",
        description="특정 역할에게 서버 시작/정지 권한을 부여합니다."
    )
    @app_commands.default_permissions(administrator=True)
    async def add_role(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        can_start: bool,
        can_stop: bool,
    ):
        db = get_session()
        setting = db.query(ServerSettings).filter(
            ServerSettings.guild_id == str(interaction.guild.id),
            ServerSettings.channel_id == str(channel.id),
        ).first()

        if not setting:
            await interaction.response.send_message("해당 채널에 등록된 서버가 없습니다.", ephemeral=True)
            db.close()
            return

        if str(interaction.user.id) != str(setting.owner_id):
            await interaction.response.send_message("채널 소유자만 권한을 설정할 수 있습니다.", ephemeral=True)
            db.close()
            return

        privilege = db.query(ServerControlPrivilege).filter(
            ServerControlPrivilege.server_uuid == setting.uuid,
            ServerControlPrivilege.privilege_type == 'role',
            ServerControlPrivilege.principal_id == str(role.id),
        ).first()

        if privilege:
            privilege.control_start = can_start
            privilege.control_stop = can_stop
        else:
            privilege = ServerControlPrivilege(
                server_uuid=setting.uuid,
                guild_id=str(interaction.guild.id),
                channel_id=str(channel.id),
                privilege_type='role',
                principal_id=str(role.id),
                principal_name=role.name,
                control_start=can_start,
                control_stop=can_stop,
            )
            db.add(privilege)

        try:
            db.commit()
            await interaction.response.send_message(
                f"**{role.name}** 역할 권한 설정 완료\n시작: `{can_start}` / 정지: `{can_stop}`",
                ephemeral=True
            )
        except Exception as ex:
            db.rollback()
            await interaction.response.send_message(f"저장 실패: {ex}", ephemeral=True)
        finally:
            db.close()
    
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