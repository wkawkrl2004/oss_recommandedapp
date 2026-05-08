import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="오버워치 영웅 추천기", page_icon="🎮", layout="centered")

st.title("🎮 오버워치 영웅 추천기")
st.markdown("당신의 플레이 스타일을 입력하면 어울리는 영웅을 추천해 드립니다.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    role = st.selectbox(
        "선호 역할군",
        ["탱커", "딜러", "힐러"],
        help="주로 담당하고 싶은 역할을 선택하세요."
    )

    style = st.selectbox(
        "플레이 스타일",
        ["공격적", "수비적", "서포트중심"],
        help="전투에서 주로 취하는 태도를 선택하세요."
    )

    range_ = st.selectbox(
        "선호 교전 거리",
        ["근거리", "중거리", "원거리"],
        help="적과의 거리 중 편한 구간을 선택하세요."
    )

with col2:
    difficulty = st.selectbox(
        "선호 난이도",
        ["쉬움", "보통", "어려움"],
        help="다루고 싶은 영웅의 조작 난이도를 선택하세요."
    )

    mobility = st.selectbox(
        "이동기 중요도",
        ["중요함", "상관없음"],
        help="대시, 점프 등 이동 스킬을 중시하는지 선택하세요."
    )

    positioning = st.selectbox(
        "포지셔닝 스타일",
        ["본대", "사이드", "둘다"],
        help="팀과 함께 움직이는 본대 플레이 vs 측면을 치는 사이드 플레이."
    )

st.divider()

if st.button("🔍 영웅 추천받기", use_container_width=True, type="primary"):
    payload = {
        "role": role,
        "style": style,
        "range": range_,
        "difficulty": difficulty,
        "mobility": mobility,
        "positioning": positioning,
    }

    with st.spinner("추천 영웅을 분석 중입니다..."):
        try:
            response = requests.post(f"{BACKEND_URL}/recommend", json=payload, timeout=5)
            response.raise_for_status()
            data = response.json()

            st.success("✅ 추천 완료!")
            st.subheader("🏆 추천 영웅")

            for i, hero in enumerate(data["recommendations"], start=1):
                with st.container(border=True):
                    st.markdown(f"### {i}위. {hero['name']}")
                    st.markdown(f"💡 {hero['reason']}")

        except requests.exceptions.ConnectionError:
            st.error("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해 주세요.")
        except requests.exceptions.Timeout:
            st.error("❌ 서버 응답 시간이 초과되었습니다.")
        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {e}")
