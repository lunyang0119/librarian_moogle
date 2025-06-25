import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import logging
import time # time 모듈 추가

gc = gspread.service_account(filename="dogwood-method-448216-f4-4023cd31106c.json")

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("dogwood-method-448216-f4-4023cd31106c.json", scopes=SCOPE)
gspread_client = gspread.authorize(creds)

def open_worksheet_with_retry(spreadsheet_name, worksheet_name, retries=5, delay=5):
    """API 오류 발생 시 재시도 로직을 포함하여 워크시트를 엽니다."""
    for i in range(retries):
        try:
            spreadsheet = gspread_client.open(spreadsheet_name)
            return spreadsheet.worksheet(worksheet_name)
        except gspread.exceptions.APIError as e:
            # 500번대 서버 오류일 경우에만 재시도
            if 500 <= e.response.status_code < 600:
                wait_time = delay * (i + 1)
                print(f"Google Sheets API 서버 오류 ({e.response.status_code}) 발생. {wait_time}초 후 재시도합니다... ({i + 1}/{retries})")
                time.sleep(wait_time) # 점차 대기 시간 증가
            else:
                raise # 그 외 다른 API 오류는 즉시 발생시킴
    raise Exception(f"{retries}번 재시도 후에도 '{worksheet_name}' 워크시트를 열 수 없습니다.")

# 각 시트 객체 (재시도 로직 적용)
sheet_user = open_worksheet_with_retry("Moogle_Escordia", "PlayerData")
sheet_boss = open_worksheet_with_retry("Moogle_Escordia", "BossData")
sheet_quests = open_worksheet_with_retry("Moogle_Escordia", "Quest")
sheet_BossLog = open_worksheet_with_retry("Moogle_Escordia", "BossBattleLog")
sheet_log_A = open_worksheet_with_retry("Moogle_Escordia", "BattleLogA")
sheet_log_B = open_worksheet_with_retry("Moogle_Escordia", "BattleLogB")
sheet_group_A = open_worksheet_with_retry("Moogle_Escordia", "BattleGroupA")
sheet_group_B = open_worksheet_with_retry("Moogle_Escordia", "BattleGroupB")
sheet_enemy_A = open_worksheet_with_retry("Moogle_Escordia", "GroupAEnemy")
sheet_enemy_B = open_worksheet_with_retry("Moogle_Escordia", "GroupBEnemy")
sheet_shop = open_worksheet_with_retry("Moogle_Escordia", "ShopData")

