import random

class Skill:
    def __init__(self, name: str, description: str, max_uses: int = 1):
        self.name = name
        self.description = description
        self.used_count = 0
        self.max_uses = max_uses

    def can_use(self, user):
        """스킬 사용 가능 여부 확인"""
        return self.used_count < self.max_uses

    def apply_bonus(self, user, stat_keys):
        """사용자의 스탯 중 가장 높은 값을 보정치로 반환"""
        return max(user.stats[key] for key in stat_keys)

    def use(self, user, targets, context):
        """스킬 사용 로직 (하위 클래스에서 구현)"""
        raise NotImplementedError("스킬 사용 로직은 하위 클래스에서 구현해야 합니다.")

    def log_usage(self, user, result):
        """스킬 사용 로그 기록"""
        return f"[LOG] {user.name} used {self.name}: {result}"


# 탱커 스킬 1: 보호
class TankSkill1(Skill):
    def __init__(self):
        super().__init__("보호", "지정한 아군의 피해를 대신 받으며, 피해는 절반으로 감소")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        context["guarding"] = {"tank": user.name, "target": target.name}
        result = f"{user.name}이(가) {target.name}을 보호합니다."
        return self.log_usage(user, result)


# 힐러 스킬 2: 단체 치유
class HealerSkill2(Skill):
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


# 근딜 스킬 1: 강력한 일격
class MeleeSkill1(Skill):
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


# 원딜 스킬 1: 전방 사격
class RangedSkill1(Skill):
    def __init__(self):
        super().__init__("전방 사격", "적 하나에게 1d20 + 민첩 + 2 만큼의 피해를 줍니다.")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        bonus = user.stats["agi"]  # 민첩 보정치
        damage = random.randint(1, 20) + bonus + 2
        target.hp = max(0, target.hp - damage)
        result = f"{user.name}이(가) {target.name}에게 {damage}의 피해를 입혔습니다."
        return self.log_usage(user, result)


# 직업별 스킬 매핑 함수
def get_skills_by_job(job_name):
    skill_mapping = {
        "탱커": [TankSkill1()],
        "힐러": [HealerSkill2()],
        "근딜(물리)": [MeleeSkill1()],
        "원딜(물리)": [RangedSkill1()],
        # 다른 직업 스킬 추가 가능
    }
    return skill_mapping.get(job_name, [])
