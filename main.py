import os
import discord 
from discord import app_commands
from discord.ext import commands
from commands.admin_commands import AdminCommands
from commands.battle_commands import BattleCommands
from dependencies import combat_session, sheet_user, material_sheet, boss
from engine.combat_engine import Boss
from engine.combat_session import CombatSession
import asyncio

# 디버깅용: 콘솔에 경고 로그 이상만 표시
import logging
logging.basicConfig(level=logging.WARNING)

# Discord 봇 초기화
intents = discord.Intents.default()
intents.messages = True
intents.messages = True

intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

TOKEN = "token" 

class aclient(discord.Client):
    def __init__(self):
         super().__init__(intents = discord.Intents.all())
         self.synced = False
    async def on_ready(self):
         await self.wait_until_ready()
         if not self.synced: 
             await tree.sync() 
             self.synced = True

client = aclient()
tree = bot.tree

# CombatSession 객체 생성
combat_session = CombatSession([], [])

# 보스 객체 생성 (예시)
boss = Boss(
    name="Boss1",
    stats={"str": 20, "agi": 10},
    hp=500,
    dialogue_80="분노한다!",
    dialogue_40="최후의 발악!",
    dialogue_0="패배했다...",
    skill_multiplier_80=2.0,
    skill_multiplier_40=3.0
)

############################
#
# 다이스 명령어어
#
#####################################

@tree.command(name="모그리", description="랜덤 대사를 출력합니다.")
async def 모그리(interaction: discord.Interaction):
    dialogues = [
        "너희 차원엔 다 나 같은 유능한 모그리가 있을 거야 쿠뽀?\n 물론 나보단 못하겠지만 쿠뽀!",
        "왜 굳이 이 곳에 있는거야 쿠뽀?\n너희들은 집이 있잖아.",
        "혹시 너희 차원에도 모그리를 귀찮게 하는 규칙 같은 게 있냐 쿠뽀?",
        "쿠뽀! 책 정리가 아니라 혼돈을 창조하러 온 거냐 쿠뽀?",
        "책장 하나 찾는데 차원이 세 개는 소멸하겠다 쿠뽀. 좀 더 빠르게 움직여 쿠뽀!",
        "이곳의 기록은 소중해, 쿠뽀!\n 더 상냥하게 다루란 말이야!",
        "별은 언젠가 빛을 잃기 마련이지만, 기억해주는 마음이 있다면 절대 사라지지 않아 쿠뽀.",
        "나한테 말을 걸 정도로 한가해? 그럼 일 해, 쿠뽀!",
        "모든 기록은 결국 과거가 되지만, 이 도서관의 책 속에서는 아직도 살아 숨 쉬고 있어, 쿠뽀.",
        "기억이 책처럼 쉽게 펼쳐지고 덮일 수 있다면 얼마나 좋을까, 쿠뽀.",
        "너희는 언젠가 돌아갈 차원이 있지만, 나는 이곳 말고 돌아갈 곳이 없어, 쿠뽀.",
        "별들이 사라질 때 얼마나 외로웠을까… 마지막까지 그걸 바라본 건 나뿐이었어.",
        "책을 읽는 건 기록 때문만이 아니야. 다시 만날 수 없는 이들을 기억하기 위해서이기도 해, 쿠뽀."
    ]
    await interaction.response.send_message(random.choice(dialogues))

@tree.command(name="챗", description="서버채널 정보를 이용해 메시지를 전송합니다.")
async def 챗(interaction: discord.Interaction, server_name: str, channel_name: str, *, message: str):
    records = server_channel_sheet.get_all_records()
    matched = next((row for row in records if row.get("서버이름", "").lower() == server_name.lower() and 
                    row.get("채널이름", "").lower() == channel_name.lower()), None)
    if not matched:
        await interaction.response.send_message(f"❌ 서버 '{server_name}'와 채널 '{channel_name}' 정보를 찾을 수 없습니다.", ephemeral=True)
        return
    try:
        channel_id = int(matched.get("채널ID"))
    except (TypeError, ValueError):
        await interaction.response.send_message("❌ 채널 ID가 올바른 숫자가 아닙니다.", ephemeral=True)
        return
    channel = bot.get_channel(channel_id)
    # 채널 ID 유효성 검사 추가
    if channel is None:
        await interaction.response.send_message(f"❌ 채널 ID '{channel_id}'로 채널을 찾을 수 없습니다. 봇 초대 여부를 확인하세요.", ephemeral=True)
        return
    await channel.send(message)
    await interaction.response.send_message(f"✅ {channel.mention}로 메시지를 전송했습니다!")

