import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from models.character import Character

def authorize_gsheets():
    """
    구글 시트 인증을 처리합니다.
    """
    credentials_path = "dogwood-method-448216-f4-4023cd31106c.json"
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    return client

def load_players_from_sheet():
    """
    구글 시트에서 플레이어 데이터를 로드합니다.
    :return: 플레이어 리스트
    """
    client = authorize_gsheets()
    sheet = client.open("Discord_Bot").worksheet("UserData")
    players = []
    for row in sheet.get_all_records():
        players.append(Character(row["name"], {"str": row["str"], "agi": row["agi"]}, row["hp"]))
    return players

def load_monsters_from_sheet():
    """
    구글 시트에서 몬스터 데이터를 로드합니다.
    :return: 몬스터 리스트
    """
    client = authorize_gsheets()
    sheet = client.open("Discord_Bot").worksheet("MonsterData")
    records = sheet.get_all_records()
    monsters = []
    for row in records:
        monsters.append(Character(row["name"], {"str": row["str"], "agi": row["agi"]}, row["hp"]))
    return monsters

def load_bosses_from_sheet():
    """
    구글 시트에서 보스 데이터를 로드합니다.
    :return: 보스 리스트
    """
    client = authorize_gsheets()
    sheet = client.open("Discord_Bot").worksheet("BossData")
    bosses = []
    for row in sheet.get_all_records():
        bosses.append(Character(row["name"], {"str": row["str"], "agi": row["agi"]}, row["hp"]))
    return bosses