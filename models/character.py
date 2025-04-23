# models/character.py

class Character:
    """
    전투에 참여하는 캐릭터(플레이어 또는 몬스터)를 나타내는 클래스.
    """

    def __init__(self, name, stats, hp):
        self.name = name
        self.stats = stats
        self.hp = hp
        self.max_hp = hp
        self.limit_break_ready = False
        self.limit_break_charge = 0

    def charge_limit_break(self, amount):
        """
        리미트 브레이크 게이지를 충전합니다.
        :param amount: 충전량
        """
        self.limit_break_charge += amount
        if self.limit_break_charge >= 100:
            self.limit_break_ready = True
            self.limit_break_charge = 100
