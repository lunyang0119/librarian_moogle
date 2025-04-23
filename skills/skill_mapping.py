import json
from skills.tank_skills import TankSkill1
from skills.healer_skills import HealerSkill2
from skills.melee_skills import MeleeSkill1

# 직업별 스킬 클래스 매핑
SKILL_CLASSES = {
    "TankSkill1": TankSkill1,
    "HealerSkill2": HealerSkill2,
    "MeleeSkill1": MeleeSkill1
}

def get_skills_by_job(job_name):
    """
    직업 이름에 따라 스킬 리스트를 반환합니다.
    :param job_name: 직업 이름 (예: "탱커", "힐러")
    :return: 스킬 객체 리스트
    """
    try:
        # JSON 파일 로드
        with open("data/skills_mapping.json", "r", encoding="utf-8") as file:
            skill_mapping = json.load(file)

        # 직업에 해당하는 스킬 이름 리스트 가져오기
        skill_names = skill_mapping.get(job_name, [])

        # 스킬 이름을 클래스 객체로 변환
        return [SKILL_CLASSES[skill_name]() for skill_name in skill_names]

    except (FileNotFoundError, KeyError) as e:
        print(f"스킬 매핑 로드 중 오류 발생: {e}")
        return []