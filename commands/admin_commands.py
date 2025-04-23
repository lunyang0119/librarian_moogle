import discord
from discord import app_commands
from discord.ext import commands
from engine.status_effects import StatusEffectManager
from dependencies import combat_session, sheet_user, material_sheet

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

class aclient(discord.Client):
    def __init__(self):
         super().__init__(intents = discord.Intents.all())
         self.synced = False
    async def on_ready(self):
         await self.wait_until_ready()
         if not self.synced: 
             await tree.sync() 
             self.synced = True

client = aclient()
tree = bot.tree

# 상태 이상 매니저 초기화
status_manager = StatusEffectManager()

class AdminCommands(commands.Cog):
    def __init__(self, bot, combat_session, sheet_user, material_sheet):
        self.bot = bot
        self.combat_session = combat_session
        self.sheet_user = sheet_user
        self.material_sheet = material_sheet

    @tree.command(name="set_hp", description="특정 캐릭터의 HP를 설정합니다.")
    async def set_hp(self, interaction: discord.Interaction, target_name: str, hp: int):
        target = self.find_combatant(target_name)
        if target:
            target.hp = max(0, hp)
            await interaction.response.send_message(f"{target.name}의 HP가 {hp}로 설정되었습니다.")
        else:
            await interaction.response.send_message(f"대상을 찾을 수 없습니다: {target_name}")

    @tree.command(name="apply_status", description="특정 캐릭터에게 상태 이상 효과를 적용합니다.")
    async def apply_status(self, interaction: discord.Interaction, target_name: str, status_name: str, duration: int, damage: int = 0):
        target = self.find_combatant(target_name)
        if target:
            status_manager.apply_effect(target, status_name, duration, {"damage": damage})
            await interaction.response.send_message(f"{target.name}에게 {status_name} 상태 이상이 {duration}턴 동안 적용되었습니다.")
        else:
            await interaction.response.send_message(f"대상을 찾을 수 없습니다: {target_name}")

    @tree.command(name="remove_status", description="특정 캐릭터의 상태 이상 효과를 제거합니다.")
    async def remove_status(self, interaction: discord.Interaction, target_name: str, status_name: str):
        target = self.find_combatant(target_name)
        if target:
            status_manager.remove_effect(target, status_name)
            await interaction.response.send_message(f"{target.name}의 {status_name} 상태 이상이 제거되었습니다.")
        else:
            await interaction.response.send_message(f"대상을 찾을 수 없습니다: {target_name}")

    @tree.command(name="reset_battle", description="전투를 초기화합니다.")
    async def reset_battle(self, interaction: discord.Interaction):
        self.combat_session.reset()
        await interaction.response.send_message("전투가 초기화되었습니다.")

    @tree.command(name="join_battle", description="새로운 캐릭터를 전투에 난입시킵니다.")
    async def join_battle(self, interaction: discord.Interaction, name: str, str_stat: int, agi_stat: int, hp: int, is_player: bool = True):
        combatant = Character(name, {"str": str_stat, "agi": agi_stat}, hp)
        self.combat_session.join_battle(combatant, is_player)
        await interaction.response.send_message(f"{name}이(가) 전투에 난입했습니다!")

    @tree.command(name="스탯등록", description="유저 스탯을 등록합니다.")
    async def 스탯등록(self, interaction: discord.Interaction, hp: int, atk: int, defense: int, job: str, lb: str):
        # 유저 스탯 등록 로직
        user_id = str(interaction.user.id)
        # 구글 시트에 데이터 저장 (예시)
        self.sheet_user.append_row([user_id, hp, atk, defense, job, lb])
        await interaction.response.send_message(f"{interaction.user.display_name}님의 스탯이 등록되었습니다!")

    @tree.command(name="스탯확인", description="자신의 스탯을 확인합니다.")
    async def 스탯확인(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        # 구글 시트에서 데이터 조회 (예시)
        user_data = self.sheet_user.find(user_id)
        if user_data:
            embed = discord.Embed(
                title=f"{interaction.user.display_name}님의 스탯",
                description=f"HP: {user_data['HP']}, ATK: {user_data['ATK']}, DEF: {user_data['DEF']}, 직업: {user_data['JOB']}, LB: {user_data['LB']}",
                colour=0x00FF00
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("등록된 스탯이 없습니다.", ephemeral=True)

    @tree.command(name="스탯업데이트", description="자신의 스탯을 업데이트합니다.")
    async def 스탯업데이트(self, interaction: discord.Interaction, hp: int, atk: int, defense: int, job: str, lb: str):
        user_id = str(interaction.user.id)
        # 구글 시트에서 데이터 업데이트 (예시)
        self.sheet_user.update_row(user_id, [hp, atk, defense, job, lb])
        await interaction.response.send_message(f"{interaction.user.display_name}님의 스탯이 업데이트되었습니다!")

    @tree.command(name="소재추가", description="새로운 소재를 추가합니다.")
    async def 소재추가(self, interaction: discord.Interaction, 소재이름: str):
        # 소재 추가 로직
        self.material_sheet.append_row([소재이름])
        await interaction.response.send_message(f"소재 '{소재이름}'이(가) 추가되었습니다!")

    @tree.command(name="소재리스트", description="등록된 소재 목록을 확인합니다.")
    async def 소재리스트(self, interaction: discord.Interaction):
        # 소재 목록 조회
        materials = self.material_sheet.get_all_records()
        material_names = [row["소재이름"] for row in materials]
        await interaction.response.send_message(f"등록된 소재: {', '.join(material_names)}")

    @tree.command(name="인벤토리", description="자신의 인벤토리를 확인합니다.")
    async def 인벤토리(self, interaction: discord.Interaction):
        # 인벤토리 조회 로직
        user_id = str(interaction.user.id)
        inventory = self.sheet_user.find(user_id)["인벤토리"]
        await interaction.response.send_message(f"{interaction.user.display_name}님의 인벤토리: {inventory}")

    @tree.command(name="도움말", description="전체 명령어 목록을 보여줍니다.")
    async def 도움말(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="**사용 가능한 명령어**",
            description=(
                "`/스탯등록`, `/스탯확인`, `/스탯업데이트`\n"
                "`/전투준비`, `/참가`, `/준비완료`, `/전투종료`\n"
                "`/소재추가`, `/소재리스트`, `/인벤토리`\n"
                "`/도움말`, `/전투도움말`, `/행동도움말`"
            ),
            colour=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

    def find_combatant(self, name):
        for combatant in self.combat_session.players + self.combat_session.monsters:
            if combatant.name == name:
                return combatant
        return None