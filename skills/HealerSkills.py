# skills/healer_skills.py

import random
from skills.skill_base import SkillBase

class HealerSkills(SkillBase):
    def __init__(self, user):
        super().__init__(user)

    def skill1(self, target):
        """
        스킬1: 지정 대상을 최대 HP까지 회복
        """
        if self.used_skills["skill1"]:
            return f"{self.user.name}은(는) 이미 스킬1을 사용했습니다."

        heal_amount = target.max_hp - target.hp
        target.hp = target.max_hp
        self.used_skills["skill1"] = True
        return f"{self.user.name}이(가) {target.name}을(를) 최대 체력까지 회복시켰습니다! (+{heal_amount} HP)"

    def skill2(self, allies):
        """
        스킬2: 아군 전체 회복 (1d10 + 민첩 or 지혜 중 높은 보정치)
        """
        if self.used_skills["skill2"]:
            return f"{self.user.name}은(는) 이미 스킬2를 사용했습니다."

        stat_bonus = max(self.user.stats.get("agi", 0), self.user.stats.get("wis", 0))
        heal_value = random.randint(1, 10) + stat_bonus

        results = []
        for ally in allies:
            before = ally.hp
            ally.hp = min(ally.max_hp, ally.hp + heal_value)
            healed = ally.hp - before
            results.append(f"{ally.name}: +{healed} HP")

        self.used_skills["skill2"] = True
        result_msg = "\n".join(results)
        return f"{self.user.name}이(가) 아군 전체를 회복시켰습니다! (+{heal_value} HP)\n{result_msg}"
