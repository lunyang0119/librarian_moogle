import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 구글 시트 연동
def authorize_gsheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def get_sheets(client):
    sheet = client.open("TRPG")
    user_data = sheet.worksheet("UserData")
    monster_data = sheet.worksheet("MonsterData")
    boss_data = sheet.worksheet("BossData")
    return user_data, monster_data, boss_data

# 사용 예시
if __name__ == "__main__":
    client = authorize_gsheets()
    user_sheet, monster_sheet, boss_sheet = get_sheets(client)
    print("시트 연동 완료")


# # 구글 시트 연동
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
# gc = gspread.authorize(credentials)

# # 시트 열기
# user_sheet = gc.open("TRPG_DB").worksheet("UserData")
# monster_sheet = gc.open("TRPG_DB").worksheet("MonsterData")
# boss_sheet = gc.open("TRPG_DB").worksheet("BossData")

# # 예시 함수: 유저 데이터 불러오기
# def get_user_data():
#     return user_sheet.get_all_records()

# # 예시 함수: 몬스터 데이터 불러오기
# def get_monster_data():
#     return monster_sheet.get_all_records()

# # 예시 함수: 보스 데이터 불러오기
# def get_boss_data():
#     return boss_sheet.get_all_records()