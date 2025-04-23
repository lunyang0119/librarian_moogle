from engine.combat_session import CombatSession
from engine.combat_engine import Boss
from sheets.sheet_loader import authorize_gsheets

# CombatSession 객체 생성
combat_session = CombatSession([], [])

# 구글 시트 인증 및 데이터 로드
gspread_client = authorize_gsheets()
sheet_user = gspread_client.open("Discord_Bot").worksheet("UserData")
material_sheet = gspread_client.open("Discord_Bot").worksheet("MaterialData")

# 보스 객체 생성
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