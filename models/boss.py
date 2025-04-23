from models.monster import Monster

class Boss(Monster):
    def __init__(
        self,
        monster_id,
        name,
        strength,
        dexterity,
        constitution,
        intelligence,
        wisdom,
        job,
        special_skill_type,
        special_skill_used=False,
        hp_80_skill_type=None,
        hp_80_multiplier=1.0,
        hp_40_skill_type=None,
        hp_40_multiplier=1.0,
        hp_80_dialogue="",
        hp_40_dialogue="",
        death_dialogue=""
    ):
        super().__init__(monster_id, name, strength, dexterity, constitution, intelligence, wisdom, job)
        self.special_skill_type = special_skill_type
        self.special_skill_used = special_skill_used

        self.hp_80_skill_type = hp_80_skill_type
        self.hp_80_multiplier = hp_80_multiplier
        self.hp_40_skill_type = hp_40_skill_type
        self.hp_40_multiplier = hp_40_multiplier

        self.hp_80_dialogue = hp_80_dialogue
        self.hp_40_dialogue = hp_40_dialogue
        self.death_dialogue = death_dialogue

        self.used_80_skill = False
        self.used_40_skill = False

    def check_special_phases(self):
        """보스 체력에 따라 스킬이나 대사 발동"""
        hp_ratio = self.current_hp / self.max_hp

        events = []
        if not self.used_80_skill and hp_ratio <= 0.8:
            events.append(("80", self.hp_80_skill_type, self.hp_80_multiplier, self.hp_80_dialogue))
            self.used_80_skill = True

        if not self.used_40_skill and hp_ratio <= 0.4:
            events.append(("40", self.hp_40_skill_type, self.hp_40_multiplier, self.hp_40_dialogue))
            self.used_40_skill = True

        if self.current_hp <= 0:
            events.append(("0", None, None, self.death_dialogue))

        return events
