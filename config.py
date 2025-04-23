# config.py

import os
import gspread
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 구글 서비스 계정 인증
gc = ServiceAccountCredentials.from_json_keyfile_name("dogwood-method-448216-f4-4023cd31106c.json", scope)

# 구글 시트 ID 및 범위
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# 각 시트 탭 이름
PLAYER_SHEET_NAME = "Players"
MONSTER_SHEET_NAME = "Monsters"
BOSS_SHEET_NAME = "Bosses"

# 시트 열 범위 설정 (필요 시 수정)
PLAYER_RANGE = "A1:Z100"
MONSTER_RANGE = "A1:Z100"
BOSS_RANGE = "A1:Z100"

def get_worksheet(sheet_name: str):
    """시트 이름으로 worksheet 객체를 반환"""
    sh = gc.open_by_key(SPREADSHEET_ID)
    return sh.worksheet(sheet_name)
