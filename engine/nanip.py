# battle/nanip.py

class BattleJoinRequest:
    def __init__(self):
        self.pending_users = set()  # 다음 턴에 투입될 유저 이름 저장

    def request_join(self, user_name):
        if user_name in self.pending_users:
            return f"{user_name}님은 이미 전투 난입을 요청했습니다."
        self.pending_users.add(user_name)
        return f"{user_name}님이 전투에 난입을 요청했습니다. 다음 턴부터 참여합니다."

    def process_joins(self, all_users, active_users):
        joined = []
        for user in list(self.pending_users):
            if user not in active_users and user in all_users:
                active_users.append(user)
                joined.append(user)
                self.pending_users.remove(user)
        return joined
