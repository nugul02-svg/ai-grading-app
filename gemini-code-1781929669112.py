import streamlit as st
import re

st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

def grade_set_3_q1(ans_1, ans_2, ans_3):
    feedback = []
    score = 0
    
    # (1) 올림픽 경기에 비유
    if re.search(r'(로봇|기계)', ans_1) and re.search(r'(실수|완벽|피겨)', ans_1):
        score += 1
        feedback.append("✅ (1) 정답: 로봇이 실수 없이 완벽하게 피겨 스케이팅을 해내는 것에 잘 비유했습니다.")
    else:
        feedback.append("❌ (1) 오답: '로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내는 것'이라는 비유가 포함되어야 합니다.")

    # (2) 예술로 볼 수 있는가 (근거 포함)
    if re.search(r'(감정|철학|이야기)', ans_2) and re.search(r'(없|어렵|아니)', ans_2):
        score += 1
        feedback.append("✅ (2) 정답: 감정이나 독자적인 철학이 없다는 근거와 함께 예술로 보기 어렵다는 결론을 잘 도출했습니다.")
    else:
        feedback.append("❌ (2) 오답: 감정이나 독자적인 철학/이야기가 없기 때문에 예술로 보기 어렵다는 내용이 들어가야 합니다.")

    # (3) 예술로서의 가치
    if re.search(r'(미술계|변화|범주|확장|상징적|의미|가치)', ans_3):
        score += 1
        feedback.append("✅ (3) 정답: 미술계에 변화를 가져왔거나 예술의 범주를 확장한다는 상징적 가치를 잘 적었습니다.")
    else:
        feedback.append("❌ (3) 오답: 기존 미술계에 큰 변화를 주었거나 예술의 범주를 확장할 수 있다는 상징적 가치가 명시되어야 합니다.")
        
    return score, feedback

def grade_set_3_q2(ans_1, ans_2):
    feedback = []
    methods_found = []
    
    method_pattern = r'\((비교와 대조|대조|비교|예시|정의|인과|분석|분류와 구분)(법)?\)'
    match_1 = re.search(method_pattern, ans_1)
    match_2 = re.search(method_pattern, ans_2)
    
    if match_1: methods_found.append(match_1.group(1))
    if match_2: methods_found.append(match_2.group(1))
    
    if len(set(methods_found)) == 2:
        feedback.append(f"✅ 조건 충족: 서로 다른 두 가지 설명 방법({', '.join(set(methods_found))})을 기재했습니다.")
    else:
        feedback.append("❌ 조건 미충족: (1)과 (2)에 서로 다른 설명 방법이 명시되지 않았거나 괄호 표기가 누락되었습니다.")
        return 0, feedback

    feedback.append("⚠️ [AI 내용 분석] 지문에 없는 외부 지식(예: 다른 AI 프로그램 이름 등)이 쓰였는지, 문맥이 매끄러운지 선생님의 최종 확인이 필요합니다.")
    return 2, feedback

def grade_set_3_q3(vis, vis_eff, aud, aud_eff):
    feedback = []
    
    # Ⓐ 시각 요소 및 효과 채점
    if re.search(r'(인간|선수|땀|노력|열정|고뇌|작가|관중)', vis):
        feedback.append("✅ Ⓐ 시각 요소: 기계와 대조되는 인간의 노력, 열정, 감정이 담긴 역동적인 장면이 잘 설정되었습니다.")
    else:
        feedback.append("△ Ⓐ 시각 요소: 장면 1(로봇의 피겨)과 대조되도록, 인간 선수의 땀과 열정, 혹은 작가의 고뇌가 드러나는 장면이면 더 좋습니다.")
        
    if re.search(r'(감동|울림|감정|철학|경험|내외부적)', vis_eff):
        feedback.append("✅ Ⓐ 시각 효과: 본문에 근거(작가의 경험, 감정, 울림 등)하여 효과를 잘 서술했습니다.")
    else:
        feedback.append("❌ Ⓐ 시각 효과: 윗글에 제시된 내용('마음을 울림', '고유한 감정이나 철학' 등)을 근거로 제시해야 합니다.")

    # Ⓑ 청각 요소 및 효과 채점
    if re.search(r'(환호|박수|심장|오케스트라|따뜻|감동|응원|거친 숨)', aud):
        feedback.append("✅ Ⓑ 청각 요소: 기계음과 완벽히 대비되는 따뜻하고 감동적인 소리(환호성, 거친 숨소리 등)가 잘 설정되었습니다.")
    else:
        feedback.append("△ Ⓑ 청각 요소: 장면 1의 기계음과 명확히 대조되는, 감동이나 열정을 줄 수 있는 소리인지 확인해 보세요.")

    if re.search(r'(울림|감동|감정|열정|노력)', aud_eff):
        feedback.append("✅ Ⓑ 청각 효과: 청각 요소가 주는 효과를 지문 속 인간 예술의 가치와 잘 연결했습니다.")
    else:
        feedback.append("❌ Ⓑ 청각 효과: 윗글에 제시된 내용('열정', '마음을 울림' 등)이 근거로 드러나야 합니다.")

    feedback.append("⚠️ [AI 내용 분석] 영상 연출의 구체성과 논리성은 선생님의 꼼꼼한 확인이 한 번 더 필요합니다.")
    return feedback

