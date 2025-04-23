from skills.skill_base import SkillBase
import random

class HealerSkill2(SkillBase):
    def __init__(self):
        super().__init__("단체치유", "모든 아군을 1d10 + 보정치 만큼 회복")

    def use(self, user, targets, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        bonus = self.apply_bonus(user, ["agi", "wis"])  # 민첩/지혜 중 높은 값
        heal_amount = random.randint(1, 10) + bonus
        for ally in targets:
            ally.hp = min(ally.max_hp, ally.hp + heal_amount)
        result = f"{user.name}이(가) 아군 전체를 {heal_amount}만큼 회복했습니다."
        return self.log_usage(user, result)