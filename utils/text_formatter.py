# utils/text_formatter.py

from typing import List
from models.character import Character

def format_hp_bar(current: int, maximum: int, length: int = 20) -> str:
    """
    텍스트 기반 HP 바 출력.
    ▮ : 현재 HP
    ▯ : 잃은 HP
    """
    filled_len = int((current / maximum) * length)
    empty_len = length - filled_len
    bar = "▮" * filled_len + "▯" * empty_len
    return f"[{bar}] {current}/{maximum}"

def format_status_effects(effects: List[str]) -> str:
    """
    상태이상 리스트를 문자열로 변환
    """
    if not effects:
        return "이상 없음"
    return ", ".join(effects)

def format_character_status(character: Character) -> str:
    """
    캐릭터의 현재 상태를 문자열로 출력
    """
    hp_bar = format_hp_bar(character.current_hp, character.max_hp)
    status = format_status_effects(character.status_effects)
    return (
        f"**{character.name}**\n"
        f"직업: {character.job} | 레벨: {character.level}\n"
        f"HP: {hp_bar}\n"
        f"상태이상: {status}\n"
    )
