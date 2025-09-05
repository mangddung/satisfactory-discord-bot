import discord
from discord import app_commands
from discord.ext import commands

class ServerControl(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="s-server-on", 
        description="starting satisfactory server"
    )
    async def server_start(self, interaction: discord.Interaction, channel_name: str = "Satisfactory-Server"):
        '''
        명령어 입력된 서버 전용 채널 확인
        DB 또는 역할에서 해당 서버 컨트롤 권한 확인
        DB에서 채널id와 서버 컨테이너 id 매핑
        서버 상태 불러오기
        off 상태이면 서버 시작 명령 전송
        '''
        pass