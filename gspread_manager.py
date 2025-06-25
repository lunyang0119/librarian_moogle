import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import pytz
from utility import *
import logging

gc = gspread.service_account()

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("dogwood-method-448216-f4-4023cd31106c.json", scopes=SCOPE)
gspread_client = gspread.authorize(creds)

# 각 시트 객체
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

    async def group_update_act(target_id: int, group, option="y"):
        """ID와 그룹 이름을 입력하면 해당 캐릭터 및 적을 행동한 상태로 만듭니다. 기본 옵션은 y"""
        if group == "A":
            await group_a_update(target_id, "act", option)
        elif group == "B":
            await group_b_update(target_id, "act", option)
        else:
            print(f"act update group value is {group}")

    def is_true(value: str) -> bool:
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
                    if not is_true(value):  # Boolean 변환 함수 사용
                        return False
                return True
            elif group == "B":
                column_values = sheet_group_B.col_values(11)
                # 첫 번째 행(헤더)을 제외한 나머지 값 확인
                for value in column_values[1:]:  # 헤더 제외
                    if not is_true(value):  # Boolean 변환 함수 사용
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
