# utils/dice.py

import random
import re

def roll_dice(expression: str) -> (int, str):
    """
    주사위 굴림 표현식을 처리합니다.
    :param expression: 주사위 표현식 (예: "2d6+3", "1d20-2")
    :return: (결과 값, 로그 문자열)
    """
    # 정규식으로 주사위 표현식 파싱 (예: "2d6+3")
    match = re.match(r"(\d*)d(\d+)([+-]\d+)?", expression)
    if not match:
        raise ValueError(f"Invalid dice expression: {expression}")

    # 파싱된 값 추출
    num_dice = int(match.group(1)) if match.group(1) else 1  # 주사위 개수 (기본값: 1)
    dice_sides = int(match.group(2))  # 주사위 면 수
    modifier = int(match.group(3)) if match.group(3) else 0  # 수정값 (기본값: 0)

    # 주사위 굴림
    rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    # 로그 생성
    rolls_str = " + ".join(map(str, rolls))
    log = f"({rolls_str}) {'+' if modifier >= 0 else ''}{modifier} = {total}"

    return total, log

def roll_dice_expression(expression: str) -> (int, str):
    return roll_dice(expression)

def roll_fixed(dice: int, sides: int, modifier: int = 0) -> Tuple[int, str]:
    """
    숫자 기반 주사위 굴림. 예: roll_fixed(2, 6, +3)
    """
    rolls = [random.randint(1, sides) for _ in range(dice)]
    total = sum(rolls) + modifier
    breakdown = f"{' + '.join(map(str, rolls))}"
    if modifier:
        breakdown += f" {'+' if modifier > 0 else '-'} {abs(modifier)}"

    log = f"({dice}d{sides}{'+' if modifier > 0 else ''}{modifier}) → {breakdown} = **{total}**"
    return total, log

def roll_d20() -> Tuple[int, str]:
    """
    기본 D20 굴림
    """
    value = random.randint(1, 20)
    return value, f"(1d20) → **{value}**"
