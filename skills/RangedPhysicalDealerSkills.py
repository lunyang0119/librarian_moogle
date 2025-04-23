# skills/ranged_physical_dealer_skills.py

import random
from skills.skill_base import SkillBase

class RangedPhysicalDealerSkills(SkillBase):
    def __init__(self, user):
        super().__init__(user)

    def skill1(self, enemies):
        """
        스킬1: 전체 적에게 출혈 상태 부여
        """
        if self.used_skills["skill1"]:
            return f"{self.user.name}은(는) 이미 스킬1을 사용했습니다."

        for enemy in enemies:
            enemy.status_effects["출혈"] = {
                "turns_left": 5,
                "start_next_turn": True
            }
        self.used_skills["skill1"] = True
        return f"{self.user.name}이(가) 전체 적에게 출혈 상태를 부여했습니다!"

    def skill2(self, enemies):
        """
        스킬2: 전체 적에게 1d20 + 민첩 - 1d5 만큼의 피해
        """
        if self.used_skills["skill2"]:
            return f"{self.user.name}은(는) 이미 스킬2를 사용했습니다."

        agi = self.user.stats.get("agi", 0)
        result_texts = []
        for enemy in enemies:
            damage = random.randint(1, 20) + agi - random.randint(1, 5)
            damage = max(0, damage)
            enemy.hp = max(0, enemy.hp - damage)
            result_texts.append(f"{enemy.name}에게 {damage}의 피해")

        self.used_skills["skill2"] = True
        return f"{self.user.name}의 스킬2 공격!\n" + "\n".join(result_texts)
