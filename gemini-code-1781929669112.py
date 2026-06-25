import streamlit as st
import re

st.set_page_config(page_title="서·논술형 답안 작성 연습", layout="wide")

# --- 세션 상태 초기화 (진행률 및 결과 저장용) ---
if 'completed' not in st.session_state:
    st.session_state.completed = {'set1': False, 'set2': False, 'set3': False}
if 'feedback' not in st.session_state:
    st.session_state.feedback = {'set1': None, 'set2': None, 'set3': None}

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]

# --- 상단 레이아웃 (스크린샷과 동일하게 구현) ---
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

# 1세트 채점
def grade_set1(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(쉬운|노력|필요 없는)', a1): fb["q1"].append("✅ ㉠ 정답")
    else: fb["q1"].append("❌ ㉠ 오답: '비교적 쉬운 취미나 큰 노력을 들일 필요가 없는 과제'가 들어가야 합니다.")
    if re.search(r'(혼자|집중|차분)', a2): fb["q1"].append("✅ ㉡ 정답")
    else: fb["q1"].append("❌ ㉡ 오답: '차분하게 혼자 집중하는 시간을 가짐'이 들어가야 합니다.")
    if re.search(r'(억제)', a3): fb["q1"].append("✅ ㉢ 정답")
    else: fb["q1"].append("❌ ㉢ 오답: '사회적 억제'가 들어가야 합니다.")
    
    if re.search(r'(혼자|방|조용|독서실)', vis): fb["q3"].append("✅ Ⓐ 시각: 혼자 집중하는 환경을 잘 설정했습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 타인이 없는 혼자만의 집중 환경이 드러나야 합니다.")
    if re.search(r'(억제|방해|집중)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 윗글의 내용을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 지문을 근거로 서술해야 합니다.")
    
    if re.search(r'(고요|무음|조용|차분)', aud): fb["q3"].append("✅ Ⓑ 청각: 방해받지 않는 소리 환경을 잘 설정했습니다.")
    else: fb["q3"].append("△ Ⓑ 청각: 타인의 소음이 없는 조용한 환경이 드러나야 합니다.")
    if re.search(r'(집중|어려운|억제)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 윗글의 내용을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 지문을 근거로 서술해야 합니다.")
    return fb

# 2세트 채점
def grade_set2(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(고여|높은)', a1): fb["q1"].append("✅ ㉠ 정답: '고여 있는 물' 비유가 들어갔습니다.")
    else: fb["q1"].append("❌ ㉠ 오답: '고여 있는 물'에 비유해야 합니다.")
    if re.search(r'(이동하지|머물러|정지)', a2): fb["q1"].append("✅ ㉡ 정답: 전하의 상태를 잘 적었습니다.")
    else: fb["q1"].append("❌ ㉡ 오답: 전하가 이동하지 않고 머물러 있다는 내용이 필요합니다.")
    if re.search(r'(위험하지 않|피해|없)', a3): fb["q1"].append("✅ ㉢ 정답: 위험성이 없다는 것을 잘 적었습니다.")
    else: fb["q1"].append("❌ ㉢ 오답: 감전 등의 위험이 없다는 내용이 필요합니다.")
    
    if re.search(r'(고인|호수|잔잔|댐)', vis): fb["q3"].append("✅ Ⓐ 시각 요소: 이동하지 않는 정전기의 특성을 시각적으로 잘 표현했습니다.")
    else: fb["q3"].append("△ Ⓐ 시각 요소: 잔잔하게 고여 있는 물의 이미지가 필요합니다.")
    if re.search(r'(이동|머물|안전|위험하지)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 지문을 근거로 시각 효과를 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 전하가 이동하지 않아 안전하다는 지문 내용이 포함되어야 합니다.")
    
    if re.search(r'(조용|고요|잔잔|바람)', aud): fb["q3"].append("✅ Ⓑ 청각 요소: 흐르지 않는 정전기의 고요한 특성을 잘 표현했습니다.")
    else: fb["q3"].append("△ Ⓑ 청각 요소: 폭포 소리와 대비되는 고요한 소리가 좋습니다.")
    if re.search(r'(위험하지|이동하지|머물)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 지문을 근거로 청각 효과를 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 지문을 근거로 서술해야 합니다.")
    return fb

# 3세트 채점
def grade_set3(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(로봇|기계)', a1) and re.search(r'(실수|완벽|피겨)', a1): fb["q1"].append("✅ ㉠ 정답: 로봇의 완벽한 피겨 스케이팅 비유가 들어갔습니다.")
    else: fb["q1"].append("❌ ㉠ 오답: '로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내는 것'이 필요합니다.")
    if re.search(r'(감정|철학|이야기)', a2) and re.search(r'(없|어렵|아니)', a2): fb["q1"].append("✅ ㉡ 정답: 감정이나 철학이 없다는 근거가 포함되었습니다.")
    else: fb["q1"].append("❌ ㉡ 오답: 감정이나 독자적인 철학이 없어 예술로 보기 어렵다는 내용이 들어가야 합니다.")
    if re.search(r'(미술계|변화|범주|확장|상징적)', a3): fb["q1"].append("✅ ㉢ 정답: 예술의 범주 확장 등 상징적 가치가 잘 적혔습니다.")
    else: fb["q1"].append("❌ ㉢ 오답: 기존 미술계에 큰 변화를 주었거나 예술의 범주를 확장할 수 있다는 상징적 가치가 명시되어야 합니다.")
    
    if re.search(r'(인간|선수|땀|노력|열정|고뇌)', vis): fb["q3"].append("✅ Ⓐ 시각: 기계와 대조되는 인간의 열정이 잘 설정되었습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 인간 선수의 노력과 열정이 드러나는 장면이 좋습니다.")
    if re.search(r'(감동|울림|감정|철학|경험)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 본문에 근거하여 효과를 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 윗글에 제시된 내용(마음을 울림 등)을 근거로 제시해야 합니다.")
    
    if re.search(r'(환호|박수|심장|오케스트라|감동|숨)', aud): fb["q3"].append("✅ Ⓑ 청각: 감동과 열정을 주는 소리가 잘 설정되었습니다.")
    else: fb["q3"].append("△ Ⓑ 청각: 기계음과 대조되는 감동적인 소리인지 확인해 보세요.")
    if re.search(r'(울림|감동|감정|열정|노력)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 청각 요소가 주는 효과를 지문 내용과 잘 연결했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 윗글에 제시된 내용(마음을 울림 등)이 근거로 드러나야 합니다.")
    return fb

# --- 탭 구성 ---
tab1, tab2, tab3, tab4 = st.tabs(["실전 적용 1", "실전 적용 2", "실전 적용 3", "📚 복습할 내용"])

# 탭 1 (사회적 촉진과 억제)
with tab1:
    st.subheader("💡 [실전 적용 1] 과제 난이도와 사회적 촉진/억제")
    with st.form("form_set1"):
        st.markdown("**[문항 1] 요약하기 (빈칸 채우기)**")
        s1_a1 = st.text_input("㉠ 특성 (사회적 촉진):", placeholder="어떤 과제일 때?")
        s1_a2 = st.text_input("㉡ 효율적인 환경 및 방법 (어려운 과제):")
        s1_a3 = st.text_input("㉢ 관련된 심리 현상 (어려운 과제):")
        
        st.markdown("**[문항 2] 설명문 작성하기**")
        s1_q2_1 = st.text_input("(1) 첫 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        s1_q2_2 = st.text_input("(2) 두 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("**[문항 3] 영상 매체 기획 (장면 2: 어려운 과제를 할 때)**")
        s1_vis = st.text_input("Ⓐ 시각 요소:")
        s1_vis_eff = st.text_input("Ⓐ 효과 (지문 근거 포함):")
        s1_aud = st.text_input("Ⓑ 청각 요소:")
        s1_aud_eff = st.text_input("Ⓑ 효과 (지문 근거 포함):")
        
        if st.form_submit_button("1세트 제출 및 채점하기"):
            st.session_state.feedback['set1'] = grade_set1(s1_a1, s1_a2, s1_a3, s1_q2_1, s1_q2_2, s1_vis, s1_vis_eff, s1_aud, s1_aud_eff)
            st.session_state.completed['set1'] = True
            st.success("✅ 1세트 채점이 완료되었습니다. '복습할 내용' 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 2 (정전기)
with tab2:
    st.subheader("💡 [실전 적용 2] 전압은 높지만 위험하지 않은 정전기")
    with st.form("form_set2"):
        st.markdown("**[문항 1] 요약하기 (빈칸 채우기)**")
        s2_a1 = st.text_input("㉠ 물의 상태에 비유:")
        s2_a2 = st.text_input("㉡ 전하의 상태:")
        s2_a3 = st.text_input("㉢ 위험성:")
        
        st.markdown("**[문항 2] 설명문 작성하기**")
        s2_q2_1 = st.text_input("(1) 첫 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        s2_q2_2 = st.text_input("(2) 두 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("**[문항 3] 영상 매체 기획 (장면 2: 정전기)**")
        s2_vis = st.text_input("Ⓐ 시각 요소:")
        s2_vis_eff = st.text_input("Ⓐ 효과 (지문 근거 포함):")
        s2_aud = st.text_input("Ⓑ 청각 요소:")
        s2_aud_eff = st.text_input("Ⓑ 효과 (지문 근거 포함):")
        
        if st.form_submit_button("2세트 제출 및 채점하기"):
            st.session_state.feedback['set2'] = grade_set2(s2_a1, s2_a2, s2_a3, s2_q2_1, s2_q2_2, s2_vis, s2_vis_eff, s2_aud, s2_aud_eff)
            st.session_state.completed['set2'] = True
            st.success("✅ 2세트 채점이 완료되었습니다. '복습할 내용' 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 3 (인공지능의 예술)
with tab3:
    st.subheader("💡 [실전 적용 3] 인공 지능이 그린 그림을 바라보는 시각")
    with st.form("form_set3"):
        st.markdown("**[문항 1] 요약하기 (빈칸 채우기)**")
        s3_a1 = st.text_input("㉠ 올림픽 경기에 비유:")
        s3_a2 = st.text_input("㉡ 예술로 볼 수 있는가 (근거 포함):")
        s3_a3 = st.text_input("㉢ 예술로서의 가치:")
        
        st.markdown("**[문항 2] 설명문 작성하기**")
        s3_q2_1 = st.text_input("(1) 첫 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        s3_q2_2 = st.text_input("(2) 두 번째 문장:", placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("**[문항 3] 영상 매체 기획 (장면 2: 마음에 울림을 주는 진정한 예술)**")
        s3_vis = st.text_input("Ⓐ 시각 요소:")
        s3_vis_eff = st.text_input("Ⓐ 효과 (지문 근거 포함):")
        s3_aud = st.text_input("Ⓑ 청각 요소:")
        s3_aud_eff = st.text_input("Ⓑ 효과 (지문 근거 포함):")
        
        if st.form_submit_button("3세트 제출 및 채점하기"):
            st.session_state.feedback['set3'] = grade_set3(s3_a1, s3_a2, s3_a3, s3_q2_1, s3_q2_2, s3_vis, s3_vis_eff, s3_aud, s3_aud_eff)
            st.session_state.completed['set3'] = True
            st.success("✅ 3세트 채점이 완료되었습니다. '복습할 내용' 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 4 (복습할 내용)
with tab4:
    st.subheader("📚 제출한 답안 피드백 모아보기")
    if completed_count == 0:
        st.info("아직 제출된 세트가 없습니다. 1~3세트 문제를 먼저 풀어주세요!")
    else:
        sets = [("실전 적용 1 (사회적 촉진과 억제)", 'set1'), 
                ("실전 적용 2 (정전기)", 'set2'), 
                ("실전 적용 3 (인공지능의 예술)", 'set3')]
        
        for title, key in sets:
            if st.session_state.completed[key]:
                with st.expander(f"📌 {title} 피드백 확인하기", expanded=True):
                    fb = st.session_state.feedback[key]
                    st.markdown("**[문항 1]**")
                    for msg in fb["q1"]: st.write(msg)
                    st.markdown("**[문항 2]**")
                    for msg in fb["q2"]: st.write(msg)
                    st.markdown("**[문항 3]**")
                    for msg in fb["q3"]: st.write(msg)
