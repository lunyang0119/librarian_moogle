from dataclasses import dataclass
from typing import Optional

@dataclass
class CharacterStats:
    str: int
    dex: int
    con: int
    int: int
    wis: int

@dataclass
class User:
    id: str
    name: str
    stats: CharacterStats
    job: str
    limit_break_title: str
    limit_break_desc: str
    coins: int
    inventory: str
    acted: bool = False
    used_skill1: bool = False
    used_skill2: bool = False
    hp: int = 0
    max_hp: int = 0

@dataclass
class Monster:
    id: str
    name: str
    stats: CharacterStats
    job: Optional[str]
    hp: int = 0
    max_hp: int = 0

@dataclass
class Boss:
    id: str
    name: str
    stats: CharacterStats
    job: Optional[str]
    special_effect: str
    used_special: bool
    hp: int
    max_hp: int
    phase2_effect: str
    phase2_multiplier: float
    phase3_effect: str
    phase3_multiplier: float
    phase2_quote: str
    phase3_quote: str
    death_quote: str
