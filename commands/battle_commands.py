import discord
from discord.ext import commands
# from discord import tree
from engine.combat_engine import determine_turn_order, process_turn, process_boss_turn
from dependencies import combat_session, sheet_user, material_sheet, boss
import random

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

class BattleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.combat_session = combat_session
        self.boss = boss
        self.turn_order = []

    @tree.command(name="행동", description="행동을 선택하고 대상을 지정합니다.")
    async def 행동(self, interaction: discord.Interaction):
        if not self.turn_order:
            await interaction.response.send_message("턴 순서가 비어 있습니다.", ephemeral=True)
            return
        current_combatant = self.turn_order[0]
        if current_combatant.name != interaction.user.name:
            await interaction.response.send_message("행동할 차례가 아닙니다.", ephemeral=True)
            return

        view = ActionSelectionView(self.combat_session, self.boss, self.turn_order)
        await interaction.response.send_message(f"{current_combatant.name}의 행동을 선택하세요:", view=view)

    @tree.command(name="보스전", description="보스전을 시작합니다.")
    async def 보스전(self, interaction: discord.Interaction):
        if not self.boss:
            await interaction.response.send_message("보스가 설정되지 않았습니다.", ephemeral=True)
            return
        self.turn_order = determine_turn_order(self.combat_session.players, [self.boss])
        await interaction.response.send_message("보스전이 시작되었습니다! 행동 순서가 결정되었습니다.")

    @tree.command(name="턴진행", description="현재 턴을 진행합니다.")
    async def 턴진행(self, interaction: discord.Interaction):
        if not self.turn_order:
            await interaction.response.send_message("행동 순서가 아직 결정되지 않았습니다. `/보스전` 명령어를 사용하세요.", ephemeral=True)
            return

        current_combatant = self.turn_order.pop(0)
        if current_combatant.hp <= 0:
            await interaction.response.send_message(f"{current_combatant.name}은(는) 행동 불능 상태입니다.", ephemeral=True)
            return

        if current_combatant.is_player:
            await interaction.response.send_message(f"{current_combatant.name}의 차례입니다. `/행동` 명령어를 사용하세요.")
        else:
            process_boss_turn(self.boss, self.combat_session.players)
            if self.turn_order:
                self.turn_order.append(current_combatant)
            await interaction.response.send_message(f"{current_combatant.name}이(가) 행동을 완료했습니다.")

class ActionSelectionView(discord.ui.View):
    def __init__(self, combat_session, boss, turn_order):
        super().__init__()
        self.combat_session = combat_session
        self.boss = boss
        self.turn_order = turn_order

    def sync_state(self):
        """
        combat_session과 boss의 상태를 동기화합니다.
        """
        # 예: 보스의 HP가 0 이하일 경우 전투 종료
        if self.boss.hp <= 0:
            self.turn_order.clear()

    @discord.ui.button(label="공격", style=discord.ButtonStyle.red)
    async def attack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.turn_order:
            await interaction.response.send_message("턴 순서가 비어 있습니다.", ephemeral=True)
            return
        current_combatant = self.turn_order[0]
        target = self.boss
        damage = self.turn_order[0].stats["str"] + random.randint(1, 20)
        target.hp = max(0, target.hp - damage)
        await interaction.response.send_message(f"{self.turn_order[0].name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
        if self.turn_order:
            self.turn_order.append(self.turn_order.pop(0))

    @discord.ui.button(label="스킬1", style=discord.ButtonStyle.green)
    async def skill1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.turn_order:
            await interaction.response.send_message("턴 순서가 비어 있습니다.", ephemeral=True)
            return
        current_combatant = self.turn_order[0]
        await interaction.response.send_message(f"{self.turn_order[0].name}이(가) 스킬1을 사용했습니다.")
        if self.turn_order:
            self.turn_order.append(self.turn_order.pop(0))

    @discord.ui.button(label="퇴각", style=discord.ButtonStyle.gray)
    async def retreat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.turn_order:
            await interaction.response.send_message("턴 순서가 비어 있습니다.", ephemeral=True)
            return
        current_combatant = self.turn_order[0]
        await interaction.response.send_message(f"{self.turn_order[0].name}이(가) 퇴각했습니다.")
        if self.turn_order:
            self.turn_order.append(self.turn_order.pop(0))