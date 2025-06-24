import discord
from discord import app_commands
import discord.ext
from discord.ext import commands
import asyncio
from gspread_manager import Character
from utility import Utility, Act, UserCheck
from discord_battle_system import BattleSystem

class Job(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    async def comp_user_enemy_throw(self, interaction: discord.Interaction, enemy_id: int):
        """user가 이기면 True, enemy가 이기면 False"""
        try:
            user_id = interaction.user.id
            stats = await Character.get_user_values(self, user_id)  # 비동기 호출
            group_name = stats[4]
    
            if group_name not in ["A", "B"]:
                print(f"Invalid group name: {group_name}")
                return None
            
            # 직업에 따른 내성굴림
            if stats[2] == "tank":
            # 사용자 공격 성공 굴림
                user_atk_roll = await BattleSystem.user_atk_success_roll(interaction)
                user_atk_roll = user_atk_roll - 2 
            elif stats[2] == "melee":
                user_atk_roll = await BattleSystem.user_atk_success_roll(interaction)
                user_atk_roll = user_atk_roll - 3
            elif stats[2] == "ranged":
                user_atk_roll = await BattleSystem.user_atk_success_roll(interaction)
                user_atk_roll = user_atk_roll - 1
            else:
                user_atk_roll = await BattleSystem.user_atk_success_roll(interaction)
    
            # 적 데이터 가져오기
            enemy_val = await Character.get_enemy_values(self, group_name, enemy_id)  # 비동기 호출
            if not enemy_val:
                print(f"Enemy ID {enemy_id} not found in group {group_name}.")
                return None
    
            # 적의 난이도 클래스 계산
            try:
                enemy_dc = int(enemy_val[7]) + int(enemy_val[8]) + int(enemy_val[10])
            except (IndexError, ValueError) as e:
                print(f"Error calculating enemy DC: {e}")
                return None
    
            # 결과 비교
            if user_atk_roll > enemy_dc:
                return True  # 사용자 승리
            elif user_atk_roll < enemy_dc:
                return False  # 적 승리
            else:
                # 동점 처리 로직
                print("It's a tie! Re-rolling...")
                return await self.comp_user_enemy_throw(interaction, enemy_id)  # 재귀 호출
    
        except Exception as e:
            print(f"An error occurred in comp_user_enemy_throw: {e}")
            return None

    async def user_skill1_logic(self, interaction: discord.Interaction, target_id: int):
        try: 
            user_id = interaction.user.id
            stats = Character.get_user_values(user_id)
            group_name = stats[4]
            job = stats[2]

            if group_name in ["A", "B"]:
                if job == "tank":
                    target_stats = await Character.get_user_values(self, target_id)
                    if not target_stats:
                        await interaction.response.send_message("대상 아군을 찾을 수 없습니다.", ephemeral=True)
                        return
                    # 적의 공격 피해 계산 (예: 적의 공격 성공 굴림)
                    enemy_damage = await BattleSystem.enemy_raw_damage(self, group_name, target_id)
                    if enemy_damage is None:
                        await interaction.response.send_message("적의 공격 데이터를 가져오는 데 실패했습니다.", ephemeral=True)
                        return

                    # 피해를 절반으로 줄임
                    mitigated_damage = enemy_damage // 2

                    await Character.group_a_update(self, target_id, "buff", "buff_tskill_1")
                    await Character.group_a_update(self, target_id, "buff_turn", 4)

                    # 결과 메시지 출력
                    await interaction.response.send_message(
                        f"{interaction.user.display_name}님이 다음 턴 부터 {target_stats[1]}의 피해를 대신 받습니다! "
                        f"받은 피해: {mitigated_damage}",
                        ephemeral=True
                    )

    except Exception as e:
        print(f"An error occurred in user_skill1_logic: {e}")
        await interaction.response.send_message("스킬 실행 중 오류가 발생했습니다.", ephemeral=True)


    
