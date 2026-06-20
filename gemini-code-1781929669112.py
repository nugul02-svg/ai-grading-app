import streamlit as st
import re

st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

def grade_set_3_q1(ans_1, ans_2, ans_3):
    feedback = []
    score = 0
    
    # ㉠ 채점: 의미 허용 (용어 없어도 필수 의미 포함 시 통과)
    if re.search(r'(다른|다르게)', ans_1) and re.search(r'(감정|받아들|느낌)', ans_1):
        score += 1
        feedback.append("✅ ㉠ 정답: '다른 감정/받아들임'의 의미가 잘 담겼습니다.")
    else:
        feedback.append("❌ ㉠ 오답: 같은 경험이라도 '다른 감정'으로 받아들일 수 있다는 의미가 필요합니다.")

    # ㉡ 채점: 결론 방향 확인
    if re.search(r'(사람|풍경|아름다움|세상)', ans_2) and re.search(r'(천천히|음미)', ans_2):
        score += 1
        feedback.append("✅ ㉡ 정답: 대상(사람/풍경)과 태도(천천히 음미)가 명확히 드러났습니다.")
    else:
        feedback.append("❌ ㉡ 오답: 세상(사람, 풍경)을 '천천히 음미'해야 한다는 결론이 누락되었습니다.")

    # ㉢ 채점: 오개념 및 범주 오류 방지 (가장 중요한 로직)
    # 한 개념의 특성을 다른 개념에 쓰면 오답 처리 (음식 칸에 세상 이야기를 쓴 경우)
    if re.search(r'(세상|아름다움|포착)', ans_3):
        feedback.append("❌ ㉢ 오답 (범주 오류): 이 빈칸은 '음식을 맛보는 일'의 결과입니다. '세상의 아름다움'은 삶에 해당하는 비유이므로 적절하지 않습니다.")
    elif "맛" in ans_3 and re.search(r'(느낄|알 수 없|다채로움)', ans_3):
        score += 1
        feedback.append("✅ ㉢ 정답: 마구 삼켰을 때 '맛'을 제대로 느낄 수 없다는 한계를 정확히 짚었습니다.")
    else:
        feedback.append("❌ ㉢ 오답: 음식을 마구 삼켰을 때 '맛을 제대로 느낄 수 없음'이 명시되어야 합니다.")
        
    return score, feedback

def grade_set_3_q2(ans_1, ans_2):
    feedback = []
    methods_found = []
    
    # 정규식: 괄호 안의 설명 방법 명칭 추출 ('법' 접미사 허용)
    method_pattern = r'\((비교와 대조|예시|정의|인과|분석|분류와 구분)(법)?\)'
    match_1 = re.search(method_pattern, ans_1)
    match_2 = re.search(method_pattern, ans_2)
    
    if match_1: methods_found.append(match_1.group(1))
    if match_2: methods_found.append(match_2.group(1))
    
    # 조건 1: 서로 다른 2가지 방법 사용 확인
    if len(set(methods_found)) == 2:
        feedback.append(f"✅ 조건 충족: 서로 다른 두 가지 설명 방법({', '.join(set(methods_found))})을 사용했습니다.")
    else:
        feedback.append("❌ 조건 미충족: 괄호 안에 명칭을 정확히 표기하지 않았거나, 두 방법이 중복되었습니다.")
        return 0, feedback

    # 조건 2: 특정 방법을 선택한 경우 그 특성이 드러나는지 확인 (키워드/결론 방향)
    # (실제 고도화 시에는 이 부분에 LLM API를 연결하여 외부 지식 차단 여부를 판별하는 것이 좋습니다.)
    feedback.append("⚠️ [AI 내용 분석] 지문에 없는 외부 배경지식이 포함되었는지 교사 확인이 필요합니다.")
    
    return 2, feedback

# --- 웹앱 UI ---
st.title("📝 2회고사 대비 서·논술형 AI 자동 채점")
st.markdown("---")

st.subheader("[실전 적용-3] 음식을 맛보는 일과 세상을 살아가는 일")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 문항 1. 내용 요약하기")
    ans1_1 = st.text_input("㉠의 내용:", placeholder="예: 다른 감정으로 받아들일 수 있음")
    ans1_2 = st.text_input("㉡의 내용:", placeholder="예: 모든 사람과 풍경을 천천히 음미해야 함")
    ans1_3 = st.text_input("㉢의 내용:", placeholder="예: 맛의 다채로움을 느낄 수 없음")
    
    st.markdown("#### 문항 2. 설명문 작성 (조건: 2가지 설명 방법 활용)")
    ans2_1 = st.text_input("문장 (1):", placeholder="문장을 작성하고 끝에 (설명방법)을 쓰세요.")
    ans2_2 = st.text_input("문장 (2):", placeholder="문장을 작성하고 끝에 (설명방법)을 쓰세요.")

with col2:
    st.markdown("#### 📊 채점 결과 및 모범 답안")
    if st.button("AI 채점 시작"):
        with st.spinner("학생 답안을 분석 중입니다..."):
            score1, fb1 = grade_set_3_q1(ans1_1, ans1_2, ans1_3)
            score2, fb2 = grade_set_3_q2(ans2_1, ans2_2)
            
            st.success(f"**문항 1 점수:** {score1}/3점")
            for msg in fb1: st.write(msg)
            
            st.markdown("---")
            st.success(f"**문항 2 점수:** {score2}/2점 (내용 확인 필요)")
            for msg in fb2: st.write(msg)
            
            st.markdown("---")
            with st.expander("💡 각 문항별 모범 답안 확인하기"):
                st.markdown("""
                **[1번 문항 모범 답안]**
                * ㉠: 같은 경험을 해도 다른 감정으로 받아들일 수 있음
                * ㉡: 모든 사람과 풍경, 그 속의 아름다움을 천천히 음미해야 함
                * ㉢: (마구 삼켜서는) 맛을 제대로 느낄 수 없음
                
                **[2번 문항 모범 답안 예시]**
                * (1) 빠르게 달리기만 하면 놓치기 쉽지만, 천천히 살피면 온전히 느낄 수 있다. (비교와 대조)
                * (2) 세상의 다채로움을 느끼려면 주변 풍경을 음미하는 시간을 가져야 하기 때문이다. (인과)
                """)