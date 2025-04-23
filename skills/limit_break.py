import random

def limit_break(user, allies, enemies, turn_tracker):
    """
    리미트 브레이크 스킬을 실행합니다.
    :param user: 스킬을 사용하는 캐릭터 (Character 객체)
    :param allies: 아군 리스트 (Character 객체 리스트)
    :param enemies: 적 리스트 (Character 객체 리스트)
    :param turn_tracker: 현재 턴 정보를 관리하는 객체
    :return: 스킬 실행 결과 로그
    """
    if user.limit_break_ready:
        # 리미트 브레이크 발동
        damage = user.stats["str"] * 2  # 예: 힘의 2배만큼 피해
        logs = []

        for enemy in enemies:
            enemy.hp = max(0, enemy.hp - damage)
            logs.append(f"{user.name}이(가) {enemy.name}에게 {damage}의 리미트 브레이크 피해를 입혔습니다.")

        # 리미트 브레이크 사용 후 초기화
        user.limit_break_ready = False
        user.limit_break_charge = 0

        # 턴 트래커에 리미트 브레이크 사용 로그 추가
        turn_tracker.add_log(f"{user.name}이(가) 리미트 브레이크를 발동했습니다!")
        turn_tracker.add_logs(logs)

        return logs
    else:
        return [f"{user.name}의 리미트 브레이크가 준비되지 않았습니다."]