logger = logging.getLogger(__name__)

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sheets = {
            "user": sheet_user,
            "group_A": sheet_group_A,
            "group_B": sheet_group_B,
            "char": sheet_user, 
            "BossData": sheet_boss,
            "Quest": sheet_quests,
            "BattleLogBoss": sheet_BossLog,
            "BattleLogA": sheet_log_A,
            "BattleLogB": sheet_log_B,
            "BattleGroupA": sheet_group_A,
            "BattleGroupB": sheet_group_B,
            "GroupAEnemy": sheet_enemy_A,
            "GroupBEnemy": sheet_enemy_B,
            "ShopData": sheet_shop
        }

    async def reload_sheet(self):
        global sheet_user, sheet_boss, sheet_quests, sheet_BossLog, sheet_log_A, sheet_log_B, sheet_group_A, sheet_group_B, sheet_enemy_A, sheet_enemy_B, sheet_shop
        sheet_user = gspread_client.open("Moogle_Escordia").worksheet("char")
        sheet_boss = gspread_client.open("Moogle_Escordia").worksheet("BossData")
        sheet_quests = gspread_client.open("Moogle_Escordia").worksheet("Quest")
        sheet_BossLog = gspread_client.open("Moogle_Escordia").worksheet("BossBattleLog")
        sheet_log_A = gspread_client.open("Moogle_Escordia").worksheet("BattleLogA")
        sheet_log_B = gspread_client.open("Moogle_Escordia").worksheet("BattleLogB")
        sheet_group_A = gspread_client.open("Moogle_Escordia").worksheet("BattleGroupA")
        sheet_group_B = gspread_client.open("Moogle_Escordia").worksheet("BattleGroupB")
        sheet_enemy_A = gspread_client.open("Moogle_Escordia").worksheet("GroupAEnemy")
        sheet_enemy_B = gspread_client.open("Moogle_Escordia").worksheet("GroupBEnemy")
        sheet_shop = gspread_client.open("Moogle_Escordia").worksheet("ShopData")

    def get_user_row_number(self, user_id: int):
        try:
            cell = sheet_user.find(str(user_id))
            return cell.row
        except gspread.exceptions.CellNotFound:
            print(f"User ID {user_id} not found in the sheet.")
            return None

    def get_user_values(self, user_id: int):
        try:
            cell = sheet_user.find(str(user_id))
            return sheet_user.row_values(cell.row)
        except gspread.exceptions.CellNotFound:
            logger.warning(f"User {user_id} not found in sheet")
            return None
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {e}")
            raise
        
    async def get_enemy_values(self, group_name: str, enemy_id: int):
        try:
            # group_name에 따라 동적으로 시트 객체 가져오기
            sheet_map = {
                "A": sheet_enemy_A,
                "B": sheet_enemy_B
            }
            sheet = sheet_map.get(group_name)
            if not sheet:
                raise ValueError(f"Invalid group name: {group_name}")
            # enemy_id를 시트에서 검색
            cell = sheet.find(str(enemy_id))
            row_idx = cell.row
            return sheet.row_values(row_idx)
        except gspread.exceptions.CellNotFound:
            print(f"{enemy_id} not found in the sheet.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    async def get_every_sheet_user_values(self, sheet_name: str, user_id: int):
        try:
            sheet_map = {
                "char": sheet_user,
                "BossData": sheet_boss,
                "Quest": sheet_quests,
                "BattleLogBoss": sheet_BossLog,
                "BattleLogA": sheet_log_A,
                "BattleLogB": sheet_log_B,
                "BattleGroupA": sheet_group_A,
                "BattleGroupB": sheet_group_B,
                "GroupAEnemy": sheet_enemy_A,
                "GroupBEnemy": sheet_enemy_B,
                "ShopData": sheet_shop,
            }
            sheet = sheet_map.get(sheet_name)
            if not sheet:
                raise ValueError(f"Invalid sheet name: {sheet_name}")
            cell = sheet.find(str(user_id))
            row_idx = cell.row
            return sheet_user.row_values(row_idx)
        except gspread.exceptions.CellNotFound:
            print(f"User ID {user_id} not found in the sheet.")
            return None
        
    async def get_column_data(self, sheet_name: str, column_name: str):
        """
        특정 시트와 열 이름을 기반으로 데이터를 가져옵니다.
        """
        try:
            # 시트 객체 가져오기
            sheet_map = {
                "char": sheet_user,
                "BossData": sheet_boss,
                "Quest": sheet_quests,
                "BattleLogBoss": sheet_BossLog,
                "BattleLogA": sheet_log_A,
                "BattleLogB": sheet_log_B,
                "BattleGroupA": sheet_group_A,
                "BattleGroupB": sheet_group_B,
                "GroupAEnemy": sheet_enemy_A,
                "GroupBEnemy": sheet_enemy_B,
                "ShopData": sheet_shop,
            }

            sheet = sheet_map.get(sheet_name)
            if not sheet:
                raise ValueError(f"Invalid sheet name: {sheet_name}")

            # 첫 번째 행(헤더)에서 열 이름 찾기
            headers = sheet.row_values(1)  # 첫 번째 행을 헤더로 가정
            if column_name not in headers:
                raise ValueError(f"Column '{column_name}' not found in sheet '{sheet_name}'")

            column_index = headers.index(column_name) + 1  # 열 인덱스는 1부터 시작
            column_data = sheet.col_values(column_index)[1:]  # 헤더 제외한 데이터 반환
            return column_data

        except Exception as e:
            print(f"An error occurred while fetching column data: {e}")
            return None

    async def update_user_row(self, interaction: discord.Interaction, column_name: str, value):
        """
        특정 유저 ID와 열 이름을 기반으로 셀 값을 업데이트합니다.
        """
        try:
            user_id = int(interaction.user.id)
            # 유저 ID로 행 번호 찾기
            cell = sheet_user.find(str(user_id))
            row_number = cell.row

            # 첫 번째 행에서 열 이름 찾기
            headers = sheet_user.row_values(1)  # 첫 번째 행을 열 이름으로 가정
            if column_name in headers:
                col_number = headers.index(column_name) + 1  # gspread는 1부터 시작하는 인덱스 사용
                sheet_user.update_cell(row_number, col_number, str(value))
                print(f"Updated {column_name} for User ID {user_id} to {value}.")
            else:
                print(f"Column '{column_name}' not found in the sheet.")
        except gspread.exceptions.CellNotFound:
            print(f"User ID {user_id} not found in the sheet.")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def calculate_date(self):
        val = sheet_shop.cell(1, 4).value
        if not val:
            print("calculate_datetime error")
            return None
        try:
            val_date = datetime.strptime(val, "%Y-%m-%d")  # 날짜 형식에 맞게 수정
            current_time = datetime.now()
            cal_date = (current_time - val_date).days  # 날짜 차이 계산
            return cal_date
        except ValueError as e:
            print(f"Date parsing error: {e}")
            return None

    async def group_a_update(self, interaction: discord.Interaction, column_name: str, value):
        """
        특정 유저 ID와 열 이름을 기반으로 셀 값을 업데이트합니다.
        """
        try:
            user_id = int(interaction.user.id)
            cell = sheet_group_A.find(str(user_id))
            row_number = cell.row

            # 첫 번째 행에서 열 이름 찾기
            headers = sheet_group_A.row_values(1)  # 첫 번째 행을 열 이름으로 가정
            if column_name in headers:
                col_number = headers.index(column_name) + 1  # gspread는 1부터 시작하는 인덱스 사용
                sheet_group_A.update_cell(row_number, col_number, str(value))
                print(f"Updated {column_name} for User ID {user_id} to {value}.")
            else:
                print(f"Column '{column_name}' not found in the sheet.")
        except gspread.exceptions.CellNotFound:
            print(f"User ID {user_id} not found in the sheet.")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def group_b_update(self, interaction: discord.Interaction, column_name: str, value):
        """
        특정 유저 ID와 열 이름을 기반으로 셀 값을 업데이트합니다.
        """
        try:
            user_id = int(interaction.user.id)
            # 유저 ID로 행 번호 찾기
            cell = sheet_group_B.find(str(user_id))
            row_number = cell.row

            # 첫 번째 행에서 열 이름 찾기
            headers = sheet_group_B.row_values(1)  # 첫 번째 행을 열 이름으로 가정
            if column_name in headers:
                col_number = headers.index(column_name) + 1  # gspread는 1부터 시작하는 인덱스 사용
                sheet_group_B.update_cell(row_number, col_number, str(value))
                print(f"Updated {column_name} for User ID {user_id} to {value}.")
            else:
                print(f"Column '{column_name}' not found in the sheet.")
        except gspread.exceptions.CellNotFound:
            print(f"User ID {user_id} not found in the sheet.")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def group_update_act(self, target_id: int, group, option="y"):
        """ID와 그룹 이름을 입력하면 해당 캐릭터 및 적을 행동한 상태로 만듭니다. 기본 옵션은 y"""
        if group == "A":
            await Character.group_a_update(target_id, "act", option)
        elif group == "B":
            await Character.group_b_update(target_id, "act", option)
        else:
            print(f"act update group value is {group}")

    def is_true(self, value: str) -> bool:
        """입력 값을 Boolean으로 변환"""
        lowered = value.lower()
        if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
            return True
        elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
            return False
        raise ValueError(f"Invalid boolean value: {value}")

    async def all_act(self, group: str):
        try:
            if group == "A":
                column_values = sheet_group_A.col_values(11)
                # 첫 번째 행(헤더)을 제외한 나머지 값 확인
                for value in column_values[1:]:  # 헤더 제외
                    if not self.is_true(value):  # Boolean 변환 함수 사용
                        return False
                return True
            elif group == "B":
                column_values = sheet_group_B.col_values(11)
                # 첫 번째 행(헤더)을 제외한 나머지 값 확인
                for value in column_values[1:]:  # 헤더 제외
                    if not self.is_true(value):  # Boolean 변환 함수 사용
                        return False
                return True
            else:
                print(f"all_act error by group {group}")
        except ValueError as ve:
            print(f"Invalid value encountered: {ve}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        
    async def add_turn(self, group_name: str):
        try:
            # 그룹별 시트 매핑
            sheet_map = {
                "A": sheet_log_A,
                "B": sheet_log_B
            }

            # 그룹 이름에 따른 시트 선택
            sheet = sheet_map.get(group_name)
            if not sheet:
                print(f"Invalid group name: {group_name}")
                return

            # 현재 턴 값 가져오기
            current_value = sheet.cell(2, 1).value
            if not current_value.isdigit():
                print(f"Invalid turn value in group {group_name}: {current_value}")
                return

            # 턴 값 증가
            new_value = int(current_value) + 1
            sheet.update_cell(1, 2, new_value)
            print(f"Turn updated for group {group_name}: {new_value}")

        except Exception as e:
            print(f"An error occurred while updating turn for group {group_name}: {e}")
        
    async def god_damn_sheets(self, sheet_name: str, row: int, column: int):
        """행과 열로 셀 값 가져오기"""
        try:
            # 시트 객체 가져오기
            sheet_map = {
                "char": sheet_user,
                "BossData": sheet_boss,
                "Quest": sheet_quests,
                "BattleLogBoss": sheet_BossLog,
                "BattleLogA": sheet_log_A,
                "BattleLogB": sheet_log_B,
                "BattleGroupA": sheet_group_A,
                "BattleGroupB": sheet_group_B,
                "GroupAEnemy": sheet_enemy_A,
                "GroupBEnemy": sheet_enemy_B,
                "ShopData": sheet_shop,
            }

            sheet = sheet_map.get(sheet_name)
            if not sheet:
                print(f"god_damn_sheets error. sheets not found.")
                return
            cell_val = sheet.cell(row, column).value
            return cell_val
        except Exception as e:
            print(f"An error occured while god_damn_sheets.")

    async def update_cell_values(self, sheet_name: str, row_number: int, column_number: int, value):
        """행과 열로 셀 값 수정. """
        try:
            sheet_map = {
                "char": sheet_user,
                "BossData": sheet_boss,
                "Quest": sheet_quests,
                "BattleLogBoss": sheet_BossLog,
                "BattleLogA": sheet_log_A,
                "BattleLogB": sheet_log_B,
                "BattleGroupA": sheet_group_A,
                "BattleGroupB": sheet_group_B,
                "GroupAEnemy": sheet_enemy_A,
                "GroupBEnemy": sheet_enemy_B,
                "ShopData": sheet_shop,
            }
            upd_sheet = sheet_map[sheet_name]
            upd_sheet.update_cell(row_number, column_number)
            print(f"update 완료")
        except gspread.exceptions.CellNotFound as e:
            print(f"An error occurred in update_cell_values: {e}")
        except Exception as e:
            print(f"An error occurred in update_cell_values: {e}")



    async def update_battle_participant_column(self, target_id: int, group_name: str, column_name: str, value):
        """특정 ID를 가진 참가자의 BattleGroup 시트 셀 값을 업데이트 합니다.(interaction 대신 target_discord_id를 직접 받음)"""
        try: 
            sheet_map = {
                "A": sheet_group_A,
                "B": sheet_group_B
            }
            
            sheet_update = sheet_map.get(group_name)
            if not sheet_update:
                print(f"There is no {group_name} group.")
                return
                
            cell = sheet_update.find(str(target_id))
            row_number = cell.row
            headers = sheet_update.row_values(1)
            if column_name in headers:
                col_number = headers.index(column_name)+1
                sheet_update.update_cell(row_number, col_number, str(value))
                print(f"update_battle_participant_column {column_name},for {target_id} in group {group_name} to {value}")
            else:
                print(f"Column {column_name} not found")
        except gspread.exceptions.CellNotFound as e:
            print(f"{target_id} not found in group {group_name} : {e}")
        except Exception as e:
            print(f"An error occurred in update_battle_participant_column: {e}")

    async def make_battle_id_part(self, interaction: discord.Interaction, group_name = "A"):
        """참가자의 데이터를 시트에 올림"""
        user_id = interaction.user.id
        sheet_map = {
            "A": sheet_group_A,
            "B": sheet_group_B
        }
        if group_name in ("A", "B"):
            await Character.update_user_row(self, interaction, "battle_id", group_name)  # interaction 객체 전달
            stats = await Character.get_user_values(self, user_id)
            new_row = ["", user_id, stats[1], "", 0, "","","","", "", "n"]
            sheet_map[group_name].append_row(new_row) 
        else:
            print(f"make_battle_id_part error. user_id: {user_id}")

    async def make_battle_enemy_id(self, group_name = "A"):
        """적 시트에 enemy_0부터 시작하는 ID를 2열에 부여"""
        try:
            sheet_map = {
                "A": sheet_enemy_A,
                "B": sheet_enemy_B
            }
            
            if group_name in ("A", "B"):
                enemy_sheet = sheet_map[group_name]
                
                # 시트의 모든 데이터 가져오기
                all_values = enemy_sheet.get_all_values()
                
                if len(all_values) <= 1:  # 헤더만 있거나 빈 시트인 경우
                    print(f"Group {group_name} enemy sheet has no enemy data")
                    return False
                
                # 헤더 제외한 실제 적 데이터 수 계산
                enemy_count = len(all_values) - 1  # 첫 번째 행(헤더) 제외
                
                # enemy_0부터 시작하는 ID 리스트 생성
                enemy_ids = [f"enemy_{i}" for i in range(enemy_count)]
                
                # 2열(B열)에 ID 업데이트 (2행부터 시작)
                start_row = 2
                end_row = start_row + enemy_count - 1
                
                # 범위 지정해서 한번에 업데이트
                cell_range = f"B{start_row}:B{end_row}"
                enemy_sheet.update(cell_range, [[enemy_id] for enemy_id in enemy_ids])
                
                print(f"Successfully assigned IDs to {enemy_count} enemies in group {group_name}")
                print(f"Enemy IDs: {enemy_ids}")
                
                return True
                
            else:
                print(f"Invalid group name: {group_name}")
                return False
                
        except Exception as e:
            print(f"An error occurred while assigning enemy IDs for group {group_name}: {e}")
            return False

    async def clear_sheet_data(self, sheet_name: str, preserve_headers: bool = True):
        """특정 시트의 데이터를 모두 지움 (선택적으로 헤더 보존)"""
        try:
            sheet_map = {
                "char": sheet_user,
                "BossData": sheet_boss,
                "Quest": sheet_quests,
                "BattleLogBoss": sheet_BossLog,
                "BattleLogA": sheet_log_A,
                "BattleLogB": sheet_log_B,
                "BattleGroupA": sheet_group_A,
                "BattleGroupB": sheet_group_B,
                "GroupAEnemy": sheet_enemy_A,
                "GroupBEnemy": sheet_enemy_B,
                "ShopData": sheet_shop,
            }
            
            sheet = sheet_map.get(sheet_name)
            if not sheet:
                print(f"Invalid sheet name: {sheet_name}")
                return False
                
            # 시트의 모든 데이터 가져오기
            all_values = sheet.get_all_values()
            
            if not all_values:
                print(f"Sheet {sheet_name} is already empty")
                return True
                
            if preserve_headers and len(all_values) > 1:
                # 헤더 보존: 2번째 행부터 삭제
                start_row = 2
                end_row = len(all_values)
                range_to_clear = f"A{start_row}:Z{end_row}"
                sheet.batch_clear([range_to_clear])
                print(f"Sheet {sheet_name} cleared (headers preserved)")
            elif not preserve_headers:
                # 모든 데이터 삭제 (헤더 포함)
                end_row = len(all_values)
                range_to_clear = f"A1:Z{end_row}"
                sheet.batch_clear([range_to_clear])
                print(f"Sheet {sheet_name} completely cleared")
            else:
                print(f"Sheet {sheet_name} has only headers, nothing to clear")
                
            return True
            
        except Exception as e:
            print(f"An error occurred while clearing sheet {sheet_name}: {e}")
            return False

    async def make_battle_log_group_clear(self, group_name = "A"):
        """그룹의 로그와 그룹 시트에 있는 데이터를 모두 지움(헤더 제외)"""
        try:
            if group_name in ("A", "B"):
                # 그룹 시트 클리어 (헤더 제외)
                group_sheet_name = f"BattleGroup{group_name}"
                group_result = await self.clear_sheet_data(group_sheet_name, preserve_headers=True)
                
                # 로그 시트 클리어 (헤더 제외)  
                log_sheet_name = f"BattleLog{group_name}"
                log_result = await self.clear_sheet_data(log_sheet_name, preserve_headers=True)
                
                if group_result and log_result:
                    print(f"Successfully cleared group {group_name} data (headers preserved)")
                    return True
                else:
                    print(f"Failed to clear some sheets for group {group_name}")
                    return False
                    
            else:
                print(f"failed to reset group {group_name}. please try again.")
                return False
                
        except Exception as e:
            print(f"An error occurred while clearing group {group_name}: {e}")
            return False

    async def _get_turn_order(self, group_name: str, target_type: str):
        """턴 순서를 구글시트에서 가져오는 함수"""
        try:
            if target_type == "user":
                if group_name == "A":
                    names = Character.get_column_data(self, "BattleGroupA", "name")
                    rolls = Character.get_column_data(self, "BattleGroupA", "turn_order")  # 턴 순서 컬럼
                elif group_name == "B":
                    names = Character.get_column_data(self, "BattleGroupB", "name")
                    rolls = Character.get_column_data(self, "BattleGroupB", "turn_order")
            elif target_type == "enemy":
                if group_name == "A":
                    names = Character.get_column_data(self, "GroupAEnemy", "name")
                    rolls = Character.get_column_data(self, "GroupAEnemy", "turn_order")
                elif group_name == "B":
                    names = Character.get_column_data(self, "GroupBEnemy", "name")
                    rolls = Character.get_column_data(self, "GroupBEnemy", "turn_order")
            
            # 이름과 주사위 결과를 조합하여 정렬
            if names and rolls:
                combined = list(zip(names, rolls))
                # 주사위 결과 내림차순으로 정렬
                combined.sort(key=lambda x: int(x[1]), reverse=True)
                return combined
            return []
            
        except Exception as e:
            print(f"Error getting turn order: {e}")
            return []




    @app_commands.command(name="내스탯", description="내 스탯을 확인합니다.")
    async def 내스탯(self, interaction: discord.Interaction):
        """
        캐릭터 스탯을 확인하는 커맨드
        """
        display_name = interaction.user.display_name 
        user_id = interaction.user.id

        # 사용자 행 번호 가져오기
        row_idx = await self.get_user_row_number(user_id)
        if not row_idx:
            await interaction.response.send_message(
                "❌ 미등록 사용자야, 쿠뽀. 먼저 `/스탯등록` 해줘.", ephemeral=True
            )
            return

        # 사용자 스탯 정보 가져오기
        stats = await self.get_user_values(user_id)
        if not stats:
            await interaction.response.send_message(
                "❌ 스탯 정보를 가져올 수 없어! 관리자에게 문의해, 쿠뽀.", ephemeral=True
            )
            return

        # Embed 메시지 생성
        embed = discord.Embed(
            title=f"{display_name}님의 스탯",
            colour=0x00FF00
        )
        embed.add_field(name="이름", value=stats[1], inline=True)
        embed.add_field(name="직업", value=stats[2], inline=True)
        embed.add_field(name="현재 전투 참가 여부", value=stats[3], inline=True)
        embed.add_field(name="전투 그룹", value=stats[4], inline=True)
        embed.add_field(name="HP", value=stats[5], inline=True)
        embed.add_field(name="공격 주사위", value=stats[6], inline=True)
        embed.add_field(name="근력", value=stats[7], inline=True)
        embed.add_field(name="민첩", value=stats[8], inline=True)
        embed.add_field(name="건강", value=stats[9], inline=True)
        embed.add_field(name="지능", value=stats[10], inline=True)
        embed.add_field(name="보정치", value=stats[11], inline=True)
        embed.add_field(name="스킬 1", value=stats[12], inline=True)
        embed.add_field(name="설명:", value=stats[15], inline=False)
        embed.add_field(name="스킬 2", value=stats[13], inline=True)
        embed.add_field(name="설명:", value=stats[16], inline=False)
        embed.add_field(name="리미트 브레이크", value=stats[14], inline=True)
        embed.add_field(name="설명:", value=stats[17], inline=False)

        # Embed 메시지 전송
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="캐릭터생성", description="새로운 캐릭터를 생성합니다.")
    @app_commands.describe(
        캐릭터명="캐릭터의 이름을 입력하세요",
        직업="직업을 선택하세요 (tank/healer/melee/ranged/magic)"
    )
    async def 캐릭터생성(self, interaction: discord.Interaction, 캐릭터명: str, 직업: str):
        """캐릭터를 생성하고 구글 시트에 등록합니다."""
        try:
            user_id = interaction.user.id
            
            # 1. 이미 등록된 유저인지 확인
            existing_stats = self.get_user_values(user_id)
            if existing_stats:
                await interaction.response.send_message(
                    f"❌ 이미 등록된 캐릭터가 있어, 쿠뽀! \n"
                    f"기존 캐릭터: **{existing_stats[1]}** ({existing_stats[2]})\n"
                    f"새로운 캐릭터를 만들고 싶다면 관리자에게 문의해줘.",
                    ephemeral=True
                )
                return
                
            # 2. 직업 유효성 검사
            valid_jobs = ["tank", "healer", "melee", "ranged", "magic"]
            if 직업.lower() not in valid_jobs:
                await interaction.response.send_message(
                    f"❌ 잘못된 직업이야, 쿠뽀! \n"
                    f"사용 가능한 직업: **{', '.join(valid_jobs)}**",
                    ephemeral=True
                )
                return
                
            # 3. 캐릭터명 중복 확인
            all_names = await self.get_column_data("char", "name")
            if 캐릭터명 in all_names:
                await interaction.response.send_message(
                    f"❌ **{캐릭터명}** 은(는) 이미 사용 중인 이름이야, 쿠뽀! 다른 이름을 선택해줘.",
                    ephemeral=True
                )
                return
                
            # 4. 직업별 기본 스탯 설정
            base_stats = self._get_job_base_stats(직업.lower())
            
            # 5. 새 캐릭터 데이터 생성
            new_character_data = [
                user_id,                    # A: id (Discord ID)
                캐릭터명,                   # B: name
                직업.lower(),               # C: job
                0,                          # D: battle_participants (전투 참가 여부)
                "",                         # E: battle_id (전투 그룹)
                base_stats["hp"],           # F: hp
                base_stats["attack_dice"],  # G: attack_dice (공격 주사위)
                base_stats["strength"],     # H: strength (근력)
                base_stats["dexterity"],    # I: dexterity (민첩)
                base_stats["constitution"], # J: constitution (건강)
                base_stats["intelligence"], # K: intelligence (지능)
                base_stats["modifier"],     # L: modifier (보정치)
                base_stats["skill1"],       # M: skill1
                base_stats["skill2"],       # N: skill2
                base_stats["limit_break"],  # O: limit_break
                base_stats["skill1_desc"],  # P: skill1_description
                base_stats["skill2_desc"],  # Q: skill2_description
                base_stats["lb_desc"]       # R: limit_break_description
            ]
            
            # 6. 구글 시트에 추가
            sheet_user.append_row(new_character_data)
            
            # 7. 성공 메시지 생성
            embed = discord.Embed(
                title="🎉 캐릭터 생성 완료!",
                description=f"**{캐릭터명}** ({직업})이(가) 성공적으로 생성되었어, 쿠뽀!",
                color=0x00FF00
            )
            
            embed.add_field(name="📊 기본 스탯", value=f"""
            **HP**: {base_stats['hp']}
            **공격 주사위**: {base_stats['attack_dice']}
            **근력**: {base_stats['strength']} | **민첩**: {base_stats['dexterity']}
            **건강**: {base_stats['constitution']} | **지능**: {base_stats['intelligence']}
            **보정치**: {base_stats['modifier']}
            """, inline=False)
            
            embed.add_field(name="🎯 스킬 정보", value=f"""
            **스킬 1**: {base_stats['skill1']}
            **스킬 2**: {base_stats['skill2']}
            **리미트 브레이크**: {base_stats['limit_break']}
            """, inline=False)
            
            embed.add_field(name="📖 사용법", value="""
            `/내스탯` - 캐릭터 정보 확인
            `/전투준비` - 전투 참가
            `/행동` - 전투 중 행동 선택
            """, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            logger.info(f"New character created: {캐릭터명} ({직업}) for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            await interaction.response.send_message(
                "❌ 캐릭터 생성 중 오류가 발생했어, 쿠뽀! 관리자에게 문의해줘.",
                ephemeral=True
            )

    def _get_job_base_stats(self, job: str) -> dict:
        """직업별 기본 스탯을 반환합니다."""
        job_stats = {
            "tank": {
                "hp": 30,  # 기본 10 + 건강 2*5 + 직업 보너스 10
                "attack_dice": "1d12",
                "strength": 8,
                "dexterity": 4,
                "constitution": 5,
                "intelligence": 3,
                "modifier": 8,  # 근력 기반
                "skill1": "대신받기",
                "skill2": "무적화",
                "limit_break": "전체 보호",
                "skill1_desc": "아군 한 명이 받는 공격을 대신 받습니다. 받는 피해는 50% 감소. (3턴간)",
                "skill2_desc": "한 턴 동안 모든 공격이 무효화됩니다.",
                "lb_desc": "2턴간 모든 아군이 받는 공격을 대신 받으며, 첫 턴은 무적, 둘째 턴은 50% 감소, 셋째 턴은 70% 감소"
            },
            "healer": {
                "hp": 15,  # 기본 10 + 건강 2*5 - 힐러 페널티
                "attack_dice": "1d10",
                "strength": 3,
                "dexterity": 6,
                "constitution": 5,
                "intelligence": 8,
                "modifier": 8,  # 민첩/지능 중 높은 값
                "skill1": "단일 회복",
                "skill2": "전체 회복",
                "limit_break": "완전 회복",
                "skill1_desc": "지정 대상을 최대 HP까지 회복합니다.",
                "skill2_desc": "아군 전체를 1d10+보정치만큼 회복합니다.",
                "lb_desc": "모든 아군을 최대 HP로 회복하고, 전투불능 아군도 소생시킵니다."
            },
            "melee": {
                "hp": 25,  # 기본 10 + 건강 2*5 + 직업 보너스 5
                "attack_dice": "1d20",
                "strength": 8,
                "dexterity": 5,
                "constitution": 5,
                "intelligence": 2,
                "modifier": 8,  # 근력 기반
                "skill1": "강화 공격",
                "skill2": "연속 공격",
                "limit_break": "필살 일격",
                "skill1_desc": "적 하나에게 1d20+근력+1d10의 피해를 줍니다.",
                "skill2_desc": "적 하나에게 1d20+근력+1d20의 피해를 줍니다.",
                "lb_desc": "적 하나에게 2d20+근력의 강력한 피해를 줍니다."
            },
            "ranged": {
                "hp": 20,  # 기본 10 + 건강 2*5
                "attack_dice": "1d20",
                "strength": 4,
                "dexterity": 8,
                "constitution": 5,
                "intelligence": 3,
                "modifier": 8,  # 민첩 기반
                "skill1": "출혈 공격",
                "skill2": "광역 공격",
                "limit_break": "상태이상 난사",
                "skill1_desc": "전체 적에게 출혈 상태를 부여합니다. (5턴간 매턴 1d5 피해)",
                "skill2_desc": "전체 적에게 1d20+민첩-1d5의 피해를 줍니다.",
                "lb_desc": "모든 적에게 랜덤 상태이상을 부여하고 1d20+민첩+1d5의 피해를 줍니다."
            },
            "magic": {
                "hp": 15,  # 기본 10 + 건강 2*5 - 마법사 페널티
                "attack_dice": "1d20",
                "strength": 2,
                "dexterity": 5,
                "constitution": 5,
                "intelligence": 8,
                "modifier": 8,  # 지능 기반
                "skill1": "마비 공격",
                "skill2": "지연 공격",
                "limit_break": "대화염",
                "skill1_desc": "전체 적에게 마비를 부여합니다. (3턴간 50% 확률로 행동 불가)",
                "skill2_desc": "적 하나에게 1d20+지능+1d25의 피해를 줍니다. (1턴 후 발동, 시전 후 1턴 행동 불가)",
                "lb_desc": "모든 적에게 발화 상태를 부여하고 2d20+1d10의 피해를 줍니다."
            }
        }
        
        return job_stats.get(job, job_stats["melee"])  # 기본값은 melee