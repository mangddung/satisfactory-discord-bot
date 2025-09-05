import discord
from datetime import timedelta
import asyncio
import ipaddress
from .satisfactory_api import *
from .embed import *
from db import *

class InitialSettingModal(discord.ui.Modal, title="Satisfactory Server — Initial Setup"):
    channel_name_input = discord.ui.TextInput(label="Channel name", placeholder="satisfactory-server", required=True, default="satisfactory-server")
    server_ip_input = discord.ui.TextInput(label="Server address (IPv4)", placeholder="192.168.0.1", required=True)
    server_port_input = discord.ui.TextInput(label="Server port (default: 7777)", placeholder="7777", default="7777")
    server_password_input = discord.ui.TextInput(label="Admin password", placeholder="Enter the admin password", required=True)
    client_password_input = discord.ui.TextInput(label="Client password (optional)", placeholder="Leave blank if not set", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        
        channel_name = self.channel_name_input.value.strip()
        server_ip = self.server_ip_input.value.strip()
        server_port = self.server_port_input.value.strip()
        server_password = self.server_password_input.value.strip()
        client_password = self.client_password_input.value.strip()

        guild = interaction.guild

        # check existing channel name
        search_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if search_channel:
            await interaction.response.send_message(f'Channel **{channel_name}** already exists.', ephemeral=True)
            return
        
        bot_member = guild.me
        bot_ow = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True,
            attach_files=True,
            manage_messages=True,
            manage_channels=True,
        )
            
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # @everyone cannot view
            bot_member: bot_ow, 
        }
        
        server_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        if not server_channel:
            await interaction.response.send_message(f'Failed to create channel **{channel_name}**.', ephemeral=True)
            await server_channel.delete()
            return

        # check valid ip addr
        try:
            ipaddress.IPv4Address(server_ip)
        except ipaddress.AddressValueError:
            await interaction.response.send_message(f'**{server_ip}** is not a valid IPv4 address.', ephemeral=True)
            await server_channel.delete()
            return

        # check valid port num
        try:
            server_port_num = int(server_port)
        except:
            await interaction.response.send_message(f'**{server_port}** is not a valid number (port).', ephemeral=True)
            await server_channel.delete()
            return

        if server_port_num < 1024 or server_port_num > 65535:
            await interaction.response.send_message(f'**{server_port_num}** is an invalid port. Please enter a value between 1024 and 65535.', ephemeral=True)
            await server_channel.delete()
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True, thinking=True)

        # check server password
        base_url = f"https://{server_ip}:{server_port}/api/v1"
        try:
            token = await asyncio.to_thread(gen_token, base_url, server_password, 5, "Administrator")
            data  = await asyncio.to_thread(get_server_status, base_url, token, 5)
        except ServerAPIError as ex:
            msg = str(ex).lower()
            if "timeout" in msg or "connection_error" in msg:
                await interaction.followup.send("❌ Unable to connect to the server. It might be offline or unreachable.", ephemeral=True)
                await server_channel.delete()
                return
            await interaction.followup.send(f"Error: {ex}", ephemeral=True)
            await server_channel.delete()
            return

        if client_password:
            try:
                gen_token(base_url, client_password, privilege = "Client")
            except ServerAPIError as ex:
                await interaction.followup.send(f"Error: {ex}")
                await server_channel.delete()
                return
            except Exception as ex:
                await interaction.followup.send(f"Error: {ex}")
                await server_channel.delete()
                return

        session_name = data.get('activeSessionName', "Unknown")
        players = data.get('numConnectedPlayers', "?")
        max_players = data.get('playerLimit', "?")
        play_time_str = data.get('totalGameDuration', "0")
        status = data.get('isGameRunning', False)

        embed = build_server_embed(
            session_name=session_name,
            players=players,
            max_players=max_players,
            play_time_str=timedelta(seconds=int(play_time_str)),
            status=status,
            server_ip=server_ip,
            server_port=server_port,
            client_password=client_password
        )

        status_message = await server_channel.send(embed=embed)

        # Persist settings to the database
        try:
            db = get_session()
            new_server_setting = ServerSettings(
                owner_id = interaction.user.id,
                guild_id = interaction.guild.id,
                channel_id = server_channel.id,
                embed_id = status_message.id,
                server_ip = server_ip,
                server_port = server_port,
                api_token = token,
                client_password = client_password
            )
            db.add(new_server_setting)
            db.commit()

        except:
            db.rollback()
            await status_message.delete()
            await server_channel.delete()
            await interaction.followup.send("An error occurred while writing to the database.", ephemeral=True)
            return
        finally:
            db.close()
        
        await interaction.followup.send("✅ Server channel created and settings saved.", ephemeral=True)