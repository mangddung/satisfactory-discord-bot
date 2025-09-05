import discord
from discord.ext import commands
from discord.errors import NotFound, Forbidden, HTTPException
from datetime import datetime, timezone, timedelta
from utils import *

STATUS_STYLE = {
    True:     {"dot": "🟢", "name": "OPEN",     "color": 0x2ECC71},
    # "starting": {"dot": "🟡", "name": "STARTING", "color": 0xF1C40F},
    False:    {"dot": "🔴", "name": "CLOSE",    "color": 0xE74C3C},
}

def build_server_embed(
    session_name: str,
    players,
    max_players,
    play_time_str: str,
    status: bool,
    server_ip: str | None = None,
    server_port: str | None = None,
    client_password: str | None = None,
) -> discord.Embed:
    style = STATUS_STYLE.get(status, STATUS_STYLE[False])
    title = f"{style['dot']}  Satisfactory Server • {style['name']}"

    embed = discord.Embed(
        title=title,
        color=style["color"],
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(name="IP", value=f"```{server_ip}```", inline=False)
    embed.add_field(name="Port", value=f"`{server_port}`", inline=False)
    embed.add_field(name="Session Name", value=f"`{session_name}`", inline=False)
    embed.add_field(name="Player", value=f"`{players}/{max_players}`", inline=True)
    embed.add_field(name="Playtime", value=f"`{play_time_str}`", inline=True)
    embed.add_field(name="Status", value=f"{style['dot']} `{style['name']}`", inline=True)

    if client_password:
        embed.add_field(name="Client password", value=f"|| ```{client_password}``` ||", inline=False)

    embed.set_footer(text="Satisfactory Server")
    return embed

async def update_server_embed(
    db,
    bot: commands.Bot,
    data: dict,
    server_setting: "ServerSettings",
) -> None:
    """
    Update (or recreate) the status embed message for a configured server/channel.
    - If the channel is missing or inaccessible, remove the stale DB row and exit.
    - If the original message is missing, send a new one and update embed_id.
    """

    # Retrieve the channel (cache first, then API). If inaccessible, clean up and exit.
    channel = bot.get_channel(server_setting.channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(server_setting.channel_id)
        except (NotFound, Forbidden, HTTPException):
            # Channel no longer exists or the bot lacks permissions → remove stale DB entry
            try:
                db.delete(server_setting)
                db.commit()
            except Exception:
                db.rollback()
            return

    # Extract fields from the server state payload
    session_name = data.get('activeSessionName', "Unknown")
    players = data.get('numConnectedPlayers', "?")
    max_players = data.get('playerLimit', "?")
    play_time_str = data.get('totalGameDuration', "0")
    status = data.get('isGameRunning', False)

    # Build the embed to display
    embed = build_server_embed(
        session_name = session_name,
        players = players,
        max_players = max_players,
        play_time_str = timedelta(seconds=int(play_time_str)),
        status = status,
        server_ip = server_setting.server_ip,
        server_port = server_setting.server_port,
        client_password = server_setting.client_password
    )
    try:
        # Edit the existing embed message
        msg = await channel.fetch_message(server_setting.embed_id)
        await msg.edit(embed = embed)
    except NotFound:
        # The original message was removed — create a new one and update embed_id
        new_embed = await channel.send(embed = embed)
        server_setting.embed_id = new_embed.id
        try:
            db.commit()
        except Exception:
            db.rollback()
            return
        return
    except Forbidden:
        # The bot lacks permission to edit/send messages in this channel
        return
    


    