@tree.command(name="젠장쿠뽀", description="특별한 메시지를 출력합니다.")
async def 젠장쿠뽀(interaction: discord.Interaction):
    responses = {
        1: "이게 코드라고 쓴 거냐, 아니면 몬스터 소환 주문이냐 쿠뽀?", 
        2: "너의 코드는 버그마저 버그를 낳는다 쿠뽀!", 
        3: "에러 메시지가 너무 많아서 로그가 소설책이 됐어 쿠뽀.", 
        4: "이딴 식으로 짤 거면 컴퓨터를 주고 초코보를 타라 쿠뽀!",
        5: "도움말은 도움말!이다 쿠뽀! 네 코드에선 그게 전혀 도움이 안 되겠지만 쿠뽀!", 
        6: "너의 알고리즘은 미궁보다 더 미궁이야 쿠뽀.", 
        7: "이 코드엔 주석이 아니라 변명이 필요한 거 아니냐 쿠뽀?",
        8: "너 때문에 이곳이 버그 사육장이 됐다 쿠뽀!", 
        9: "차라리 내 뭉툭한 손으로 짜는 게 빠르겠다 쿠뽀!", 
        10: "코딩은 재능이 아니라고 했지만, 너를 보니 재능이 확실히 필요한 거 같다 쿠뽀!"
    }
    roll = random.randint(1, 10)
    embed = discord.Embed(title="**사서쿠뽀의 한마디**", description=responses[roll], colour=0x00FF00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="주사위", description="1d10 주사위를 굴립니다.")
async def 주사위(interaction: discord.Interaction):
    roll = random.randint(1, 10)
    embed = discord.Embed(title="**주사위**", description=f"**{roll}**", colour=0x00FF00)
    await interaction.response.send_message(embed=embed)

@tree.command(name="책찾기", description="랜덤 책을 뽑습니다.")
async def 책찾기(interaction: discord.Interaction):
    roll = random.randint(1, 10)
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
        10: "허기가 지거나, 지치거나, 허무할 만큼 아무것도 찾지 못했다."
    }
    embed = discord.Embed(
        title=f"**{interaction.user.display_name}이(가) 책을 뽑았어, 쿠뽀!**",
        description=f"**{roll}** → **{responses[roll]}**",
        colour=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="일반행동", description="일반 행동을 수행합니다.")
@app_commands.describe(option="응답에서 하나만 무작위로 선택할지 여부 (y: 하나만 선택, n: 전체 문자열; 기본값은 n)")
async def 일반행동(interaction: discord.Interaction, option: str = "n"):
    roll = random.randint(1, 10)
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
        10: "시간만 낭비했다 / 감정이 격해졌다 / 미묘했다"
    }
    resp_text = responses[roll]
    if option.lower() == "y":
        # 슬래시 ("/")를 기준으로 잘라서 3가지 중 하나를 랜덤 선택합니다.
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

@tree.command(name="전투행동", description="전투 행동을 수행합니다.")
@app_commands.describe(option="응답에서 하나만 무작위로 선택할지 여부 (y: 하나만 선택, n: 전체 문자열; 기본값은 n)")
async def 전투행동(interaction: discord.Interaction, option: str = "n"):
    roll = random.randint(1, 10)
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
        10: "일어났다 / 버텼다 / 돌진했다"
    }
    resp_text = responses[roll]
    if option.lower() == "y":
        # 슬래시 ("/")를 기준으로 잘라서 3가지 중 하나를 랜덤 선택합니다.
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

@tree.command(name="대인행동", description="대인행동을 수행합니다.")
@app_commands.describe(option="응답에서 하나만 무작위로 선택할지 여부 (y: 하나만 선택, n: 전체 문자열; 기본값은 n)")
async def 대인행동(interaction: discord.Interaction, option: str = "n"):
    roll = random.randint(1, 10)
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
        10: "반응이 없다 / 비웃는다 / 사과한다"
    }
    resp_text = responses[roll]
    if option.lower() == "y":
        # 슬래시 ("/")를 기준으로 잘라서 3가지 중 하나를 랜덤 선택합니다.
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

@tree.command(name="행동", description="효과가 없다 / 있다의 결과가 나오는 1d2 주사위를 굴립니다.")
async def 행동(interaction: discord.Interaction):
    # `/행동` 명령어에서 결과 메시지 랜덤화
    result = random.choice(["효과가 있어보여 쿠뽀!", "아무 일도 일어나지 않았어 쿠뽀...."])
    embed = discord.Embed(
        title=f"{interaction.user.display_name}이(가) 행동했어, 쿠뽀!",
        description=f"{result}",
        colour=0x00FF00
    )
    await interaction.response.send_message(embed=embed)


###################################


##################################
async def setup(bot):
    # AdminCommands와 BattleCommands에 필요한 객체를 전달
    await bot.add_cog(AdminCommands(bot, combat_session, sheet_user, material_sheet))
    await bot.add_cog(BattleCommands(bot))

# 봇 준비 완료 이벤트
@bot.event
async def on_ready():
    try:
        # 슬래시 커맨드 동기화
        await bot.tree.sync()
        print(f"슬래시 커맨드가 동기화되었습니다.")
    except Exception as e:
        print(f"슬래시 커맨드 동기화 중 오류 발생: {e}")

async def main():
    await setup(bot)
    await bot.start(TOKEN)
    print(f"{bot.user} 로그인 완료! 명령어 동기화 완료!")

asyncio.run(main())
