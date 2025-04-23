from skills.skill_base import SkillBase
import random

class MeleeSkill1(SkillBase):
    """
    근딜 스킬 1: 강력한 일격
    적 하나에게 1d20 + 근력 + 1d10 만큼의 피해를 줍니다.
    """
    def __init__(self):
        super().__init__("강력한 일격", "적 하나에게 1d20 + 근력 + 1d10 만큼의 피해를 줍니다.")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        bonus = user.stats["str"]  # 근력 보정치
        damage = random.randint(1, 20) + bonus + random.randint(1, 10)
        target.hp = max(0, target.hp - damage)
        result = f"{user.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다."
        return self.log_usage(user, result)


class MeleeSkill2(SkillBase):
    """
    근딜 스킬 2: 연속 공격
    적 하나에게 2번 공격을 가하며, 각각 1d10 + 근력의 피해를 줍니다.
    """
    def __init__(self):
        super().__init__("연속 공격", "적 하나에게 2번 공격을 가하며, 각각 1d10 + 근력의 피해를 줍니다.")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        bonus = user.stats["str"]  # 근력 보정치
        total_damage = 0
        logs = []
        for _ in range(2):  # 2번 공격
            damage = random.randint(1, 10) + bonus
            target.hp = max(0, target.hp - damage)
            total_damage += damage
            logs.append(f"{user.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다.")
        result = " ".join(logs)
        return self.log_usage(user, result)


class MeleeSkill3(SkillBase):
    """
    근딜 스킬 3: 방어 관통
    적 하나에게 1d20 + 근력의 피해를 주며, 방어력을 무시합니다.
    """
    def __init__(self):
        super().__init__("방어 관통", "적 하나에게 1d20 + 근력의 피해를 주며, 방어력을 무시합니다.")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        bonus = user.stats["str"]  # 근력 보정치
        damage = random.randint(1, 20) + bonus
        target.hp = max(0, target.hp - damage)
        result = f"{user.name}이(가) {target.name}에게 방어를 무시하고 {damage}의 피해를 입혔습니다."
        return self.log_usage(user, result)