# --- 웹앱 UI ---
st.title("📝 2회고사 대비 서·논술형 AI 자동 채점")
st.markdown("---")

st.subheader("[실전 적용-3] 인공 지능이 그린 그림을 바라보는 시각")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 문항 1. 내용 요약하기")
    ans1_1 = st.text_input("㉠ (올림픽 경기에 비유):", placeholder="예: 로봇이 완벽하게 피겨 스케이팅을 해내는 것")
    ans1_2 = st.text_input("㉡ (예술로 볼 수 있는가):", placeholder="예: 감정이나 철학이 없어 예술로 보기 어려움")
    ans1_3 = st.text_input("㉢ (예술로서의 가치):", placeholder="예: 미술계에 큰 변화를 주며 상징적 가치가 있음")
    
    st.markdown("#### 문항 2. 설명문 작성 (조건: 2가지 설명 방법 활용)")
    ans2_1 = st.text_input("문장 (1):", placeholder="문장을 작성하고 끝에 (설명방법)을 쓰세요.")
    ans2_2 = st.text_input("문장 (2):", placeholder="문장을 작성하고 끝에 (설명방법)을 쓰세요.")

    st.markdown("#### 문항 3. 영상 매체 기획 (시·청각 요소와 효과)")
    ans3_vis = st.text_input("Ⓐ 시각 요소:", placeholder="어떤 화면을 보여줄 것인가요?")
    ans3_vis_eff = st.text_input("Ⓐ 시각 요소 효과:", placeholder="지문의 내용을 근거로 효과를 적어주세요.")
    ans3_aud = st.text_input("Ⓑ 청각 요소:", placeholder="어떤 소리를 들려줄 것인가요?")
    ans3_aud_eff = st.text_input("Ⓑ 청각 요소 효과:", placeholder="지문의 내용을 근거로 효과를 적어주세요.")

with col2:
    st.markdown("#### 📊 채점 결과 및 모범 답안")
    if st.button("AI 채점 시작"):
        with st.spinner("학생 답안을 분석 중입니다..."):
            score1, fb1 = grade_set_3_q1(ans1_1, ans1_2, ans1_3)
            score2, fb2 = grade_set_3_q2(ans2_1, ans2_2)
            fb3 = grade_set_3_q3(ans3_vis, ans3_vis_eff, ans3_aud, ans3_aud_eff)
            
            st.success(f"**문항 1 점수:** {score1}/3점")
            for msg in fb1: st.write(msg)
            
            st.markdown("---")
            st.success(f"**문항 2 점수:** {score2}/2점 (내용 확인 필요)")
            for msg in fb2: st.write(msg)

            st.markdown("---")
            st.success("**문항 3 분석 결과** (내용 확인 필요)")
            for msg in fb3: st.write(msg)
            
            st.markdown("---")
            with st.expander("💡 각 문항별 모범 답안 확인하기"):
                st.markdown("""
                **[1번 문항 모범 답안]**
                * ㉠: 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내는 것
                * ㉡: 감정도 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 예술로 보기는 어렵다.
                * ㉢: 기존 미술계에 큰 변화를 가져왔으며, 예술의 범주를 확장할 수 있다는 상징적인 가치를 지닌다.
                
                **[2번 문항 모범 답안 예시]**
                * (1) 인공 지능의 그림은 감정이나 독자적인 철학이 없기 때문에 진정한 예술로 보기는 어렵다. (인과)
                * (2) 인간의 작품에는 작가의 고유한 감정과 경험이 담겨 있는 반면, 인공 지능의 그림에는 이러한 내외부적 요소가 없기 때문이다. (비교와 대조)

                **[3번 문항 모범 답안 예시]**
                * Ⓐ 시각 요소: 인간 선수가 땀을 흘리며 열정적으로 경기에 임하거나, 결과에 감격해 우는 역동적인 장면
                * Ⓐ 시각 효과: 지문에 언급된 '인간 선수의 노력이나 열정, 작가의 고유한 감정'이 예술의 진정한 감동을 만든다는 점을 시각적으로 강조함.
                * Ⓑ 청각 요소: 관중들의 뜨거운 환호성과 선수의 거친 숨소리, 또는 웅장하고 감동적인 오케스트라 음악
                * Ⓑ 청각 효과: 기계음과 대조적으로, 인간의 감정과 열정이 사람의 '마음을 울린다'는 본문의 내용을 청각적으로 효과적으로 전달함.
                """)
