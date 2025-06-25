import discord
from discord import app_commands
import asyncio
from discord.ext import commands
import random 
import os 
from dotenv import load_dotenv
from gspread_manager import Character
from discord_battle_system import BattleSystem
from job import Job
import traceback

load_dotenv()

moogle_token = os.getenv('moogle_token')
test_token = os.getenv('test_token')

# Bot initialization
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
activity = discord.Activity(type=discord.ActivityType.watching, name="!start")
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    
    # 로드할 Cog 클래스 목록
    cogs_to_load = [
        Character,
        BattleSystem,
        Job,
        Utility,
        Act,
        UserCheck
    ]
    
    # 상세한 로그와 함께 Cog 로드
    for cog_class in cogs_to_load:
        try:
            # 클래스의 인스턴스를 생성하여 cog로 추가
            await bot.add_cog(cog_class(bot))
            print(f"✅ Cog '{cog_class.__name__}' loaded successfully.")
            await bot.change_presence(status=discord.Status.online, activity=discord.Game('폼폼 빠지게 일하는 중이니까 방해하지마 쿠뽀!'))
        except Exception as e:
            # 오류 발생 시 어떤 Cog에서 문제인지 출력
            print(f"❌ Failed to load cog '{cog_class.__name__}':")
            traceback.print_exc() # 전체 오류 트레이스백 출력

    # 슬래시 커맨드 동기화
    try:
        # 특정 서버(길드)에만 동기화하여 속도 향상 (테스트 시 권장)
        # guild = discord.Object(id=YOUR_SERVER_ID) # 여기에 테스트 서버 ID를 숫자로 입력
        # synced = await bot.tree.sync(guild=guild)
        
        # 모든 서버에 동기화 (전역)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands:")
        traceback.print_exc()
    

#######################################
#
#######################################


@app_commands.command(name="도움말", description="도움말을 출력합니다.")
async def 도움말(interaction: discord.Interaction):
    await interaction.response.send_message("도움말", ephemeral=True)

#######################################
# 전투
#######################################

