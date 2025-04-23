import random
import math

def roll_dice(num: int, sides: int) -> int:
    """num d sides 형태의 주사위 굴림"""
    return sum(random.randint(1, sides) for _ in range(num))

def get_stat_modifier(stat: int) -> int:
    """스탯 보정치 계산 (기본적으로 D&D 방식: (stat - 10) // 2)"""
    return (stat - 10) // 2

def clamp(value: int, min_value: int, max_value: int) -> int:
    """값이 특정 범위 내로 유지되도록 고정"""
    return max(min_value, min(value, max_value))
