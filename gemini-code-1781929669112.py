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
def draw_side_guide():
    with st.sidebar:
        st.header("📖 개념 길잡이", anchor=False)
        st.markdown("---")
        
        with st.expander("📝 1. 설명 방법 공식", expanded=True):
            st.markdown("""
            * 정의: ~란 ~를 말한다.
            * 예시: 예를 들어 ~
            * 인과: ~ 때문에 ~ 한다.
            * 비교와 대조: [공통점] ~와 ~의 공통점은 ~이다. / [차이점] ~는 ~이지만, ~는 ~이다.
            * 분석: ~는 ~와(과) ~로 이루어져 있다.
            * 분류와 구분: ~는 ~라는 기준에 따라 ~와(과) ~로 나뉜다.
            """)
            st.info("💡 2번 문제 풀이 팁: 위 공식을 활용해 문장을 만들고 끝에 (설명방법)을 꼭 쓰세요! 서로 다른 두 방법을 사용해야 합니다.")

        with st.expander("🎬 2. 영상 매체와 복합양식성", expanded=True):
            st.markdown("* 복합양식성: 문자, 소리, 그림, 사진, 동영상 등 다양한 양식이 결합된 것")
            st.warning("💡 3번 문제 풀이 팁: 효과를 기술할 때는 윗글의 내용(근거)이 반드시 들어가야 합니다. '보기 좋다'는 오답입니다!")

def draw_blue_box(text):
    st.markdown(f"<div style='background-color: #f0f4fa; padding: 20px; border-radius: 8px; color: #1e3a8a; margin-bottom: 20px; line-height: 1.6; font-size: 15px;'>{text}</div>", unsafe_allow_html=True)

def draw_gray_box(text):
    st.markdown(f"<div style='background-color: #f5f5f5; padding: 20px; border-radius: 8px; border-left: 6px solid #a1a1aa; margin-bottom: 20px; line-height: 1.6; font-size: 15px;'>&lt;조건&gt;<br>{text}</div>", unsafe_allow_html=True)

# --- 사이드바 호출 ---
draw_side_guide()

# --- 상단 레이아웃 ---
st.title("✏️ [국어] 서·논술형 답안 작성 연습", anchor=False)
st.markdown("작성한 답안을 입력한 뒤 문제의 조건에 맞게 작성하였는지의 여부를 확인하세요. 수업시간에 배운 내용을 복습할 때 마음이 막막할까봐 만든 자료이므로, 참고로만 활용하세요. 선생님과 수업 시간에 공부한 내용이 답안 작성의 초점이에요 😉")

st.markdown("---")

