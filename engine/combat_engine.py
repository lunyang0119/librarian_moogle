import gspread
from oauth2client.service_account import ServiceAccountCredentials
from engine.status_effects import StatusEffectManager
from models.character import Character  # Character 클래스를 가져옴
from engine.combat_session import CombatSession
import random

class Boss(Character):
    def __init__(self, name, stats, hp, dialogue_80, dialogue_40, dialogue_0, skill_multiplier_80, skill_multiplier_40):
        super().__init__(name, stats, hp)
        self.dialogue_80 = dialogue_80
        self.dialogue_40 = dialogue_40
        self.dialogue_0 = dialogue_0
        self.skill_multiplier_80 = skill_multiplier_80
        self.skill_multiplier_40 = skill_multiplier_40
        self.used_80_percent_skill = False
        self.used_40_percent_skill = False

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

def load_boss_from_sheet(boss_sheet):
    """
    구글 시트에서 보스 데이터를 로드합니다.
    """
    boss_data = boss_sheet.get_all_records()[0]
    return Boss(
        name=boss_data["name"],
        stats={"str": boss_data["str"], "agi": boss_data["agi"]},
        hp=boss_data["hp"],
        dialogue_80=boss_data["dialogue_80"],
        dialogue_40=boss_data["dialogue_40"],
        dialogue_0=boss_data["dialogue_0"],
        skill_multiplier_80=boss_data["skill_multiplier_80"],
        skill_multiplier_40=boss_data["skill_multiplier_40"]
    )

# 상태 이상 매니저 초기화
status_manager = StatusEffectManager()

# 가상 플레이어와 몬스터 객체 생성 (예시)
players = [
    Character("Player1", {"str": 5, "agi": 10}, 50),  # Character 클래스를 사용
    Character("Player2", {"str": 7, "agi": 8}, 60),
]

monsters = [
    Character("Monster1", {"str": 6, "agi": 5}, 40),
    Character("Monster2", {"str": 8, "agi": 7}, 50),
]

# 전투 세션 초기화
combat_session = CombatSession(players, monsters)

def determine_turn_order(players, monsters):
    """
    유저와 몬스터에게 랜덤한 행동 순서를 부여하고 정렬합니다.
    :param players: 유저 리스트
    :param monsters: 몬스터 리스트
    :return: 행동 순서가 정렬된 리스트
    """
    all_combatants = players + monsters
    for combatant in all_combatants:
        combatant.turn_order = random.randint(1, 100)  # 랜덤한 번호 부여
    return sorted(all_combatants, key=lambda x: x.turn_order)

def process_boss_turn(boss, players):
    """
    보스의 행동을 처리합니다.
    :param boss: 보스 객체
    :param players: 플레이어 리스트
    """
    if boss.hp <= boss.max_hp * 0.4 and not boss.used_40_percent_skill:
        # 40% 이하일 때 특수 스킬 사용
        print(f"보스 대사: {boss.dialogue_40}")
        damage = boss.stats["str"] * boss.skill_multiplier_40
        target = random.choice(players)
        target.hp = max(0, target.hp - damage)
        print(f"{boss.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
        boss.used_40_percent_skill = True
    elif boss.hp <= boss.max_hp * 0.8 and not boss.used_80_percent_skill:
        # 80% 이하일 때 특수 스킬 사용
        print(f"보스 대사: {boss.dialogue_80}")
        damage = boss.stats["str"] * boss.skill_multiplier_80
        target = random.choice(players)
        target.hp = max(0, target.hp - damage)
        print(f"{boss.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
        boss.used_80_percent_skill = True
    else:
        # 일반 공격
        target = random.choice(players)
        damage = boss.stats["str"] + random.randint(1, 20)
        target.hp = max(0, target.hp - damage)
        print(f"{boss.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")

def select_target(targets):
    """
    대상 리스트에서 유저가 대상을 선택합니다.
    """
    print("대상 목록:")
    for idx, target in enumerate(targets):
        print(f"{idx + 1}. {target.name} (HP: {target.hp})")

    while True:
        try:
            choice = int(input("대상의 번호를 입력하세요: ")) - 1
            if 0 <= choice < len(targets):
                return targets[choice]
            else:
                print("잘못된 번호입니다. 다시 입력하세요.")
        except ValueError:
            print("숫자를 입력하세요.")

def process_turn(combatant, players, monsters):
    """
    현재 차례의 캐릭터가 행동을 수행합니다.
    :param combatant: 현재 차례의 캐릭터
    :param players: 유저 리스트
    :param monsters: 몬스터 리스트
    """
    if combatant.hp <= 0:
        print(f"{combatant.name}은(는) 행동 불능 상태입니다.")
        return

    if combatant.is_player:
        print(f"{combatant.name}의 차례입니다.")
        action = input("행동을 선택하세요 (공격/스킬/퇴각): ").strip().lower()

        if action == "공격":
            target = select_target(monsters)
            if target:
                damage = combatant.stats["str"] + random.randint(1, 20)
                target.hp = max(0, target.hp - damage)
                print(f"{combatant.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
        elif action == "스킬":
            print(f"{combatant.name}이(가) 스킬을 사용했습니다.")
        elif action == "퇴각":
            print(f"{combatant.name}이(가) 퇴각했습니다.")
        else:
            print("잘못된 입력입니다. 행동을 건너뜁니다.")
    else:
        print(f"{combatant.name} (몬스터)의 차례입니다.")
        target = random.choice(players)
        damage = combatant.stats["str"] + random.randint(1, 10)
        target.hp = max(0, target.hp - damage)
        print(f"{combatant.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")

# 전투 진행
if __name__ == "__main__":
    client = authorize_gsheets()
    user_sheet, monster_sheet, boss_sheet = get_sheets(client)
    print("시트 연동 완료")

    # 보스 데이터 로드
    boss = load_boss_from_sheet(boss_sheet)

    # 행동 순서 결정
    turn_order = determine_turn_order(players, monsters)

    # 보스전 진행
    print(f"보스 {boss.name}와의 전투가 시작되었습니다!")
    while combat_session.is_battle_active():
        for combatant in turn_order:
            if combatant.hp <= 0:
                continue  # 행동 불능 상태
            if combatant.is_player:
                print(f"{combatant.name}의 차례입니다.")
                action = input("행동을 선택하세요 (공격/스킬/퇴각): ").strip()
                if action == "공격":
                    target = boss  # 보스를 공격
                    damage = combatant.stats["str"] + random.randint(1, 20)
                    target.hp = max(0, target.hp - damage)
                    print(f"{combatant.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
                elif action == "스킬":
                    print(f"{combatant.name}이(가) 스킬을 사용했습니다.")
                elif action == "퇴각":
                    print(f"{combatant.name}이(가) 퇴각했습니다.")
            else:
                process_boss_turn(boss, players)

        # 전투 종료 조건 확인
        if all(player.hp <= 0 for player in players):
            print("보스가 승리했습니다!")
            break
        if boss.hp <= 0:
            print(f"{boss.name}이(가) 쓰러졌습니다. 보스 대사: {boss.dialogue_0}")
            print("플레이어가 승리했습니다!")
            break