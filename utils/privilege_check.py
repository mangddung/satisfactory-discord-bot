import discord
from db import *

def check_privilege(
    db,
    container_id: str,
    interaction: discord.Interaction,
    control: str  # 'start' or 'stop'
) -> bool:
    server = db.query(ServerSettings).filter(
        ServerSettings.container_id == container_id
    ).first()
    if not server:
        return False

    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel_id)

    member_priv = db.query(ServerControlPrivilege).filter(
        ServerControlPrivilege.server_uuid == server.uuid,
        ServerControlPrivilege.privilege_type == 'member',
        ServerControlPrivilege.guild_id == guild_id,
        ServerControlPrivilege.channel_id == channel_id,
        ServerControlPrivilege.principal_id == user_id,
    ).first()

    if member_priv:
        if control == 'start' and member_priv.control_start:
            return True
        if control == 'stop' and member_priv.control_stop:
            return True

    user_role_ids = [str(r.id) for r in interaction.user.roles]
    role_privs = db.query(ServerControlPrivilege).filter(
        ServerControlPrivilege.server_uuid == server.uuid,
        ServerControlPrivilege.privilege_type == 'role',
        ServerControlPrivilege.guild_id == guild_id,
        ServerControlPrivilege.channel_id == channel_id,
        ServerControlPrivilege.principal_id.in_(user_role_ids),
    ).all()

    for rp in role_privs:
        if control == 'start' and rp.control_start:
            return True
        if control == 'stop' and rp.control_stop:
            return True

    return False
