import discord
from discord import app_commands
import discord.ext
from discord.ext import commands
import asyncio
from gspread_manager import Character
from utility import Utility, Act, UserCheck
from discord_battle_system import BattleSystem
import logging

logger = logging.getLogger(__name__)

class Job(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        battle_system = BattleSystem(self.bot)

    async def comp_user_enemy_throw(self, interaction: discord.Interaction, enemy_id: int, max_retries: int = 3):
        """사용자와 적의 전투 결과를 판정합니다.
        
        Args:
            interaction: Discord 상호작용 객체
            enemy_id: 적 ID
            max_retries: 동점 시 최대 재시도 횟수
            
        Returns:
            bool: 사용자 승리 시 True, 적 승리 시 False, 에러 시 None
        """
        try:
            # 1. 사용자 데이터 검증
            user_id = interaction.user.id
            stats = await Character.get_user_values(user_id)
    
            if not stats:
                await self._safe_send_message(interaction, "캐릭터 정보를 찾을 수 없습니다.")
                return None
            
            group_name = stats[4]
            if group_name not in ["A", "B"]:
                logger.warning(f"Invalid group name for user {user_id}: {group_name}")
                return None
            
            # 2. 사용자 공격 굴림 계산
            battle_system = BattleSystem(self.bot)
            user_atk_roll = await battle_system.user_atk_success_roll(interaction)
    
            # 직업별 보정치 적용
            job_modifiers = {"tank": -2, "melee": -3, "ranged": -1, "heal": 0, "magic": 0}
            modifier = job_modifiers.get(stats[2], 0)
            user_atk_roll += modifier
    
            # 3. 적 데이터 가져오기 및 DC 계산
            enemy_val = await Character.get_enemy_values(self, group_name, enemy_id)
            if not enemy_val:
                logger.error(f"Enemy ID {enemy_id} not found in group {group_name}")
                return None
    
            try:
                enemy_dc = int(enemy_val[7]) + int(enemy_val[8]) + int(enemy_val[10])
            except (IndexError, ValueError) as e:
                logger.error(f"Error calculating enemy DC: {e}")
                return None
    
            # 4. 결과 판정
            if user_atk_roll > enemy_dc:
                return True  # 사용자 승리
            elif user_atk_roll < enemy_dc:
                return False  # 적 승리
            else:
                # 동점 처리
                if max_retries > 0:
                    logger.info(f"Tie in battle! Re-rolling... ({max_retries} retries left)")
                    return await self.comp_user_enemy_throw(interaction, enemy_id, max_retries - 1)
                else:
                    logger.warning("Max retries reached in battle tie. Defaulting to user victory.")
                    return True  # 기본값으로 사용자 승리
    
        except Exception as e:
            logger.error(f"Critical error in comp_user_enemy_throw: {e}")
            await self._safe_send_message(interaction, "전투 계산 중 오류가 발생했습니다.")
            return None
    
    async def _safe_send_message(self, interaction: discord.Interaction, message: str):
        """안전한 메시지 전송"""
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(message, ephemeral=True)
            else:
                await interaction.followup.send(message, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

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


    