class BattleInteraction(discord.ui.View):
    """유저 행동을 위한 버튼 뷰"""
    def __init__(self):
        super().__init__()
        self.add_item(BattleButton(custom_id="attack", label="공격", style=discord.ButtonStyle.red))
        self.add_item(BattleButton(custom_id="defence", label="방어", style=discord.ButtonStyle.green))
        self.add_item(BattleButton(custom_id="skill", label="스킬", style=discord.ButtonStyle.blurple))
        return True

    async def attack(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        await interaction.response.send_message(
            "공격 대상을 선택하세요:", 
            view=AttackTargetSelect(user_id), 
            ephemeral=True
        )
        return

    async def defence(self, interaction: discord.Interaction):
        # 방어 로직
        return

    async def skill(self, interaction: discord.Interaction):
        # 스킬 버튼 클릭 시 새로운 버튼 세트를 표시
        await interaction.response.send_message("스킬을 선택하세요:", view=SkillInteraction(), ephemeral=True)

class AttackTargetSelect(discord.ui.View):
    def __init__(self, user_id: int):
        """
        공격 로직
        """
        super().__init__(timeout=300)
        self.user_id = user_id
        self._add_enemy_buttons(user_id)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """상호작용 권한 검증"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "본인만 사용할 수 있습니다.", ephemeral=True
            )
            return False
        return True
    
    async def on_timeout(self):
        """타임아웃 처리"""
        for item in self.children:
            item.disabled = True

    def _add_enemy_buttons(self, user_id):
        """적 대상 버튼들 추가"""
        stats = Character.get_user_values(user_id)
        group_name = stats[5]
        if group_name == "A":
            enemies = Character.get_column_data(self, "GroupAEnemy", "name")
        elif group_name == "B":
            enemies = Character.get_column_data(self, "GroupBEnemy", "name")
        else:
            print(f"add_enemy_button groupname error. {group_name}")
        for index, enemy in enumerate(enemies):
            self.add_item(discord.ui.Button(
                    label=enemy, 
                    style=discord.ButtonStyle.red, 
                    custom_id=f"enemy_{index}"  
            ))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """버튼 클릭 이벤트 처리"""
        target_id = interaction.data['custom_id']
        await self._handle_attack(interaction, target_id)        
        return True
    
    async def _handle_attack(self, interaction: discord.Interaction, target_id: str):
        """공격 처리 로직"""
        # target_id에서 적의 인덱스 추출 (예: enenmy_0 -> "0")
        enemy_index = target_id.split("_")[1]
        user_id = interaction.user.id
        stats = Character.get_user_values(user_id)
        group_name = stats[4]

        if group_name == "A":
            enemies = Character.get_column_data(self, "GroupAEnemy", "name")
        elif group_name == "B":
            enemies = Character.get_column_data(self, "GroupBEnemy", "name")
        else: 
            await interaction.response.send_message("그룹 정보를 찾을 수 없어, 쿠뽀.... 오류인가봐 쿠뽀.", ephemeral=True)
            return
        try:
            enemy_name = enemies[int(enemy_index)]
            #TODO: 공격 로직 구현
            Job.comp_user_enemy_throw(self, user_id, enemy_id)
            await interaction.response.send_message(f"{interaction.user.display_name}이(가) {enemy_name}을 공격했습니다!")
        except (IndexError, ValueError):
            await interaction.response.send_message("잘못된 대상이야 쿠뽀.", ephemeral=True)
    


class BattleButton(discord.ui.Button['BattleInteraction']):
    """BattleInteraction을 위한 로직"""
    def __init__(self, custom_id: str, label: str, style: discord.ButtonStyle):
        super().__init__(style=style, label=label, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: BattleInteraction = self.view

        # 버튼의 custom_id를 기반으로 BattleInteraction의 메서드 호출
        if self.custom_id == "attack":
            await view.attack(interaction)
        elif self.custom_id == "defence":
            await view.defence(interaction)
        elif self.custom_id == "skill":
            await view.skill(interaction)
        else:
            await interaction.response.send_message(
                "알 수 없는 행동입니다. 다시 시도해주세요.", ephemeral=True
            )


class SkillInteraction(discord.ui.View):
    """스킬 버튼. 스킬 id와 직업에 따른 target_type 전달."""
    # TODO: user_id를 어떻게 전달할지 고려 필요
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="스킬 1", style=discord.ButtonStyle.blurple, custom_id="skill_1"))
        self.add_item(discord.ui.Button(label="스킬 2", style=discord.ButtonStyle.blurple, custom_id="skill_2"))
        self.add_item(discord.ui.Button(label="리미트 브레이크", style=discord.ButtonStyle.blurple, custom_id="skill_lb"))
    
    async def skill_1(self, interaction: discord.Interaction):
        user_job = await self._get_user_job(interaction.user.id)
        if user_job == "tank":
            target_type = "ally"
        elif user_job == "heal":
            target_type = "ally_and_self"
        elif user_job in ("melee", "ranged", "magic"):
            target_type = "enemy"
        else:
            print(f"skill_1 user_job error: {user_job}")
            
        await interaction.response.send_message(
            "스킬1 대상을 선택하세요:", 
            view=SkillTargetSelect("skill_1", target_type), 
            ephemeral=True
        )

    async def skill_2(self, interaction: discord.Interaction):
        user_job = await self._get_user_job(interaction.user.id)
        
        if user_job == "tank":
            target_type = "all_ally"
        elif user_job == "heal":
            target_type = "all_ally"  # 전체 아군 회복
        elif user_job == "ranged":
            target_type = "all_enemy"  # 전체 적 공격
        else:
            target_type = "enemy"  # 단일 적 공격
            
        await interaction.response.send_message(
            "스킬2 대상을 선택하세요:", 
            view=SkillTargetSelect("skill_2", target_type), 
            ephemeral=True
        )

    async def skill_lb(self, interaction: discord.Interaction):
        user_job = await self._get_user_job(interaction.user.id)
        
        if user_job == "힐러":
            target_type = "all_ally"
        elif user_job in ["원딜(물리)", "원딜(마법)"]:
            target_type = "all_enemy"
        else:
            target_type = "enemy"
            
        await interaction.response.send_message(
            "리미트 브레이크 대상을 선택하세요:", 
            view=SkillTargetSelect("limit_break", target_type), 
            ephemeral=True
        )
    
    async def _get_user_job(self, user_id: int):
        """사용자의 직업을 구글시트에서 가져오는 함수"""
        stats = Character.get_user_values(user_id)
        job = stats[2]
        if job in ("tank", "heal", "melee", "ranged", "magic"):
            return job
        else:
            print(f"{interaction.user.display_name}'s job: {job}. There is no {job}")


class SkillTargetSelect(discord.ui.View):
    def __init__(self, skill_type: str, target_type: str = "enemy"):
        """
        범용 스킬 대상 선택 로직
        
        Args:
            skill_type: "skill_1", "skill_2", "limit_break" 등
            target_type: "user_self", "enemy", "ally", "all", "ally_or_self" 등
        """
        super().__init__()
        self.skill_type = skill_type
        self.target_type = target_type
        
        # 대상 유형에 따라 버튼 생성
        if target_type == "enemy":
            self._add_enemy_buttons()
        elif target_type == "ally":
            self._add_ally_buttons()
        elif target_type == "ally_and_self":
            self._add_ally_buttons()
            self.add_item(discord.ui.Button(label="자기자신", style=discord.ButtonStyle.blurple, custom_id="self"))
        elif target_type == "all_enemy":
            self.add_item(discord.ui.Button(label="모든 적", style=discord.ButtonStyle.red, custom_id="all_enemies"))
        elif target_type == "all_ally":
            self.add_item(discord.ui.Button(label="모든 아군", style=discord.ButtonStyle.green, custom_id="all_allies"))
        elif target_type == "user_self":
            self.add_item(discord.ui.Button(label="자기자신", style=discord.ButtonStyle.blurple, custom_id="self"))

    
    def _add_enemy_buttons(self, interaction: discord.Interaction):
        """적 대상 버튼들 추가"""
        user_id = interaction.user.id
        stats = Character.get_user_values(user_id)
        group_name = stats[5]
        if group_name == "A":
            enemies = Character.get_column_data(self, "GroupAEnemy", "name")
        elif group_name == "B":
            enemies = Character.get_column_data(self, "GroupBEnemy", "name")
        else:
            print(f"add_enemy_button groupname error. {group_name}")
        for index, enemy in enumerate(enemies):
            self.add_item(discord.ui.Button(
                label=enemy, 
                style=discord.ButtonStyle.red, 
                custom_id=f"enemy_{index}"  
            ))
    
    def _add_ally_buttons(self, interaction: discord.Interaction):
        """아군 대상 버튼들 추가"""
        user_id = interaction.user.id
        stats = Character.get_user_values(user_id)
        group_name = stats[5]
        if group_name == "A":
            allies = Character.get_column_data(self, "BattleGroupA", "name")
        elif group_name == "B":
            allies = Character.get_column_data(self, "BattleGroupB", "name")
        else:
            print(f"add_ally_button groupname error. {group_name}")
        for index, ally in enumerate(allies):
            self.add_item(discord.ui.Button(
                label=ally, 
                style=discord.ButtonStyle.red, 
                custom_id=f"ally_{index}"  
            ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """버튼 클릭 이벤트 처리"""
        target_id = interaction.data['custom_id']
        
        # 스킬 타입에 따라 적절한 처리 함수 호출
        if self.skill_type == "skill_1":
            await self._handle_skill_1(interaction, target_id)
        elif self.skill_type == "skill_2":
            await self._handle_skill_2(interaction, target_id)
        elif self.skill_type == "limit_break":
            await self._handle_limit_break(interaction, target_id)
        
        return True
    
    async def _handle_skill_1(self, interaction: discord.Interaction, target_id: str):
        """스킬1 처리 로직"""
        if self.target_type == "ally":
            # 아군 대상 스킬1 (예: 힐러의 단일 회복)
            await interaction.response.send_message(f"스킬1을 {target_id}에게 사용했습니다!", ephemeral=True)
        elif self.target_type == "enemy":
            # 적 대상 스킬1 (예: 공격 스킬)
            await interaction.response.send_message(f"스킬1로 {target_id}을(를) 공격했습니다!", ephemeral=True)
    
    async def _handle_skill_2(self, interaction: discord.Interaction, target_id: str):
        """스킬2 처리 로직"""
        if self.target_type == "all_ally":
            # 전체 아군 대상 스킬2 (예: 힐러의 전체 회복)
            await interaction.response.send_message("스킬2로 모든 아군을 회복했습니다!", ephemeral=True)
        elif self.target_type == "all_enemy":
            # 전체 적 대상 스킬2 (예: 광역 공격)
            await interaction.response.send_message("스킬2로 모든 적을 공격했습니다!", ephemeral=True)
        elif self.target_type == "enemy":
            # 단일 적 대상 스킬2
            await interaction.response.send_message(f"스킬2로 {target_id}을(를) 공격했습니다!", ephemeral=True)
    
    async def _handle_limit_break(self, interaction: discord.Interaction, target_id: str):
        """리미트 브레이크 처리 로직"""
        await interaction.response.send_message(f"리미트 브레이크를 사용했습니다! 대상: {target_id}", ephemeral=True)



@app_commands.command(name="전투준비", description="그룹을 선택하여 전투합니다.")
@app_commands.describe(option="그룹명: A, B, boss 중 하나 선택; 기본값은 A")
async def 전투준비(interaction: discord.Interaction, option: str = "A"):
    user_id = interaction.user.id
    lowered = option.lower()
    if lowered == "a":
        await Character.make_battle_log_group_clear(self, "A")  #해당 그룹 시트 초기화
        await Character.make_battle_id_part(self, user_id, "A") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "A")
        await Character.make_battle_enemy_id(self, "A")
        await interaction.response.send_message("{interaction.user.display_name}의 A그룹 로그 리셋 및 참가가 완료되었어 쿠뽀.\n참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    elif lowered == "b":
        await Character.make_battle_log_group_clear(self, "B")  #해당 그룹 시트 초기화
        await Character.make_battle_id_part(self, user_id, "B") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "B")
        await Character.make_battle_enemy_id(self, "B")
        await interaction.response.send_message("{interaction.user.display_name}의 B그룹 로그 리셋 및 참가가 완료되었어 쿠뽀.\n참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    elif lowered == "boss":
        await Character.make_battle_log_group_clear(self, "boss")  #해당 그룹 시트 초기화
        await Character.make_battle_id_part(self, user_id, "boss") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "boss")
        await Character.make_battle_enemy_id(self, "boss")
        await interaction.response.send_message(f"{interaction.user.display_name}의 보스전 로그 리셋 및 참가가 완료되었어 쿠뽀.\n참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    else:
        print(f"전투준비 option error: {option}")
        await interaction.response.send_message("미안하지만 그룹 이름이 잘못 입력된 것 같아, 쿠뽀. 다시 한 번 입력해줄래?\nA나 B, 혹은 boss를 입력하면 돼. 소문자로 입력해도 괜찮아.", ephemeral=True)

@app_commands.command(name="전투참가", description="그룹을 선택하여 전투에 참가합니다.")
@app_commands.describe(option="그룹명: A, B, boss 중 하나 선택; 기본값은 A")
async def 참가(interaction: discord.Interaction, option: str = "A"):
    user_id = interaction.user.id
    lowered = option.lower()
    if lowered == "a":
        await Character.make_battle_id_part(self, user_id, "A") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "A")
        await interaction.response.send_message("{interaction.user.display_name}의 A그룹 로그 리셋 및 참가가 완료되었어 쿠뽀.\n더 참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    elif lowered == "b":
        await Character.make_battle_id_part(self, user_id, "B") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "B")
        await interaction.response.send_message("{interaction.user.display_name}의 B그룹 로그 리셋 및 참가가 완료되었어 쿠뽀.\n더 참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    elif lowered == "boss":
        await Character.make_battle_id_part(self, user_id, "boss") #해당 그룹 시트에 유저 데이터 올림
        await Character.update_user_row(self, user_id, "battle_participants", 1)
        await Character.update_user_row(self, user_id, "battle_id", "boss")
        await interaction.response.send_message("{interaction.user.display_name}의 보스전 참가가 완료되었어 쿠뽀.\n더 참가할 사람들은 `/참가` 커맨드를 써주고, 참가자가 모두 모였다면 `/준완`으로 전투를 시작해줘 쿠뽀.")
    else:
        print(f"전투준비 option error: {option}")
        await interaction.response.send_message("미안하지만 그룹 이름이 잘못 입력된 것 같아, 쿠뽀. 다시 한 번 입력해줄래?\nA나 B, 혹은 boss를 입력하면 돼. 소문자로 입력해도 괜찮아.", ephemeral=True)

@app_commands.command(name="준완", description="그룹을 선택하여 전투를 개시합니다.")
@app_commands.describe(option="그룹명: A, B, boss 중 하나 선택; 기본값은 A")
async def 준완(interaction: discord.Interaction, option: str = "A"):
    lowered = option.lower()
    if lowered == "a":
        await Character.update_cell_values(self, "BattleLogA", 2, 1, 0)
        user_list = Character.get_column_data(self, "BattleGroupA", "name")
        enemy_list = Character.get_column_data(self, "GroupAEnemy", "name")
        await BattleSystem.user_turn_manager(self, interaction.user.id)
        embed2 = discord.Embed(
            title = "A그룹 전투개시!",
            description="전투를 개시합니다!",
            color = 0x0000ff
        )
        embed = discord.Embed(
            title = "A그룹 참가자",
            color = 0x00ff00
        )
        embed3 = discord.Embed(
            title = "A그룹 전투 대상",
            color = 0x00ff00
        )

        # 아군 리스트 추가
        if user_list:
            user_names = "\n".join([f"• {user}" for user in user_list])
            embed.add_field(
                name="참가 아군",
                value=user_names,
                inline=False
            )
        else:
            embed.add_field(
                name="참가 아군",
                value="참가자가 없습니다.",
                inline=False
            )
        
        # 적 리스트 추가
        if enemy_list:
            enemy_names = "\n".join([f"• {enemy}" for enemy in enemy_list])
            embed3.add_field(
                name="적 목록",
                value=enemy_names,
                inline=False
            )
        else:
            embed3.add_field(
                name="적 목록",
                value="적이 없습니다.",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(embed=embed2)
        await interaction.response.send_message(embed=embed3)

        embed = discord.Embed(
            title="순서 정하는 중...",
            description= "잠시만 기다려줘, 쿠뽀뽀.",
            color= 0x00ff00
        )
        order_message = await interaction.followup.send(embed=order_embed)

        await BattleSystem.battle_order_batch(self, "A")

        user_order = await Character._get_turn_order(self, "A", "user")
        enemy_order = await Character._get_turn_order(self, "A", "enemy")
        
        # 턴 순서 embed 생성
        turn_embed = discord.Embed(
            title="🎲 A그룹 진행 순서",
            color=0xffd700
        )
        # 아군 턴 순서
        if user_order:
            user_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                       for i, (name, roll) in enumerate(user_order)])
            turn_embed.add_field(
                name="🛡️ 아군 행동 순서",
                value=user_turn_text,
                inline=True
            )
        
        # 적 턴 순서
        if enemy_order:
            enemy_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                        for i, (name, roll) in enumerate(enemy_order)])
            turn_embed.add_field(
                name="⚔️ 적 행동 순서",
                value=enemy_turn_text,
                inline=True
            )
        
        turn_embed.add_field(
            name="📋 정말 시작!",
            value="이제 순서대로 `/행동`을 입력해서 전투를 시작해줘 쿠뽀!",
            inline=False
        )
        
        # 기존 "순서 정하는 중" 메시지를 턴 순서로 교체
        await order_message.edit(embed=turn_embed)


    elif lowered == "b":
        # B그룹도 동일한 로직 적용
        await Character.update_cell_values(self, "BattleLogB", 2, 1, 0)
        user_list = Character.get_column_data(self, "BattleGroupB", "name")
        enemy_list = Character.get_column_data(self, "GroupBEnemy", "name")
        
        embed = discord.Embed(
            title="B그룹 참가 아군 리스트",
            description="전투 준비가 완료되었습니다!",
            color=0xff0000
        )
        
        # 아군/적 리스트 추가 (위와 동일한 로직)
        if user_list:
            user_names = "\n".join([f"• {user}" for user in user_list])
            embed.add_field(name="참가 아군", value=user_names, inline=False)
        else:
            embed.add_field(name="참가 아군", value="참가자가 없습니다.", inline=False)
        
        if enemy_list:
            enemy_names = "\n".join([f"• {enemy}" for enemy in enemy_list])
            embed.add_field(name="적 목록", value=enemy_names, inline=False)
        else:
            embed.add_field(name="적 목록", value="적이 없습니다.", inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        # B그룹 턴 순서도 동일하게 처리
        order_embed = discord.Embed(
            title="순서 정하는 중...",
            description="잠시만 기다려줘, 쿠뽀뽀.",
            color=0x00ff00
        )
        order_message = await interaction.followup.send(embed=order_embed)
        
        await BattleSystem.battle_order_batch(self, "B")
        
        user_order = await Character._get_turn_order(self, "B", "user")
        enemy_order = await Character._get_turn_order(self, "B", "enemy")
        
        turn_embed = discord.Embed(
            title="🎲 B그룹 진행 순서",
            color=0xffd700
        )
        
        if user_order:
            user_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                       for i, (name, roll) in enumerate(user_order)])
            turn_embed.add_field(name="🛡️ 아군 행동 순서", value=user_turn_text, inline=True)
        
        if enemy_order:
            enemy_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                        for i, (name, roll) in enumerate(enemy_order)])
            turn_embed.add_field(name="⚔️ 적 행동 순서", value=enemy_turn_text, inline=True)
        
        turn_embed.add_field(name="📋 정말 시작!", value="이제 순서대로 `/행동`을 입력해서 전투를 시작해줘 쿠뽀!", inline=False)
        
        await order_message.edit(embed=turn_embed)
        
    elif lowered == "boss":
        # B그룹도 동일한 로직 적용
        await Character.update_cell_values(self, "BattleLogBoss", 2, 1, 0)
        user_list = Character.get_column_data(self, "BattleGroupBoss", "name")
        enemy_list = Character.get_column_data(self, "BossData", "name")
        
        embed = discord.Embed(
            title="B그룹 참가 아군 리스트",
            description="전투 준비가 완료되었습니다!",
            color=0xff0000
        )
        
        # 아군/적 리스트 추가 (위와 동일한 로직)
        if user_list:
            user_names = "\n".join([f"• {user}" for user in user_list])
            embed.add_field(name="참가 아군", value=user_names, inline=False)
        else:
            embed.add_field(name="참가 아군", value="참가자가 없습니다.", inline=False)
        
        if enemy_list:
            enemy_names = "\n".join([f"• {enemy}" for enemy in enemy_list])
            embed.add_field(name="적 목록", value=enemy_names, inline=False)
        else:
            embed.add_field(name="적 목록", value="적이 없습니다.", inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        # B그룹 턴 순서도 동일하게 처리
        order_embed = discord.Embed(
            title="순서 정하는 중...",
            description="잠시만 기다려줘, 쿠뽀뽀.",
            color=0x00ff00
        )
        order_message = await interaction.followup.send(embed=order_embed)
        
        await BattleSystem.battle_order_batch(self, "B")
        
        user_order = await Character._get_turn_order(self, "B", "user")
        enemy_order = await Character._get_turn_order(self, "B", "enemy")
        
        turn_embed = discord.Embed(
            title="🎲 B그룹 진행 순서",
            color=0xffd700
        )
        
        if user_order:
            user_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                       for i, (name, roll) in enumerate(user_order)])
            turn_embed.add_field(name="🛡️ 아군 행동 순서", value=user_turn_text, inline=True)
        
        if enemy_order:
            enemy_turn_text = "\n".join([f"{i+1}. {name} (주사위: {roll})" 
                                        for i, (name, roll) in enumerate(enemy_order)])
            turn_embed.add_field(name="⚔️ 적 행동 순서", value=enemy_turn_text, inline=True)
        
        turn_embed.add_field(name="📋 정말 시작!", value="이제 순서대로 `/행동`을 입력해서 전투를 시작해줘 쿠뽀!", inline=False)
        
        await order_message.edit(embed=turn_embed)
    else:
        await interaction.response.send_message(
            "미안하지만 그룹 이름이 잘못 입력된 것 같아, 쿠뽀. 다시 한 번 입력해줄래?\n"
            "A나 B, 혹은 boss를 입력하면 돼. 소문자로 입력해도 괜찮아.", 
            ephemeral=True
        )








@app_commands.command(name="행동", description="행동을 선택하세요.")
async def 행동(interaction: discord.Interaction):
    await interaction.response.send_message('네 차례야, 쿠뽀!', view=BattleInteraction())

@app_commands.command(name="코그출력", description="(관리자용 커맨드) 등록된 코그 목록을 출력합니다.")
async def 코그출력(interaction: discord.Interaction):
    await interaction.response.send_message(str(bot.cogs), ephemeral=True)




bot.run(test_token)