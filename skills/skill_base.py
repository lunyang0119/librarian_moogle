import random

class SkillBase:
    """
    스킬의 공통 로직을 정의하는 기본 클래스.
    """
    def __init__(self, name: str, description: str, max_uses: int = 1):
        """
        SkillBase 생성자.
        :param name: 스킬 이름
        :param description: 스킬 설명
        :param max_uses: 스킬 최대 사용 횟수
        """
        self.name = name
        self.description = description
        self.max_uses = max_uses
        self.used_count = 0

    def can_use(self, user):
        """
        스킬 사용 가능 여부를 확인합니다.
        :param user: 스킬 사용자
        :return: 사용 가능 여부 (bool)
        """
        return self.used_count < self.max_uses

    def apply_bonus(self, user, stat_keys):
        """
        사용자의 스탯 중 가장 높은 값을 보정치로 반환합니다.
        :param user: 스킬 사용자
        :param stat_keys: 보정치로 사용할 스탯 키 리스트
        :return: 보정치 값
        """
        return max(user.stats[key] for key in stat_keys)

    def use(self, user, targets, context):
        """
        스킬 사용 로직. 하위 클래스에서 구현해야 합니다.
        """
        raise NotImplementedError("스킬 사용 로직은 하위 클래스에서 구현해야 합니다.")

    def log_usage(self, user, result):
        """
        스킬 사용 로그를 생성합니다.
        :param user: 스킬 사용자
        :param result: 스킬 사용 결과
        :return: 로그 문자열
        """
        return f"[LOG] {user.name} used {self.name}: {result}"