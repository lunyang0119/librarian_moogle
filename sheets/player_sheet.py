# sheets/player_sheet.py

import gspread
from typing import List
from models.player import Player
from config import SHEET_KEY

gc = gspread.service_account(filename="service_account.json")
spreadsheet = gc.open_by_key(SHEET_KEY)

def load_players() -> List[Player]:
    worksheet = spreadsheet.worksheet("Players")
    data = worksheet.get_all_records()

    players = []
    for row in data:
        player = Player(
            name=row["이름"],
            job=row["직업"],
            level=int(row["레벨"]),
            max_hp=int(row["최대 HP"]),
            current_hp=int(row["현재 HP"]),
            str_stat=int(row["STR"]),
            dex_stat=int(row["DEX"]),
            int_stat=int(row["INT"]),
            weapon=row["무기"],
            skill1_used=False,
            skill2_used=False,
            limit_break_used=False,
            status_effects=[],
            is_active=True,
        )
        players.append(player)

    return players
