import discord
from discord import app_commands
from discord.ext import commands
import docker
from config import CONTAINER_ID
from db import *
from utils.privilege_check import *

class ServerControlCommands(commands.Cog):
    """
    Cog for binding a specific Docker container (Satisfactory server) to a Discord channel.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = docker.from_env()
        self.container_id = CONTAINER_ID
        self.container = None
        self.server_control = False

        def check_container(self):
            """
            Resolve and validate the target container from CONFIG.CONTAINER_ID.
            If found, set `self.container` and enable server control features.
            """
            if not self.client:
                print("Docker client is not available (Docker might not be running).")
                return False

            try:
                if self.container_id:
                    self.container = self.client.containers.get(self.container_id)
            except Exception as ex:
                print(f"Failed to get container '{self.container_id}': {ex}")
                self.container = None

            if not self.container:
                print("Container not found. If you intend to run without server control, you can ignore this.")
                self.server_control = False
                return False

            container_image = self.container.attrs.get("Config", {}).get("Image")
            if not container_image:
                print("Image attribute not found in container config.")
                return False

            print(f"Detected container image: {container_image}")
            self.server_control = True
            return True

        check_container(self)

    @app_commands.command(
        name="connect-docker",
        description="Connect the Satisfactory Docker container to this channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def connect_docker(self, interaction: discord.Interaction, channel_name: discord.TextChannel):
        """
        Bind the configured Docker container to the given Discord text channel.
        - Ensures the initial setup exists for this guild+channel.
        - Only the owner registered in the DB can run this command.
        - Persists the container_id to the DB mapping.
        """
        db = get_session()

        # Prevent duplicate binding of the same container to multiple channels
        duplicate_binding = db.query(ServerSettings).filter(
            ServerSettings.container_id == self.container_id
        ).first()
        if duplicate_binding:
            await interaction.response.send_message(
                "This Docker container is already connected to a channel.",
                ephemeral=True
            )
            db.close()
            return

        d_server_setting = db.query(ServerSettings).filter(
            ServerSettings.guild_id == interaction.guild.id,
            ServerSettings.channel_id == channel_name.id
        ).first()

        if not d_server_setting:
            await interaction.response.send_message(
                "Cannot find the server checker channel record. Please complete the initial setup first.",
                ephemeral=True
            )
            db.close()
            return

        # Match types carefully: if owner_id is stored as string, cast user id to str.
        if str(interaction.user.id) != str(d_server_setting.owner_id):
            await interaction.response.send_message(
                "Only the owner can use this command.",
                ephemeral=True
            )
            db.close()
            return

        try:
            d_server_setting.container_id = self.container_id
            db.commit()
        except Exception as ex:
            db.rollback()
            await interaction.response.send_message(
                f"Failed to save container info to the database: {ex}",
                ephemeral=True
            )
            return
        finally:
            db.close()

        # Refresh container state before reporting it
        try:
            self.container.reload()
        except Exception:
            pass

        container_status = getattr(self.container, "status", "unknown")
        container_name = getattr(self.container, "name", self.container_id)

        await interaction.response.send_message(
            f"**{container_name}** has been successfully connected to this channel.\n"
            f"Current status: `{container_status}`\n"
            f"Use `/disconnect-docker` to unlink it later."
        )

    @app_commands.command(
        name="disconnect-docker",
        description="Disconnect the bound Docker container from this channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def disconnect_docker(self, interaction: discord.Interaction):
        """
        Unbind the configured Docker container from whichever channel it is currently linked to.
        - Requires an existing mapping for this container_id.
        """
        db = get_session()

        db_setting = db.query(ServerSettings).filter(
            ServerSettings.container_id == self.container_id
        ).first()

        if not db_setting:
            await interaction.response.send_message(
                "No channel is currently linked to this Docker container.",
                ephemeral=True
            )
            db.close()
            return

        # Optional: only the owner can disconnect
        if str(interaction.user.id) != str(db_setting.owner_id):
            await interaction.response.send_message(
                "Only the owner can disconnect this container.",
                ephemeral=True
            )
            db.close()
            return

        try:
            db_setting.container_id = None
            db.commit()
        except Exception as ex:
            db.rollback()
            await interaction.response.send_message(
                f"Failed to remove the container mapping: {ex}",
                ephemeral=True
            )
            return
        finally:
            db.close()

        await interaction.response.send_message("Disconnected the Docker container successfully.")

    @app_commands.command(
        name="server-start",
        description="server start"
    )
    async def server_start(self, interaction: discord.Interaction):
        db = get_session()
        if not check_privilege(db, self.container_id, interaction, 'start'):
            db.close()
            await interaction.response.send_message("no privilege", ephemeral=True)
            return
        db.close()
        try:
            self.container.reload()
            if self.container.status == "running":
                await interaction.response.send_message("Server is already running.", ephemeral=True)
                return
            self.container.start()
            await interaction.response.send_message("Server started successfully.")
        except Exception as ex:
            await interaction.response.send_message(f"Failed to start container: {ex}", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    """
    Add this Cog only if the target container is detected and validated.
    """
    cog = ServerControlCommands(bot)
    if cog.server_control:
        await bot.add_cog(cog)
    else:
        print("Container not found. Server control commands were not loaded.")
