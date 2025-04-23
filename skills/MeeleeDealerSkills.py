# skills/melee_dealer_skills.py

import random
from skills.skill_base import SkillBase

class MeleeDealerSkills(SkillBase):
    def __init__(self, user):
        super().__init__(user)

    def skill1(self, target):
        """
        스킬1: 적 하나에게 1d20 + 근력 + 1d10 만큼의 피해
        """
        if self.used_skills["skill1"]:
            return f"{self.user.name}은(는) 이미 스킬1을 사용했습니다."

        damage = random.randint(1, 20) + self.user.stats.get("str", 0) + random.randint(1, 10)
        target.hp = max(0, target.hp - damage)
        self.used_skills["skill1"] = True
        return f"{self.user.name}의 스킬1 공격! {target.name}에게 {damage}의 피해를 입혔습니다."

    def skill2(self, target):
        """
        스킬2: 적 하나에게 1d20 + 근력 + 1d20 만큼의 피해
        """
        if self.used_skills["skill2"]:
            return f"{self.user.name}은(는) 이미 스킬2를 사용했습니다."

        damage = random.randint(1, 20) + self.user.stats.get("str", 0) + random.randint(1, 20)
        target.hp = max(0, target.hp - damage)
        self.used_skills["skill2"] = True
        return f"{self.user.name}의 스킬2 공격! {target.name}에게 {damage}의 피해를 입혔습니다."
