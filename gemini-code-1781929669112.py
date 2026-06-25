import streamlit as st
import re

st.set_page_config(page_title="서·논술형 답안 작성 연습", layout="wide")

# --- UI 디자인 컴포넌트 함수 ---
def draw_side_guide():
    with st.sidebar:
        st.header("📖 개념 길잡이")
        st.markdown("---")
        
        with st.expander("📝 1. 6가지 설명 방법", expanded=True):
            st.markdown("""
            * **정의:** 대상의 뜻/개념 밝힘
            * **예시:** 구체적 사례 제시
            * **인과:** 원인과 결과를 중심
            * **분석:** 요소를 나누어 설명
            * **비교/대조:** 공통점/차이점 제시
            * **분류/구분:** 기준에 따라 나눔
            """)
            st.info("**[2번 문제 꿀팁]**\n문장을 만들고 끝에 (설명방법)을 꼭 쓰세요! 서로 다른 두 방법을 사용해야 합니다.")

        with st.expander("🎬 2. 영상 매체와 복합양식성", expanded=True):
            st.markdown("* **복합양식성:** 문자, 소리, 그림 등 다양한 양식의 결합")
            st.warning("**[3번 문제 꿀팁]**\n효과를 기술할 때는 **'윗글의 근거'**가 반드시 들어가야 합니다. '그냥 보기 좋다'는 오답입니다!")

# [사이드바 호출]
draw_side_guide()

# --- 이하 기존의 탭 구성 및 로직 코드를 그대로 유지하여 붙여넣으세요 ---
# (앞서 제공해 드린 탭 구성 코드와 합치면 완성됩니다.)
