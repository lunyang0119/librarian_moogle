# models/monster.py

from models.character import Character


class Monster(Character):
    def __init__(
        self,
        name: str,
        level: int,
        max_hp: int,
        current_hp: int,
        str_stat: int,
        dex_stat: int,
        int_stat: int,
        status_effects=None,
        is_active=True,
    ):
        super().__init__(name, level, max_hp, current_hp, str_stat, dex_stat, int_stat, status_effects, is_active)
        # 일반 몬스터는 별도의 필드 없음. 기본 캐릭터 정보만 사용함.
