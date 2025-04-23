import random  # random 모듈 추가

class StatusEffectManager:
    """
    상태 이상 효과를 관리하는 클래스.
    """

    def __init__(self):
        """
        상태 이상 효과 초기화.
        """
        self.effects = {}  # 대상별 상태 이상 효과 저장

    def apply_effect(self, target, effect_name, duration, extra_data=None):
        """
        대상에게 상태 이상 효과를 적용합니다.
        :param target: 상태 이상 효과를 받을 대상
        :param effect_name: 상태 이상 이름 (예: "출혈", "마비")
        :param duration: 상태 이상 지속 턴 수
        :param extra_data: 추가 데이터 (예: 피해량, 확률 등)
        """
        if target not in self.effects:
            self.effects[target] = {}
        self.effects[target][effect_name] = {
            "duration": duration,
            "extra_data": extra_data,
        }

    def remove_effect(self, target, effect_name):
        """
        대상의 특정 상태 이상 효과를 제거합니다.
        """
        if target in self.effects and effect_name in self.effects[target]:
            del self.effects[target][effect_name]

    def process_effects(self, target):
        """
        대상의 모든 상태 이상 효과를 처리합니다.
        :param target: 상태 이상 효과를 받을 대상
        :return: 처리된 상태 이상 효과 로그
        """
        if target not in self.effects:
            return []

        logs = []
        for effect_name, data in list(self.effects[target].items()):
            # 상태 이상 효과 처리
            if effect_name == "출혈":
                damage = data["extra_data"]["damage"]
                target.hp = max(0, target.hp - damage)
                logs.append(f"{target.name}이(가) 출혈로 {damage} 피해를 입었습니다.")
            elif effect_name == "마비":
                if random.random() < 0.5:  # 50% 확률로 행동 불가
                    logs.append(f"{target.name}이(가) 마비로 행동할 수 없습니다.")
                    continue

            # 지속 시간 감소
            data["duration"] -= 1
            if data["duration"] <= 0:
                logs.append(f"{target.name}의 {effect_name} 상태가 해제되었습니다.")
                del self.effects[target][effect_name]

        # 대상의 상태 이상 효과가 모두 제거되면, 대상 자체를 삭제
        if not self.effects[target]:
            del self.effects[target]

        return logs