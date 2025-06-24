import discord
import gspread
import asyncio
from discord.ext import commands
import random 
import os 
from dotenv import load_dotenv

from gspread_manager import *
from discord_battle_system import *

load_dotenv()

moogle_token = os.getenv('moogle_token')
test_token = os.getenv('test_token')

# Bot initialization
intents = discord.Intents.all()
activity = discord.Activity(type=discord.ActivityType.watching, name="!start")
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity)


@bot.event
async def on_ready():
    await bot.add_cog(Character(bot))
    print(f"{bot.user.name} 로그인 성공")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('폼폼 빠지게 일하는 중이니까 방해하지마 쿠뽀!'))

#######################################
#
#######################################


@app_commands.command(name="도움말", description="도움말을 출력합니다.")
async def 도움말(interaction: discord.Interaction):
    await interaction.response.send_message("도움말", ephemeral=True)

#######################################
# 전투
#######################################

class BattleInteraction(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(BattleButton(custom_id="attack", label="공격", style=discord.ButtonStyle.red))
        self.add_item(BattleButton(custom_id="defence", label="방어", style=discord.ButtonStyle.green))
        self.add_item(BattleButton(custom_id="skill", label="스킬", style=discord.ButtonStyle.blurple))
        return True

    async def attack(self, interaction: discord.Interaction):
        # 공격 로직
        return

    async def defence(self, interaction: discord.Interaction):
        # 방어 로직
        return

    async def skill(self, interaction: discord.Interaction):
        # 스킬 버튼 클릭 시 새로운 버튼 세트를 표시
        await interaction.response.send_message("스킬을 선택하세요:", view=SkillInteraction(), ephemeral=True)

class SkillInteraction(discord.ui.View):
    # ToDo
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="스킬 1", style=discord.ButtonStyle.blurple, custom_id="skill_1"))
        self.add_item(discord.ui.Button(label="스킬 2", style=discord.ButtonStyle.blurple, custom_id="skill_2"))
        self.add_item(discord.ui.Button(label="리미트 브레이크", style=discord.ButtonStyle.blurple, custom_id="skill_lb"))
    
    async def skill_1(self, interaction: discord.Interaction):
        # 스킬1 로직
        return

    async def skill_2(self, interaction: discord.Interaction):
        # 스킬2 로직
        return

    async def skill_lb(self, interaction: discord.Interaction):
        # 리밋 로직
        return


class BattleButton(discord.ui.Button['BattleInteraction']):
    def __init__(self, custom_id: str, label: str, style: discord.ButtonStyle):
        super().__init__(style=style, label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: BattleInteraction = self.view

        # 버튼의 custom_id를 기반으로 BattleInteraction의 메서드 호출
        if self.custom_id == "attack":
            await view.attack(interaction)
        elif self.custom_id == "defence":
            await view.defence(interaction)
        elif self.custom_id == "skill":
            await view.skill(interaction)
        else:
            await interaction.response.send_message(
                "알 수 없는 행동입니다. 다시 시도해주세요.", ephemeral=True
            )

@app_commands.command(name="행동", description="행동을 선택하세요.")
async def 행동(interaction: discord.Interaction):
    await interaction.response.send_message('네 차례야, 쿠뽀!', view=BattleInteraction())

@app_commands.command(name="코그 확인", description="(관리자용 커맨드) 등록된 코그 목록을 출력합니다.")
async def 코그출력(interaction: discord.Interaction):
    await interaction.response.send_message(str(bot.cogs), ephemeral=True)




bot.run(test_token)