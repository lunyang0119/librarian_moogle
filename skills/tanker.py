from skills.skill_base import SkillBase

class TankerSkill1(SkillBase):
    """
    탱커 스킬 1: 보호
    지정한 아군의 피해를 대신 받으며, 피해는 절반으로 감소합니다.
    """
    def __init__(self):
        super().__init__("보호", "지정한 아군의 피해를 대신 받으며, 피해는 절반으로 감소")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        context["guarding"] = {"tank": user.name, "target": target.name}
        result = f"{user.name}이(가) {target.name}을 보호합니다."
        return self.log_usage(user, result)


class TankerSkill2(SkillBase):
    """
    탱커 스킬 2: 도발
    적 전체를 도발하여 자신을 공격하도록 만듭니다.
    """
    def __init__(self):
        super().__init__("도발", "적 전체를 도발하여 자신을 공격하도록 만듭니다.")

    def use(self, user, targets, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        for target in targets:
            context["taunt"] = {"tank": user.name, "target": target.name}
        result = f"{user.name}이(가) 적 전체를 도발했습니다."
        return self.log_usage(user, result)


class TankerSkill3(SkillBase):
    """
    탱커 스킬 3: 철벽 방어
    자신에게 1턴 동안 받는 피해를 50% 감소시키는 버프를 부여합니다.
    """
    def __init__(self):
        super().__init__("철벽 방어", "자신에게 1턴 동안 받는 피해를 50% 감소시키는 버프를 부여합니다.")

    def use(self, user, target, context):
        if not self.can_use(user):
            return f"{self.name} 스킬은 이미 사용되었습니다."
        self.used_count += 1
        context["buff"] = {"target": user.name, "effect": "damage_reduction", "value": 50, "duration": 1}
        result = f"{user.name}이(가) 철벽 방어를 사용하여 받는 피해를 50% 감소시킵니다."
        return self.log_usage(user, result)
