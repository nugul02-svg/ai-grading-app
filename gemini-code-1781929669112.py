import streamlit as st
import re

st.set_page_config(page_title="서·논술형 답안 작성 연습", layout="wide")

# --- 세션 상태 초기화 ---
if 'completed' not in st.session_state:
    st.session_state.completed = {'set1': False, 'set2': False, 'set3': False}
if 'feedback' not in st.session_state:
    st.session_state.feedback = {'set1': None, 'set2': None, 'set3': None}

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]

# --- UI 디자인 컴포넌트 함수 ---
def draw_blue_box(text):
    st.markdown(f"""
    <div style='background-color: #f0f4fa; padding: 20px; border-radius: 8px; color: #1e3a8a; margin-bottom: 20px; line-height: 1.6; font-size: 15px;'>
    {text}
    </div>
    """, unsafe_allow_html=True)

def draw_gray_box(text):
    st.markdown(f"""
    <div style='background-color: #f5f5f5; padding: 20px; border-radius: 8px; border-left: 6px solid #a1a1aa; margin-bottom: 20px; line-height: 1.6; font-size: 15px;'>
    <b>&lt;조건&gt;</b><br>
    {text}
    </div>
    """, unsafe_allow_html=True)

# --- 상단 레이아웃 ---
st.title("✏️ [국어] 서·논술형 답안 작성 연습")
st.markdown("작성한 답안을 입력한 뒤 문제의 조건에 맞게 작성하였는지의 여부를 확인하세요. 수업시간에 배운 내용을 복습할 때 마음이 막막할까봐 만든 자료이므로, 참고로만 활용하세요. 선생님과 수업 시간에 공부한 내용이 답안 작성의 초점이에요 😉")

st.markdown("---")

completed_count = sum(st.session_state.completed.values())
st.markdown(f"**✅ 완료된 문제: {completed_count} / 3**")
st.progress(completed_count / 3)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("1~3번 세트를 모두 제출하면 마지막 탭 **'📚 복습할 내용'**에서 피드백을 한눈에 확인할 수 있어요. 답안을 초기화하고 처음부터 다시 풀고 싶다면 다음의 버튼을 누르세요.")
with col2:
    if st.button("🔄 처음부터 다시 풀기", use_container_width=True):
        reset_all()
        st.rerun()

st.markdown("---")

# --- 채점 함수 모음 (이전과 동일) ---
def grade_q2(ans_1, ans_2):
    feedback = []
    methods_found = []
    method_pattern = r'\((비교와 대조|대조|비교|예시|정의|인과|분석|분류와 구분)(법)?\)'
    match_1 = re.search(method_pattern, ans_1)
    match_2 = re.search(method_pattern, ans_2)
    if match_1: methods_found.append(match_1.group(1))
    if match_2: methods_found.append(match_2.group(1))
    
    if len(set(methods_found)) == 2:
        feedback.append(f"✅ 조건 충족: 서로 다른 두 가지 설명 방법({', '.join(set(methods_found))})을 활용했습니다.")
    else:
        feedback.append("❌ 조건 미충족: 문장 끝에 서로 다른 설명 방법을 괄호 안에 표기해야 합니다.")
    return feedback

def grade_set1(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(쉬운|노력|필
