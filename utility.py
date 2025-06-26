import random
import discord
from discord import app_commands
import discord.ext
from discord.ext import commands
import time
import datetime
import asyncio
from gspread_manager import Character

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @staticmethod
    def dice_roller(sides: int):
        dice = random.randint(1, sides)
        return dice

    async def shop_reset(self, bot: discord.ext.commands.Bot):
        while True:
            today = datetime.date.today()
            today_week = today.weekday()
            # 1은 월요일, 2는 월요일, 7은 일요일
            if today_week == 1:
                #대충 상점 리셋하는 코드 - ToDo
                shop_channel = bot.get_channel('1382624387059941446')
                await shop_channel.send('상점이 리셋되었어 쿠뽀!')
                await asyncio.sleep(86400)
            else: 
                await asyncio.sleep(86400)


class Act(commands.Cog):
    def _init__(self, bot):
        self.bot = bot

    @app_commands.command(name='대인행동', description="대인행동")
    @app_commands.describe(option="y: 3개의 응답 중 하나만 선택; 기본값은 n")
    async def 대인행동(self, interaction: discord.Interaction, option: str = "n"):
        roll = Utility.dice_roller(10)
        responses = {
            1: "협력한다 / 애원한다 / 웃는다", 
            2: "굴복한다 / 안도한다 / 협상한다", 
            3: "망설인다 / 무시한다 / 화를 낸다", 
            4: "우호적이다 / 거짓말한다 / 두려워한다",
            5: "경계한다 / 위로한다 / 당황한다", 
            6: "신뢰한다 / 시큰둥해 한다 / 침묵한다", 
            7: "대가를 요구한다 / 약속한다 / 의심한다",
            8: "적대한다 / 알려준다 / 슬퍼한다", 
            9: "만족해 한다 / 협박한다 / 허락한다", 
            10: "반응이 없다 / 비웃는다 / 사과한다"}
        resp_text = responses[roll]
        if option.lower() == "y":
            parts = [part.strip() for part in resp_text.split("/")]
            chosen_resp = random.choice(parts)
        else:
            chosen_resp = resp_text

        embed = discord.Embed(
            title=f"{interaction.user.display_name}이(가) 행동했어, 쿠뽀!",
            description=f"**{roll}** → **{chosen_resp}**",
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='일반행동', description="일반행동")
    @app_commands.describe(option="y: 3개의 응답 중 하나만 선택; 기본값은 n")
    async def 일반행동(self, interaction: discord.Interaction, option: str = "n"):
        roll = Utility.dice_roller(10)
        responses = {
            1: "기대보다 효과적이었다 / 사람이 더 필요하다 / 사라졌다",
            2: "예상치 못한 문제가 발생했다 / 만족스러웠다 / 힘만 뺐다", 
            3: "아무 일도 일어나지 않았다 / 불쾌해졌다 / 기억났다", 
            4: "성공한 건지 잘 모르겠다 / 난장판이 되었다 / 찾아냈다",
            5: "그럭저럭 해냈다 / 원래대로 돌아왔다 / 위험했다", 
            6: "시간이 더 필요하다 / 뜻밖의 수확이 있었다 / 고통을 유발했다", 
            7: "반쯤은 해냈다 / 사소한 문제가 생겼다 / 망가졌다",
            8: "목표를 이루었다 / 막대한 손실을 입었다 / 바뀌었다", 
            9: "약간은 진척이 있었다 / 자원만 낭비했다 / 만들었다", 
            10: "시간만 낭비했다 / 감정이 격해졌다 / 미묘했다"}
        resp_text = responses[roll]
        if option.lower() == "y":
            parts = [part.strip() for part in resp_text.split("/")]
            chosen_resp = random.choice(parts)
        else:
            chosen_resp = resp_text

        embed = discord.Embed(
            title=f"{interaction.user.display_name}이(가) 행동했어, 쿠뽀!",
            description=f"**{roll}** → **{chosen_resp}**",
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='전투행동', description="전투행동")
    @app_commands.describe(option="y: 3개의 응답 중 하나만 선택; 기본값은 n")
    async def 전투행동(self, interaction: discord.Interaction, option: str = "n"):
        roll = Utility.dice_roller(10)
        responses = {
            1: "적중했다 / 숨겼다 / 떨어졌다", 
            2: "빗나갔다 / 바꾸었다 / 무너뜨렸다", 
            3: "피했다 / 빼앗았다 / 늦었다", 
            4: "붙잡았다 / 넘어졌다 / 접근했다",
            5: "막았다 / 노렸다 / 살폈다", 
            6: "들켰다 / 쫓았다 / 터졌다", 
            7: "아슬아슬했다 / 멈추었다 / 던졌다",
            8: "고통스럽다 / 밀었다 / 물러났다", 
            9: "흔들렸다 / 기다렸다 / 부딪쳤다", 
            10: "일어났다 / 버텼다 / 돌진했다"}
        resp_text = responses[roll]
        if option.lower() == "y":
            parts = [part.strip() for part in resp_text.split("/")]
            chosen_resp = random.choice(parts)
        else:
            chosen_resp = resp_text

        embed = discord.Embed(
            title=f"{interaction.user.display_name}이(가) 행동했어, 쿠뽀!",
            description=f"**{roll}** → **{chosen_resp}**",
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='책찾기', description="10가지 유형의 책 중 랜덤하게 하나를 뽑습니다.")
    async def 책찾기(self, interaction: discord.Interaction):
        roll = Utility.dice_roller(10)
        responses = {
            1: "우리 중 누군가와 똑같은 이름을 가진 인물이 등장하는 이야기가 쓰여 있는 책을 발견했다.", 
            2: "날카로운 이빨로 사람을 깨무는 책을 발견했다.", 
            3: "자극적인 막장 연애 소설을 발견했다.", 
            4: "책 한 권을 뽑으려 했을 뿐인데 옆에 있던 책들까지 와르르 쏟아져 나왔다.",
            5: "책장 건너편의 누군가와 눈이 마주쳤다. ", 
            6: "꼭 읽어 보고 싶을 만큼 흥미로운 제목이 적힌 책을 발견했다.", 
            7: "여러 권의 시리즈인데 순서가 제멋대로 섞인 채로 꽂혀 있는 것을 발견했다.",
            8: "책 사이에 끼여 있던 편지를 발견했다.",
            9: "이 책에는 유독 먼지가 심각하게 많이 쌓여 있었다.", 
            10: "허기가 지거나, 지치거나, 허무할 만큼 아무것도 찾지 못했다."}
        resp_text = responses[roll]

        embed = discord.Embed(
            title=f"{interaction.user.display_name}이(가) 책을 뽑았어, 쿠뽀!",
            description=f"**{roll}** → **{resp_text}**",
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="행동", description="효과가 있다 / 없다")
    async def 행동(self, interaction: discord.Interaction):
        result = random.choice(["효과가 있어보여 쿠뽀!", "아무 일도 일어나지 않았어 쿠뽀...."])
        embed = discord.Embed(
            title=f"{interaction.user.display_name}이(가) 행동했어, 쿠뽀!",
            description=f"{result}",
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

# class UserCheck(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @app_commands.command(name="시트업뎃", description="구글 시트를 다시 불러옵니다.")
#     async def 시트업뎃(self, interaction: discord.Interaction):
#         try:
#             character_cog = self.bot.get_cog('Character')
#             if character_cog:
#                 await character_cog.reload_sheet()
#                 await interaction.response.send_message("✅ 구글 시트를 성공적으로 다시 불러왔습니다, 쿠뽀!")
#             else:
#                 await interaction.response.send_message("❌ 캐릭터 관리 모듈을 찾을 수 없어, 쿠뽀!", ephemeral=True)
#         except Exception as e:
#             await interaction.response.send_message(f"❌ 시트를 다시 불러오는 중 오류가 발생했습니다: {e}", ephemeral=True)

    # @app_commands.command(name="코인보유량", description="내 코인 보유량을 확인합니다.")
    # async def 내코인(interaction: discord.Interaction):
    #     #ToDo