import json
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

HEROES = json.loads(Path("heroes.json").read_text(encoding="utf-8"))

DIFFICULTY_ORDER = {"쉬움": 0, "보통": 1, "어려움": 2}


class UserInput(BaseModel):
    role: str          # 탱커 / 딜러 / 힐러
    style: str         # 공격적 / 수비적 / 서포트중심
    range: str         # 근거리 / 중거리 / 원거리
    difficulty: str    # 쉬움 / 보통 / 어려움
    mobility: str      # 중요함 / 상관없음
    positioning: str   # 본대 / 사이드 / 둘다


class HeroRecommendation(BaseModel):
    name: str
    reason: str


class RecommendResponse(BaseModel):
    recommendations: List[HeroRecommendation]


def score_hero(hero: dict, user: UserInput) -> float:
    score = 0

    if hero["role"] == user.role:
        score += 4  # 역할군은 가장 중요 
    # 포지셔닝 점수
    if hero["positioning"] == user.positioning and user.positioning != "둘다":
        score += 3  # 완전 일치
    elif hero["positioning"] == "둘다" and user.positioning == "둘다":
        score += 2.5  # 유연 매칭    
    elif hero["positioning"] == "둘다" or user.positioning == "둘다":
        score += 2  # 둘다끼리도 살짝 더 우대

    if hero["style"] == user.style:
        score += 2
    if hero["range"] == user.range:
        score += 2
    if hero["mobility"] == user.mobility:
        score += 1

    # 난이도는 요청 난이도와 가까울수록 점수 부여
    diff_gap = abs(
        DIFFICULTY_ORDER.get(hero["difficulty"], 1)
        - DIFFICULTY_ORDER.get(user.difficulty, 1)
    )
    score += max(0, 2 - diff_gap)

    return score


def build_reason(hero: dict, user: UserInput) -> str:
    reasons = []

    
    if hero["positioning"] == user.positioning and user.positioning != "둘다":
        if user.positioning == "본대":
            reasons.append("본대 중심 플레이에 최적화")
        else:
            reasons.append("사이드 운영에 특화")
    elif hero["positioning"] == "둘다" and user.positioning == "둘다":
        reasons.append("모든 포지셔닝에서 자유로운 플레이 가능")
    elif hero["positioning"] == "둘다":
        reasons.append("본대와 사이드 모두 대응 가능한 유연한 플레이")
    elif user.positioning == "둘다":
        reasons.append("다양한 포지션에서 활용 가능")
    if hero["style"] == user.style:
        style_map = {"공격적": "공격적인 플레이 스타일", "수비적": "수비적인 운영", "서포트중심": "팀 서포트 중심 플레이"}
        reasons.append(style_map.get(user.style, user.style))
    if hero["range"] == user.range:
        reasons.append(f"{user.range} 전투에 강함")
    if hero["mobility"] == "중요함" and user.mobility == "중요함":
        reasons.append("뛰어난 이동기 보유")
    if hero["difficulty"] == user.difficulty:
        reasons.append(f"난이도 {user.difficulty} 수준에 적합")

    if not reasons:
        reasons.append("전반적인 플레이 스타일과 부합")

    return ", ".join(reasons)


@app.post("/recommend", response_model=RecommendResponse)
def recommend(user: UserInput):
    scored = [(hero, score_hero(hero, user)) for hero in HEROES]
    scored.sort(key=lambda x: x[1], reverse=True)

    top3 = scored[:3]
    recommendations = [
        HeroRecommendation(name=hero["name"], reason=build_reason(hero, user))
        for hero, _ in top3
    ]

    return RecommendResponse(recommendations=recommendations)


@app.get("/health")
def health():
    return {"status": "ok"}
