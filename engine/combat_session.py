import random
from engine.status_effects import StatusEffectManager

class Combatant:
    """
    전투에 참여하는 캐릭터를 나타내는 클래스.
    """
    def __init__(self, name, stats, hp):
        self.name = name
        self.stats = stats
        self.hp = hp
        self.max_hp = hp

class CombatSession:
    """
    전투의 전체 흐름을 관리하는 클래스.
    """

    def __init__(self, players, monsters):
        """
        CombatSession 생성자.
        :param players: 플레이어 리스트
        :param monsters: 몬스터 리스트
        """
        self.players = players
        self.monsters = monsters
        self.turn_order = self.determine_turn_order()
        self.current_turn = 0
        self.status_manager = StatusEffectManager()  # 상태 이상 매니저 추가
        self.logs = []

    def determine_turn_order(self):
        """
        턴 순서를 결정합니다. (속도 기반 정렬)
        :return: 정렬된 턴 순서 리스트
        """
        all_combatants = self.players + self.monsters
        return sorted(all_combatants, key=lambda x: x.stats["agi"], reverse=True)

    def join_battle(self, combatant, is_player=True):
        """
        새로운 플레이어나 몬스터가 전투에 난입합니다.
        """
        if not isinstance(combatant, Combatant):
            raise ValueError("combatant는 Combatant 클래스의 인스턴스여야 합니다.")
        if is_player:
            self.players.append(combatant)
        else:
            self.monsters.append(combatant)
        self.turn_order = self.determine_turn_order()
        self.logs.append(f"{combatant.name}이(가) 전투에 난입했습니다!")

    def process_turn(self):
        """
        현재 턴의 행동을 처리합니다.
        """
        actor = self.turn_order[self.current_turn]
        if actor.hp <= 0:
            self.logs.append(f"{actor.name}은(는) 행동 불능 상태입니다.")
            return

        if actor in self.players:
            action_log = self.player_action(actor)
        else:
            action_log = self.monster_action(actor)
        self.logs.append(action_log)

        self.current_turn = (self.current_turn + 1) % len(self.turn_order)

    def player_action(self, player):
        """
        플레이어의 행동 처리
        """
        # 예시: 기본 공격
        if self.monsters:
            target = self.monsters[0]  # 첫 번째 몬스터를 타겟으로 설정
            damage = player.stats["str"] + 5  # 간단한 데미지 계산
            target.hp = max(0, target.hp - damage)
            return f"{player.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다."
        return f"{player.name}이(가) 공격할 대상이 없습니다."

    def monster_action(self, monster):
        """
        몬스터의 행동 처리
        """
        # 예시: 기본 공격
        if self.players:
            target = self.players[0]  # 첫 번째 플레이어를 타겟으로 설정
            damage = monster.stats["str"] + 3  # 간단한 데미지 계산
            target.hp = max(0, target.hp - damage)
            return f"{monster.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다."
        return f"{monster.name}이(가) 공격할 대상이 없습니다."

    def is_battle_active(self):
        """
        전투가 진행 중인지 확인합니다.
        :return: 전투 진행 여부 (bool)
        """
        players_alive = any(player.hp > 0 for player in self.players)
        monsters_alive = any(monster.hp > 0 for monster in self.monsters)
        return players_alive and monsters_alive

    def get_logs(self):
        """
        현재까지의 전투 로그를 반환합니다.
        :return: 전투 로그 문자열
        """
        return "\n".join(self.logs)