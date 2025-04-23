# models/player.py

from models.character import Character


class Player(Character):
    def __init__(
        self,
        name: str,
        level: int,
        max_hp: int,
        current_hp: int,
        str_stat: int,
        dex_stat: int,
        int_stat: int,
        job: str,
        status_effects=None,
        is_active=True,
    ):
        super().__init__(name, level, max_hp, current_hp, str_stat, dex_stat, int_stat, status_effects, is_active)
        self.job = job
        self.used_skill1 = False
        self.used_skill2 = False
        self.used_limit_break = False
        self.joined_late = False  # 전투 난입 여부
        self.retreat = False      # 퇴각 여부
