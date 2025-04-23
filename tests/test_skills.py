import unittest
from skills.tank_skills import TankSkill1
from skills.healer_skills import HealerSkill2
from skills.melee_skills import MeleeSkill1

class MockCombatant:
    def __init__(self, name, stats, hp, max_hp):
        self.name = name
        self.stats = stats
        self.hp = hp
        self.max_hp = max_hp

class TestSkills(unittest.TestCase):
    def test_tank_skill(self):
        tank = MockCombatant("Tank", {"str": 5, "agi": 3}, 50, 50)
        ally = MockCombatant("Ally", {"str": 3, "agi": 2}, 40, 40)
        skill = TankSkill1()
        result = skill.use(tank, ally, {})
        self.assertIn("보호합니다", result)

    def test_healer_skill(self):
        healer = MockCombatant("Healer", {"agi": 5, "wis": 8}, 50, 50)
        ally = MockCombatant("Ally", {"str": 3, "agi": 2}, 30, 50)
        skill = HealerSkill2()
        result = skill.use(healer, [ally], {})
        self.assertIn("회복했습니다", result)
        self.assertGreaterEqual(ally.hp, 30)

    def test_melee_skill(self):
        melee = MockCombatant("Melee", {"str": 10, "agi": 5}, 50, 50)
        target = MockCombatant("Target", {"str": 3, "agi": 2}, 40, 40)
        skill = MeleeSkill1()
        result = skill.use(melee, target, {})
        self.assertIn("피해를 입혔습니다", result)
        self.assertLessEqual(target.hp, 40)

if __name__ == "__main__":
    unittest.main()