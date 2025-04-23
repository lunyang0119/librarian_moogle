# skills/ranged_magic_dealer_skills.py

import random
from skills.skill_base import SkillBase

class RangedMagicDealerSkills(SkillBase):
    def __init__(self, user):
        super().__init__(user)
        self.skill2_pending = False  # 스킬2가 다음 턴에 데미지를 입히도록 대기 상태

    def skill1(self, enemies):
        """
        스킬1: 전체 적에게 마비 상태 부여
        """
        if self.used_skills["skill1"]:
            return f"{self.user.name}은(는) 이미 스킬1을 사용했습니다."

        for enemy in enemies:
            enemy.status_effects["마비"] = {
                "turns_left": 3,
                "start_next_turn": True,
                "chance": 0.5
            }
        self.used_skills["skill1"] = True
        return f"{self.user.name}이(가) 전체 적에게 마비 상태를 부여했습니다!"

    def skill2(self, enemies):
        """
        스킬2: 적 하나에게 1d20 + 스탯보정치 + 1d25 피해
        - 캐스팅 턴 이후 다음 턴에 발동
        - 캐스팅 턴과 그 다음 턴 동안 행동 불가
        """
        if self.used_skills["skill2"]:
            return f"{self.user.name}은(는) 이미 스킬2를 사용했습니다."

        if self.skill2_pending:
            return f"{self.user.name}의 스킬2는 이미 시전 중입니다."

        self.used_skills["skill2"] = True
        self.skill2_pending = True
        self.user.action_disabled_turns = 2  # 이번 턴 + 다음 턴
        return f"{self.user.name}이(가) 마법 스킬2를 시전합니다! 다음 턴에 공격이 발동됩니다."

    def resolve_skill2(self, target):
        """
        스킬2의 다음 턴에 실행될 데미지 계산
        """
        if not self.skill2_pending:
            return None

        stat_bonus = max(self.user.stats.get("agi", 0), self.user.stats.get("wis", 0))
        damage = random.randint(1, 20) + stat_bonus + random.randint(1, 25)
        target.hp = max(0, target.hp - damage)
        self.skill2_pending = False
        return f"{self.user.name}의 스킬2가 {target.name}에게 적중! {damage}의 피해를 입혔습니다."
