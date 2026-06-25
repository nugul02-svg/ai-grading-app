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

# --- 채점 함수 모음 ---
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
    if re.search(r'(쉬운|노력|필요 없는)', a1): fb["q1"].append("✅ ㉠ 정답")
    else: fb["q1"].append("❌ ㉠ 오답: '비교적 쉬운 과제' 등의 의미가 들어가야 합니다.")
    if re.search(r'(혼자|집중|차분)', a2): fb["q1"].append("✅ ㉡ 정답")
    else: fb["q1"].append("❌ ㉡ 오답: '차분하게 혼자 집중하는 시간'이 들어가야 합니다.")
    if re.search(r'(억제)', a3): fb["q1"].append("✅ ㉢ 정답")
    else: fb["q1"].append("❌ ㉢ 오답: '사회적 억제'가 들어가야 합니다.")
    
    if re.search(r'(혼자|방|조용|독서실)', vis): fb["q3"].append("✅ Ⓐ 시각: 혼자 집중하는 환경을 잘 설정했습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 타인이 없는 혼자만의 집중 환경이 드러나야 합니다.")
    if re.search(r'(억제|방해|집중|효율)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 윗글의 내용을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 지문을 근거로 서술해야 합니다.")
    
    if re.search(r'(고요|무음|조용|차분|사각)', aud): fb["q3"].append("✅ Ⓑ 청각: 방해받지 않는 소리 환경을 잘 설정했습니다.")
    else: fb["q3"].append("△ Ⓑ 청각: 타인의 소음이 없는 조용한 환경이 드러나야 합니다.")
    if re.search(r'(집중|어려운|억제|방해)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 윗글의 내용을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 지문을 근거로 서술해야 합니다.")
    return fb

def grade_set2(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(고여|높은)', a1): fb["q1"].append("✅ ㉠ 정답")
    else: fb["q1"].append("❌ ㉠ 오답: '고여 있는 물'에 비유해야 합니다.")
    if re.search(r'(이동하지|머물러|정지)', a2): fb["q1"].append("✅ ㉡ 정답")
    else: fb["q1"].append("❌ ㉡ 오답: 전하가 이동하지 않고 머물러 있다는 내용이 필요합니다.")
    if re.search(r'(위험하지 않|피해|없)', a3): fb["q1"].append("✅ ㉢ 정답")
    else: fb["q1"].append("❌ ㉢ 오답: 감전 등의 위험이 없다는 내용이 필요합니다.")
    
    if re.search(r'(고인|호수|잔잔|댐)', vis): fb["q3"].append("✅ Ⓐ 시각: 정전기의 특성을 시각적으로 잘 표현했습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 잔잔하게 고여 있는 물의 이미지가 필요합니다
