from skills.skill_base import SkillBase

class TankSkill1(SkillBase):
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