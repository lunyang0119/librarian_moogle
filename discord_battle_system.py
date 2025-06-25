import gspread_manager
import discord
from discord import app_commands
import discord.ext
from discord.ext import commands
import gspread_manager
from gspread_manager import Character
from utility import Utility, Act

class BattleSystem(commands.Cog):
    def _init__(self, bot):
        self.bot = bot
        self.character = Character(bot)
        self.utility = Utility(bot)

    async def user_turn_manager(self, interaction: discord.Interaction):
        user_id = int(interaction.user.id)
        stats = Character.get_user_values(self, user_id)
        group_name = stats[4]
        if group_name == "A":
            await Character.group_update_act(user_id, "A")
            allact = Character.all_act(self, "A")
            if allact == True:
                Character.add_turn(self, "A")
                return
            else:
                return
        elif group_name == "B":
            await Character.group_update_act(user_id, "B")
            allact = Character.all_act(self, "B")
            if allact == True:
                Character.add_turn(self, "B")
                return
            else:
                return
        else:
            print(f"user_turn_manager error. {user_id} isn't participating in battle.")

    async def user_atk_success_roll(self, interaction: discord.Interaction):
        user_id = int(interaction.user.id)
        stats = Character.get_user_values(self, user_id)
        ar_val = stats[11]
        roll = int(Utility.dice_roller(20)) + int(ar_val)
        return roll

    async def user_raw_damage(self, interaction: discord.Interaction):
        user_id = int(interaction.user.id)
        stats = Character.get_user_values(self, user_id)
        atk_dice = stats[6]
        ar_val = stats[11]
        roll = int(Utility.dice_roller(atk_dice)) + int(ar_val)
        return roll
    
    async def enemy_raw_damage(self, group_name: str, enemy_id: int):
        stats = Character.get_enemy_values(self, group_name, enemy_id)
        atk_dice = stats[6]
        ar_val = stats[11]
        roll = int(Utility.dice_roller(atk_dice)) + int(ar_val)
        return roll
    
    async def user_difficulty_class(self, interaction: discord.Interaction):
        user_id = int(interaction.user.id)
        stats = Character.get_user_values(self, user_id)
        user_dc = int(int(stats[7]) + int(stats[8]) + int(stats[10]))
        return user_dc
    
    async def battle_order_batch(self, group_name = "A"):
        """그룹의 적과 유저에게 순서를 부여"""
        group_map = {
            "A": "BattleGroupA",
            "B": "BattleGroupB"
        }
        enemy_map = {
            "A": "GroupAEnemy", 
            "B": "GroupBEnemy"
        }
        users = await Character.get_column_data(self, group_map[group_name], "id")
        enemies = await Character.get_column_data(self, enemy_map[group_name], "id")
        if not users or not enemies:
            print(f"No users or enemies found for group {group_name}")
            return
        dice_sides = len(users) + len(enemies)
        user_order = []

        while len(user_order) < len(users):
            user_roll = Utility.dice_roller(dice_sides)
            if user_roll not in user_order:
                user_order.append(user_roll)
        
        enemy_order = []

        while len(enemy_order) < len(enemies):
            enemy_roll = Utility.dice_roller(dice_sides)
            if enemy_roll not in user_order and enemy_roll:
                enemy_order.append(enemy_roll)

        try:
            group_sheet = getattr(gspread_manager, group_map[group_name])
            group_sheet.update(f"A2:A{len(user_order) + 1}", [[value] for value in user_order])

            # enemy_map 시트에 enemy_order 저장
            enemy_sheet = getattr(gspread_manager, enemy_map[group_name])
            enemy_sheet.update(f"A2:A{len(enemy_order) + 1}", [[value] for value in enemy_order])

            print(f"User order and enemy order successfully updated in sheets for group {group_name}.")
        except Exception as e:
            print(f"An error occurred while updating sheets: {e}")

    async def user_is_your_turn(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        stats = Character.get_user_values(user_id)
        group_name = stats[4]

        if group_name in ["A", "B"]:
            stats2 = Character.get_every_sheet_user_values(self, f"BattleGroup{group_name}", user_id)
            user_act = stats2[8]
            return Character.is_true(user_act)
        else:
            print(f"user_is_your_turn error by {user_id}.")
            return False
        
    async def group_logging(self, target_id, ):
        #TODO: 배틀 로그 말고 다른 로그 스프레드 시트를 만들어야 함.

    async def turn_over(self, group_name= "A"):
        #TODO: 배틀로그에 최종적으로 계산된 데미지와 버프 등과 사망여부 확인을 해줄 커맨드 

class BattleValidator:
    #TODO
    @staticmethod
    def validate_user_turn(user_id: int, group_name: str) -> bool:
        """사용자 턴 검증"""
        if not user_id or not group_name:
            return False
            
        # 그룹 참여 여부 확인
        # 턴 순서 확인
        # 행동 완료 여부 확인
        return True
    
class BattleState:
    #TODO
    def __init__(self, group_name: str):
        self.group_name = group_name
        self.current_turn = 0
        self.participants = []
        self.enemies = []
        
    async def advance_turn(self):
        """턴 진행 로직"""
        if self.all_participants_acted():
            self.current_turn += 1
            await self.reset_participant_actions()
            
    def all_participants_acted(self) -> bool:
        """모든 참가자가 행동했는지 확인"""
        # 구현...

    
        


# async def on_button_click(interaction: discord.Interaction):
#     custom_id = inter.data["custom_id"]
#     if custom_id == "attack":
#         pass
#     elif custom_id == "defence":
#         pass
#     elif custom_id == "skill":
#         pass
#     else:
#         emebed = discord.Embed(
#             title = "오류!",
#             description= "미안하지만 다시 시도해줘, 쿠뽀.",
#             color = 0x0000ff
#         )
#         await interaction.response.send_message(emebed=emebed, ephemeral=True)