completed_count = sum(st.session_state.completed.values())
st.markdown(f"✅ 완료된 문제: {completed_count} / 3")
st.progress(completed_count / 3)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("1~3번 세트를 모두 제출하면 마지막 탭 '📚 복습할 내용'에서 피드백을 한눈에 확인할 수 있어요. 답안을 초기화하고 처음부터 다시 풀고 싶다면 다음의 버튼을 누르세요.")
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
    if re.search(r'(쉬운|노력|필요 없는)', a1): fb["q1"].append("✅ (1) 정답")
    else: fb["q1"].append("❌ (1) 오답: '비교적 쉬운 과제' 등의 의미가 들어가야 합니다.")
    if re.search(r'(혼자|집중|차분)', a2): fb["q1"].append("✅ (2) 정답")
    else: fb["q1"].append("❌ (2) 오답: '차분하게 혼자 집중하는 시간'이 들어가야 합니다.")
    if re.search(r'(억제)', a3): fb["q1"].append("✅ (3) 정답")
    else: fb["q1"].append("❌ (3) 오답: '사회적 억제'가 들어가야 합니다.")
    
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
    if re.search(r'(고여|높은)', a1): fb["q1"].append("✅ (1) 정답")
    else: fb["q1"].append("❌ (1) 오답: '고여 있는 물'에 비유해야 합니다.")
    if re.search(r'(이동하지|머물러|정지)', a2): fb["q1"].append("✅ (2) 정답")
    else: fb["q1"].append("❌ (2) 오답: 전하가 이동하지 않고 머물러 있다는 내용이 필요합니다.")
    if re.search(r'(위험하지 않|피해|없)', a3): fb["q1"].append("✅ (3) 정답")
    else: fb["q1"].append("❌ (3) 오답: 감전 등의 위험이 없다는 내용이 필요합니다.")
    
    if re.search(r'(고인|호수|잔잔|댐)', vis): fb["q3"].append("✅ Ⓐ 시각: 정전기의 특성을 시각적으로 잘 표현했습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 잔잔하게 고여 있는 물의 이미지가 필요합니다.")
    if re.search(r'(이동|머물|안전|위험하지)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 지문을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 전하가 이동하지 않아 안전하다는 근거가 포함되어야 합니다.")
    
    if re.search(r'(조용|고요|잔잔|바람)', aud): fb["q3"].append("✅ Ⓑ 청각: 고요한 특성을 잘 표현했습니다.")
    else: fb["q3"].append("△ Ⓑ 청각: 폭포 소리와 대비되는 고요한 소리가 좋습니다.")
    if re.search(r'(위험하지|이동하지|머물)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 지문을 근거로 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 본문 근거를 바탕으로 서술해야 합니다.")
    return fb

def grade_set3(a1, a2, a3, q2_1, q2_2, vis, vis_eff, aud, aud_eff):
    fb = {"q1": [], "q2": grade_q2(q2_1, q2_2), "q3": []}
    if re.search(r'(로봇|기계)', a1) and re.search(r'(실수|완벽|피겨)', a1): fb["q1"].append("✅ (1) 정답")
    else: fb["q1"].append("❌ (1) 오답: '로봇이 완벽하게 피겨 스케이팅을 해내는 것'이 필요합니다.")
    if re.search(r'(감정|철학|이야기)', a2) and re.search(r'(없|어렵|아니)', a2): fb["q1"].append("✅ (2) 정답")
    else: fb["q1"].append("❌ (2) 오답: 감정이나 철학이 없어 예술로 보기 어렵다는 내용이 들어가야 합니다.")
    if re.search(r'(미술계|변화|범주|확장|상징적)', a3): fb["q1"].append("✅ (3) 정답")
    else: fb["q1"].append("❌ (3) 오답: 미술계 변화나 예술의 범주 확장이라는 가치가 명시되어야 합니다.")
    
    if re.search(r'(인간|선수|땀|노력|열정|고뇌)', vis): fb["q3"].append("✅ Ⓐ 시각: 인간의 열정이 잘 설정되었습니다.")
    else: fb["q3"].append("△ Ⓐ 시각: 인간 선수의 노력과 열정이 드러나는 장면이 좋습니다.")
    if re.search(r'(감동|울림|감정|철학|경험)', vis_eff): fb["q3"].append("✅ Ⓐ 효과: 본문에 근거하여 효과를 잘 서술했습니다.")
    else: fb["q3"].append("❌ Ⓐ 효과: 윗글의 내용(마음을 울림 등)을 근거로 제시해야 합니다.")
    
    if re.search(r'(환호|박수|심장|오케스트라|감동|숨)', aud): fb["q3"].append("✅ Ⓑ 청각: 감동과 열정을 주는 소리가 잘 설정되었습니다.")
    else: fb["q3"].append("△ Ⓑ 청각: 기계음과 대조되는 감동적인 소리인지 확인해 보세요.")
    if re.search(r'(울림|감동|감정|열정|노력)', aud_eff): fb["q3"].append("✅ Ⓑ 효과: 본문 내용과 잘 연결했습니다.")
    else: fb["q3"].append("❌ Ⓑ 효과: 윗글의 내용(마음을 울림 등)이 근거로 드러나야 합니다.")
    return fb

# --- 공통 조건 텍스트 ---
cond_q2 = "<ul style='margin-bottom: 0;'><li>🎯 주어진 문장에 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것.</li><li>🎯 (1)과 (2)에는 서로 다른 설명 방법이 1가지 이상 활용되어야 하며, 각 문장에 사용된 설명 방법의 명칭을 괄호에 넣어 문장 끝에 기재할 것.</li><li>🎯 윗글에 제시된 내용만을 활용하여 문장을 구성할 것. (외부 지식 활용 시 오답)</li><li>🎯 (1)과 (2)가 논리적 흐름을 갖고 이어지도록 할 것.</li></ul>"

cond_q3 = "<ul style='margin-bottom: 0;'><li>🎯 윗글을 바탕으로 특성이 잘 드러나도록 Ⓐ와 Ⓑ에 들어갈 연출 계획을 세울 것.</li><li>🎯 자신이 설정한 시각/청각 요소가 글의 내용을 전달하는 데 어떤 효과가 있는지 각각 서술할 것.</li><li>🎯 효과를 기술할 때에는 윗글에 제시된 근거를 반드시 포함할 것.</li></ul>"

# --- 탭 구성 ---
tab1, tab2, tab3, tab4 = st.tabs(["문제 1", "문제 2", "문제 3", "📚 복습할 내용"])

# 탭 1 (사회적 촉진과 억제)
with tab1:
    st.subheader("💡 [실전 적용 1] 과제 난이도와 사회적 촉진/억제", anchor=False)
    
    draw_blue_box("""
    [기자] 심리학 용어인 '사회적 촉진'과 '사회적 억제'를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?<br><br>
    [전문가] 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?<br><br>
    [기자] 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?<br><br>
    [전문가] 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. 평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어서 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.<br><br>
    [기자] 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?<br><br>
    [전문가] 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.
    """)

    with st.form("form_set1"):
        st.markdown("[서·논술형 1] 윗글을 요약하여 표로 정리하였다. 빈칸 ㉠~㉢에 들어갈 내용을 찾아 쓰시오.")
        
        # --- HTML 표 ---
        st.markdown("""
        <table style="width:100%; text-align:center; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background-color:#e2e8f0;">
                <th style="padding:15px; border: 1px solid #cbd5e1;">과제의 특성</th>
                <th style="padding:15px; border: 1px solid #cbd5e1;">효율적인 환경 및 방법</th>
                <th style="padding:15px; border: 1px solid #cbd5e1;">관련된 심리 현상</th>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉠</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">커피숍, 도서관 등에서 하거나 모임을 만들어 다른 사람들과 함께 함</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">사회적 촉진</td>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">지나치게 어렵거나<br>도전이 필요한 과제</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉡</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉢</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        # --- 답안 작성란 ---
        s1_a1 = st.text_input("(1) ㉠ 특성 (사회적 촉진):", placeholder="내용을 입력하세요.")
        s1_a2 = st.text_input("(2) ㉡ 효율적인 환경 및 방법 (어려운 과제):", placeholder="내용을 입력하세요.")
        s1_a3 = st.text_input("(3) ㉢ 관련된 심리 현상 (어려운 과제):", placeholder="내용을 입력하세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 2] 윗글을 활용하여 '과제 난이도에 따른 효율적인 학습 전략'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
        draw_gray_box(cond_q2)
        st.markdown("<span style='color: gray; font-size: 14px;'>* 첫 문장: 과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.</span>", unsafe_allow_html=True)
        s1_q2_1 = st.text_area("(1) 첫 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        s1_q2_2 = st.text_area("(2) 두 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 3] 윗글을 바탕으로 '상황에 맞는 학습 공간 선택법'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        st.markdown("<span style='color: gray; font-size: 14px;'>* [장면 2] 어려운 과제를 할 때</span>", unsafe_allow_html=True)
        s1_vis = st.text_area("(1) Ⓐ 시각 요소:", height=68, placeholder="어떤 화면을 보여줄 것인가요?")
        s1_vis_eff = st.text_area("(2) Ⓐ 시각 효과:", height=100, placeholder="지문의 내용을 근거로 효과를 상세히 적어주세요.")
        s1_aud = st.text_area("(3) Ⓑ 청각 요소:", height=68, placeholder="어떤 소리를 들려줄 것인가요?")
        s1_aud_eff = st.text_area("(4) Ⓑ 청각 효과:", height=100, placeholder="지문의 내용을 근거로 효과를 상세히 적어주세요.")
        
        if st.form_submit_button("1세트 제출 및 채점하기"):
            st.session_state.feedback['set1'] = grade_set1(s1_a1, s1_a2, s1_a3, s1_q2_1, s1_q2_2, s1_vis, s1_vis_eff, s1_aud, s1_aud_eff)
            st.session_state.completed['set1'] = True
            st.success("채점이 완료되었습니다. 마지막 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 2 (정전기)
with tab2:
    st.subheader("💡 [실전 적용 2] 전압은 높지만 위험하지 않은 정전기", anchor=False)
    
    draw_blue_box("""
    [기자] 겨울철 불청객인 '정전기'란 정확히 무엇인지 설명 부탁드립니다.<br><br>
    [전문가] 정전기란 전하가 정지 상태로 있어 그 분포가 시간적으로 변화하지 않는 전기, 그리고 그로 인한 전기 현상을 말합니다. 쉽게 설명하면 흐르지 않고 머물러 있는 전기라고 해서 "움직이지 아니하여 조용하다."는 뜻을 가진 한자 '정(靜)'을 써서 정전기라고 부르는 것이죠.<br><br>
    [기자] 우리가 실생활에서 쓰는 전기와는 어떻게 다른가요? 물에 비유해서 설명해 주시면 이해가 쉬울 것 같습니다.<br><br>
    [전문가] 아주 좋은 비유가 될 수 있습니다. 우리가 실생활에서 쓰는 전기가 '흐르는 물'이라면, 정전기는 '높은 곳에 고여 있는 물'이라고 할 수 있습니다.<br><br>
    [기자] 정전기가 일어날 때 찌릿한 느낌이 드는데, 혹시 위험하지는 않은가요?<br><br>
    [전문가] 정전기의 전압은 매우 높지만, 우리가 실생활에서 쓰는 전기와는 다르게 전하가 이동하지 않고 머물러 있어 위험하지는 않습니다. 어마어마하게 높은 곳에 고여 있는 물이지만 떨어지지 않고 있어서 별 피해가 없는 것과 같다고 이해하시면 됩니다.
    """)

    with st.form("form_set2"):
        st.markdown("[서·논술형 1] 윗글을 요약하여 표로 정리하였다. 빈칸 ㉠~㉢에 들어갈 내용을 찾아 쓰시오.")
        
        # --- HTML 표 ---
        st.markdown("""
        <table style="width:100%; text-align:center; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background-color:#e2e8f0;">
                <th style="padding:15px; border: 1px solid #cbd5e1; width:20%;">대상</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:25%;">물의 상태에 비유</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:25%;">전하의 상태</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:30%;">위험성</th>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">실생활 전기</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">흐르는 물</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">전하가 이동함</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">감전 등의 위험이 있음</td>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">정전기</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉠</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉡</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉢</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        # --- 답안 작성란 ---
        s2_a1 = st.text_input("(1) ㉠ 물의 상태에 비유:", placeholder="내용을 입력하세요.")
        s2_a2 = st.text_input("(2) ㉡ 전하의 상태:", placeholder="내용을 입력하세요.")
        s2_a3 = st.text_input("(3) ㉢ 위험성:", placeholder="내용을 입력하세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 2] 윗글을 활용하여 '정전기의 특징'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
        draw_gray_box(cond_q2)
        st.markdown("<span style='color: gray; font-size: 14px;'>* 첫 문장: 겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.</span>", unsafe_allow_html=True)
        s2_q2_1 = st.text_area("(1) 첫 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        s2_q2_2 = st.text_area("(2) 두 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 3] 윗글을 바탕으로 '정전기의 특징'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        st.markdown("<span style='color: gray; font-size: 14px;'>* [장면 2] 정전기 (고여 있는 물)</span>", unsafe_allow_html=True)
        s2_vis = st.text_area("(1) Ⓐ 시각 요소:", height=68)
        s2_vis_eff = st.text_area("(2) Ⓐ 시각 효과:", height=100)
        s2_aud = st.text_area("(3) Ⓑ 청각 요소:", height=68)
        s2_aud_eff = st.text_area("(4) Ⓑ 청각 효과:", height=100)
        
        if st.form_submit_button("2세트 제출 및 채점하기"):
            st.session_state.feedback['set2'] = grade_set2(s2_a1, s2_a2, s2_a3, s2_q2_1, s2_q2_2, s2_vis, s2_vis_eff, s2_aud, s2_aud_eff)
            st.session_state.completed['set2'] = True
            st.success("채점이 완료되었습니다. 마지막 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 3 (인공지능의 예술)
with tab3:
    st.subheader("💡 [실전 적용 3] 인공 지능이 그린 그림을 바라보는 시각", anchor=False)
    
    draw_blue_box("""
    [기자] 최근 생성형 인공 지능이 그린 그림이 미술계에서 큰 화제를 모으고 있습니다. 이 그림을 인간이 만든 예술 작품과 같다고 볼 수 있을까요?<br><br>
    [전문가] 올림픽 경기를 예로 들어 볼게요. 우리가 올림픽에 열광하는 이유는 선수들이 경기를 위해 기울인 노력이나 열정을 알기 때문입니다. 반면 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내더라도 우리의 마음을 울리지는 못하지요.<br><br>
    이처럼 인간의 작품에는 작가의 고유한 감정이나 철학, 그리고 작가가 살아온 삶의 경험, 세상을 바라보는 관점 같은 요소가 담겨 있으므로 예술로 볼 수 있습니다. 하지만 인공 지능은 감정도 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 이를 예술로 보기는 어렵습니다.<br><br>
    [기자] 그렇다면 인공 지능이 그린 그림은 가치가 전혀 없는 것인가요?<br><br>
    [전문가] 그렇지는 않습니다. 비록 인간과 같은 감정은 없더라도, 기존 미술계에 큰 변화를 가져왔다는 점에서 분명한 의미가 있습니다. 또한 앞으로 우리가 알고 있던 예술의 범주를 확장할 수 있다는 점에서 상징적인 가치를 지닙니다.
    """)

    with st.form("form_set3"):
        st.markdown("[서·논술형 1] 윗글을 요약하여 표로 정리하였다. 빈칸 ㉠~㉢에 들어갈 내용을 찾아 쓰시오.")
        
        # --- HTML 표 ---
        st.markdown("""
        <table style="width:100%; text-align:center; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="background-color:#e2e8f0;">
                <th style="padding:15px; border: 1px solid #cbd5e1; width:15%;">대상</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:25%;">올림픽 경기에 비유</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:35%;">예술로 볼 수 있는가<br>(근거 포함)</th>
                <th style="padding:15px; border: 1px solid #cbd5e1; width:25%;">예술로서의 가치</th>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">인간의 예술</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">인간 선수의 노력과<br>열정이 담긴 경기</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">작가의 경험, 관점, 환경이 담겨<br>있으므로 예술이다.</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">감상자에게<br>남다른 감동을 줌</td>
            </tr>
            <tr>
                <td style="padding:15px; border: 1px solid #cbd5e1;">인공 지능의 예술</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉠</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉡</td>
                <td style="padding:15px; border: 1px solid #cbd5e1;">㉢</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        # --- 답안 작성란 ---
        s3_a1 = st.text_input("(1) ㉠ 올림픽 경기에 비유:", placeholder="내용을 입력하세요.")
        s3_a2 = st.text_input("(2) ㉡ 예술로 볼 수 있는가 (근거 포함):", placeholder="내용을 입력하세요.")
        s3_a3 = st.text_input("(3) ㉢ 예술로서의 가치:", placeholder="내용을 입력하세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 2] 윗글을 활용하여 '인공 지능이 그린 그림을 바라보는 시각'에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 <조건>에 맞추어 작성하시오.")
        draw_gray_box(cond_q2)
        st.markdown("<span style='color: gray; font-size: 14px;'>* 첫 문장: 인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 생각해야 한다.</span>", unsafe_allow_html=True)
        s3_q2_1 = st.text_area("(1) 첫 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        s3_q2_2 = st.text_area("(2) 두 번째 문장:", height=68, placeholder="문장 끝에 (설명방법)을 적으세요.")
        
        st.markdown("---")
        st.markdown("[서·논술형 3] 윗글을 바탕으로 '인공 지능이 그린 그림을 바라보는 시각'을 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        st.markdown("<span style='color: gray; font-size: 14px;'>* [장면 2] 마음에 울림을 주는 진정한 예술</span>", unsafe_allow_html=True)
        s3_vis = st.text_area("(1) Ⓐ 시각 요소:", height=68)
        s3_vis_eff = st.text_area("(2) Ⓐ 시각 효과:", height=100)
        s3_aud = st.text_area("(3) Ⓑ 청각 요소:", height=68)
        s3_aud_eff = st.text_area("(4) Ⓑ 청각 효과:", height=100)
        
        if st.form_submit_button("3세트 제출 및 채점하기"):
            st.session_state.feedback['set3'] = grade_set3(s3_a1, s3_a2, s3_a3, s3_q2_1, s3_q2_2, s3_vis, s3_vis_eff, s3_aud, s3_aud_eff)
            st.session_state.completed['set3'] = True
            st.success("채점이 완료되었습니다. 마지막 탭에서 결과를 확인하세요!")
            st.rerun()

# 탭 4 (복습할 내용)
with tab4:
    st.subheader("📚 제출한 답안 피드백 모아보기", anchor=False)
    if completed_count == 0:
        st.info("아직 제출된 세트가 없습니다. 문제 탭에서 답안을 먼저 제출해 주세요!")
    else:
        sets = [
            ("실전 적용 1 (사회적 촉진과 억제)", "set1"), 
            ("실전 적용 2 (정전기)", "set2"), 
            ("실전 적용 3 (인공지능의 예술)", "set3")
        ]
        
        for title, key in sets:
            if st.session_state.completed[key]:
                with st.expander(f"📌 {title} 피드백 확인하기", expanded=True):
                    fb = st.session_state.feedback[key]
                    st.markdown("[문항 1]")
                    for msg in fb["q1"]: st.write(msg)
                    st.markdown("<br>[문항 2]", unsafe_allow_html=True)
                    for msg in fb["q2"]: st.write(msg)
                    st.markdown("<br>[문항 3]", unsafe_allow_html=True)
                    for msg in fb["q3"]: st.write(msg)
