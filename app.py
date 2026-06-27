import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="서·논술형 답안 작성 연습", layout="wide")

# --- Gemini API 설정 ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.warning("⚠️ Streamlit Secrets에 GEMINI_API_KEY를 설정해주세요.")
except Exception as e:
    st.error(f"API 설정 중 오류가 발생했습니다: {e}")

# --- 세션 상태 초기화 ---
# step: 각 세트별 현재 문항 (1, 2, 3)
# feedback: 각 세트 각 문항별 피드백
# completed: 각 세트 각 문항별 완료 여부
for key, default in [
    ('step', {'set1': 1, 'set2': 1, 'set3': 1}),
    ('feedback', {'set1': {1: None, 2: None, 3: None},
                  'set2': {1: None, 2: None, 3: None},
                  'set3': {1: None, 2: None, 3: None}}),
    ('completed', {'set1': {1: False, 2: False, 3: False},
                   'set2': {1: False, 2: False, 3: False},
                   'set3': {1: False, 2: False, 3: False}}),
    ('answers', {'set1': {}, 'set2': {}, 'set3': {}}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

# --- UI 컴포넌트 ---
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
            st.warning("💡 3번 문제 풀이 팁: 효과를 기술할 때는 윗글의 내용(근거)이 반드시 들어가야 합니다.")

def draw_blue_box(text):
    st.markdown(
        f"<div style='background-color:#e8f0fb; padding:20px; border-radius:8px; "
        f"color:#111111; margin-bottom:20px; line-height:1.8; font-size:15px;'>{text}</div>",
        unsafe_allow_html=True)

def draw_gray_box(text):
    st.markdown(
        f"<div style='background-color:#f5f5f5; padding:20px; border-radius:8px; "
        f"border-left:6px solid #a1a1aa; margin-bottom:20px; line-height:1.6; font-size:15px;'>"
        f"&lt;조건&gt;<br>{text}</div>",
        unsafe_allow_html=True)

def draw_blue_info_box(text):
    st.markdown(
        f"<div style='background-color:#e8f0fb; padding:16px 20px; border-radius:8px; "
        f"color:#111111; margin-bottom:16px; line-height:1.8; font-size:15px;'>{text}</div>",
        unsafe_allow_html=True)

def step_indicator(set_key, current, completed_dict):
    """문항 탐색 버튼 — 클릭하면 해당 문항으로 바로 이동"""
    labels = ["1번  빈칸 채우기", "2번  설명문 쓰기", "3번  영상 기획"]
    cols = st.columns(3)
    for i, (col, label) in enumerate(zip(cols, labels), start=1):
        with col:
            if i == current:
                # 현재 문항: 파란 박스로 강조, 버튼 아님
                st.markdown(
                    f"<div style='background:#1d6fc4; border-radius:8px; padding:11px; "
                    f"text-align:center; color:#fff; font-size:14px; font-weight:bold;'>"
                    f"✏️ {label}</div>",
                    unsafe_allow_html=True)
            elif completed_dict[i]:
                # 완료 문항: 초록 버튼, 클릭 가능
                if st.button(f"✅ {label}", key=f"step_{set_key}_{i}", use_container_width=True):
                    st.session_state.step[set_key] = i
                    st.rerun()
            else:
                # 미완료 문항: 회색 버튼, 클릭 가능
                if st.button(f"⬜ {label}", key=f"step_{set_key}_{i}", use_container_width=True):
                    st.session_state.step[set_key] = i
                    st.rerun()

# --- AI 채점 ---
def ask_gemini_grading(prompt_content):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt_content)
        return response.text
    except Exception as e:
        return f"❌ 채점 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요! (오류: {e})"

# --- 공통 조건 ---
cond_q2 = (
    "<ul style='margin-bottom:0;'>"
    "<li>🎯 주어진 문장에 이어지는 문장을 (1), (2)에 각각 하나씩 작성할 것.</li>"
    "<li>🎯 (1)과 (2)에는 서로 다른 설명 방법이 1가지 이상 활용되어야 하며, 각 문장에 사용된 설명 방법의 명칭을 괄호에 넣어 문장 끝에 기재할 것.</li>"
    "<li>🎯 윗글에 제시된 내용만을 활용하여 문장을 구성할 것. (외부 지식 활용 시 오답)</li>"
    "<li>🎯 (1)과 (2)가 논리적 흐름을 갖고 이어지도록 할 것.</li>"
    "</ul>"
)
cond_q3 = (
    "<ul style='margin-bottom:0;'>"
    "<li>🎯 윗글을 바탕으로 특성이 잘 드러나도록 Ⓐ와 Ⓑ에 들어갈 연출 계획을 세울 것.</li>"
    "<li>🎯 자신이 설정한 시각/청각 요소가 글의 내용을 전달하는 데 어떤 효과가 있는지 각각 서술할 것.</li>"
    "<li>🎯 효과를 기술할 때에는 윗글에 제시된 근거를 반드시 포함할 것.</li>"
    "</ul>"
)

# ══════════════════════════════════════════════════════
# 세트별 문항 렌더링 함수
# ══════════════════════════════════════════════════════

def render_set(set_key, passage_html, q1_table_html, q1_labels,
               q1_answer_keys, q1_correct,
               q2_first_sentence, q2_prompt_kwargs,
               q3_plan_html, q3_prompt_kwargs):
    """
    세트 공통 렌더링 함수.
    - set_key: 'set1' | 'set2' | 'set3'
    - passage_html: 지문 HTML
    - q1_*: 1번 문항 관련
    - q2_*: 2번 문항 관련
    - q3_*: 3번 문항 관련
    """
    current = st.session_state.step[set_key]
    completed = st.session_state.completed[set_key]

    # 지문 (항상 표시)
    draw_blue_box(passage_html)

    # 진행 상태 표시 (클릭 가능)
    step_indicator(set_key, current, completed)
    st.markdown("---")

    # ── 1번: 빈칸 채우기 ──────────────────────────────
    if current == 1:
        st.markdown("**[서·논술형 1]** 윗글을 요약하여 표로 정리하였다. 빈칸 ㉠~㉢에 들어갈 내용을 찾아 쓰시오.")
        st.markdown(q1_table_html, unsafe_allow_html=True)

        with st.form(f"form_{set_key}_q1"):
            inputs = {}
            for label, key in zip(q1_labels, q1_answer_keys):
                inputs[key] = st.text_input(label, placeholder="내용을 입력하세요.",
                                            value=st.session_state.answers[set_key].get(key, ""))
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key].update(inputs)
            with st.spinner("채점 중입니다..."):
                vals = [inputs[k] for k in q1_answer_keys]
                prompt = f"""
너는 다정하고 꼼꼼한 중학교 국어 교사야. 말투는 부드럽고 격려하는 구어체로 해줘.
[학생 답안] ㉠={vals[0]}, ㉡={vals[1]}, ㉢={vals[2]}
[정답 기준] {q1_correct}
각 빈칸별로 정오를 판단하고, 틀렸다면 무엇이 빠졌는지 친절하게 알려줘.
"""
                fb = ask_gemini_grading(prompt)
                st.session_state.feedback[set_key][1] = fb
                st.session_state.completed[set_key][1] = True
                st.rerun()

        if completed[1]:
            st.info("📊 AI 피드백")
            st.write(st.session_state.feedback[set_key][1])

    # ── 2번: 설명문 쓰기 ─────────────────────────────
    elif current == 2:
        st.markdown("**[서·논술형 2]** 윗글을 활용하여 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 &lt;조건&gt;에 맞추어 작성하시오.")
        draw_gray_box(cond_q2)
        draw_blue_info_box(f"첫 문장: {q2_first_sentence}")

        with st.form(f"form_{set_key}_q2"):
            a1 = st.text_area("(1) 첫 번째 문장:", height=80,
                               placeholder="문장 끝에 (설명방법)을 적으세요.",
                               value=st.session_state.answers[set_key].get('q2_1', ''))
            a2 = st.text_area("(2) 두 번째 문장:", height=80,
                               placeholder="문장 끝에 (설명방법)을 적으세요.",
                               value=st.session_state.answers[set_key].get('q2_2', ''))
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key]['q2_1'] = a1
            st.session_state.answers[set_key]['q2_2'] = a2
            with st.spinner("채점 중입니다..."):
                prompt = f"""
너는 다정하고 꼼꼼한 중학교 국어 교사야. 말투는 부드럽고 격려하는 구어체로 해줘.
[학생 답안] (1) {a1} / (2) {a2}
[채점 기준]
- 괄호 안에 서로 다른 설명 방법 명칭이 각각 표기되어 있어야 함.
- 지문에 제시된 내용만 활용해야 함 (외부 지식 사용 시 감점).
- (1)과 (2)가 논리적 흐름으로 이어져야 함.
- {q2_prompt_kwargs.get('extra_criteria', '')}
잘한 점과 보완할 점을 문장별로 구체적으로 알려줘.
"""
                fb = ask_gemini_grading(prompt)
                st.session_state.feedback[set_key][2] = fb
                st.session_state.completed[set_key][2] = True
                st.rerun()

        if completed[2]:
            st.info("📊 AI 피드백")
            st.write(st.session_state.feedback[set_key][2])

    # ── 3번: 영상 기획 ───────────────────────────────
    elif current == 3:
        st.markdown("**[서·논술형 3]** 윗글을 바탕으로 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        draw_blue_info_box(q3_plan_html)

        with st.form(f"form_{set_key}_q3"):
            vis = st.text_area("(1) Ⓐ 시각 요소 및 효과:", height=110,
                                placeholder="시각 요소를 쓰고, 지문의 내용을 근거로 효과를 함께 서술하세요.",
                                value=st.session_state.answers[set_key].get('q3_vis', ''))
            aud = st.text_area("(2) Ⓑ 청각 요소 및 효과:", height=110,
                                placeholder="청각 요소를 쓰고, 지문의 내용을 근거로 효과를 함께 서술하세요.",
                                value=st.session_state.answers[set_key].get('q3_aud', ''))
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key]['q3_vis'] = vis
            st.session_state.answers[set_key]['q3_aud'] = aud
            with st.spinner("채점 중입니다..."):
                prompt = f"""
너는 다정하고 꼼꼼한 중학교 국어 교사야. 말투는 부드럽고 격려하는 구어체로 해줘.
[학생 답안] 시각 요소 및 효과: {vis} / 청각 요소 및 효과: {aud}
[채점 기준]
- 시각/청각 요소가 지문의 핵심 내용을 반영해야 함.
- 효과 서술에 반드시 지문의 근거가 포함되어야 함.
- {q3_prompt_kwargs.get('extra_criteria', '')}
시각·청각 각각에 대해 잘한 점과 보완할 점을 알려줘.
"""
                fb = ask_gemini_grading(prompt)
                st.session_state.feedback[set_key][3] = fb
                st.session_state.completed[set_key][3] = True
                st.rerun()

        if completed[3]:
            st.info("📊 AI 피드백")
            st.write(st.session_state.feedback[set_key][3])

    # (문항 이동은 상단 버튼으로)


# ══════════════════════════════════════════════════════
# 상단 UI
# ══════════════════════════════════════════════════════
draw_side_guide()
st.title("✏️ [국어] 서·논술형 답안 작성 연습", anchor=False)
st.markdown("작성한 답안을 입력한 뒤 문제의 조건에 맞게 작성하였는지 확인하세요. 수업 시간에 배운 내용이 답안 작성의 초점이에요 😉")
st.markdown("---")

# 전체 완료 현황
total_done = sum(
    sum(st.session_state.completed[s].values())
    for s in ['set1', 'set2', 'set3']
)
st.markdown(f"✅ 완료된 문항: {total_done} / 9")
st.progress(total_done / 9)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("세트별 탭을 자유롭게 이동하면서, 각 세트 안에서 문항별로 즉각 피드백을 받을 수 있어요.")
with col2:
    if st.button("🔄 처음부터 다시 풀기", use_container_width=True):
        reset_all()
        st.rerun()

st.markdown("---")

# ══════════════════════════════════════════════════════
# 탭
# ══════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["🧠 사회적 촉진", "⚡ 정전기", "🎨 인공지능 예술", "📚 복습할 내용"])

# ── 탭 1: 사회적 촉진/억제 ────────────────────────────
with tab1:
    st.subheader("💡 [실전 적용 1] 과제 난이도와 사회적 촉진/억제", anchor=False)
    render_set(
        set_key='set1',
        passage_html=(
            "[기자] 심리학 용어인 '사회적 촉진'과 '사회적 억제'를 일상생활, 특히 우리의 학습에 어떻게 적용할 수 있을까요?<br><br>"
            "[전문가] 이 두 가지 개념을 알면 상황에 맞춰 유용하게 활용할 수 있습니다. 예를 들어, 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 어떨까요?<br><br>"
            "[기자] 음, 그냥 집에서 편하게 혼자 하는 게 집중이 잘되지 않을까요?<br><br>"
            "[전문가] 그렇지 않습니다. 오히려 집에서 혼자 하는 것보다는 커피숍이나 도서관에서 하는 것이 더 효율적일 수 있습니다. "
            "평소 친숙하고 좋아하는 과목이라면 공부 모임을 만들어서 다른 사람들과 함께 공부하는 것도 좋은 방법이죠.<br><br>"
            "[기자] 그렇다면 어렵고 복잡한 과제를 할 때는 어떻게 해야 하나요?<br><br>"
            "[전문가] 그럴 때는 반대입니다. 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다."
        ),
        q1_table_html=(
            "<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'>"
            "<tr style='background-color:#e2e8f0;'>"
            "<th style='padding:15px;border:1px solid #cbd5e1;'>과제의 특성</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;'>효율적인 환경 및 방법</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;'>관련된 심리 현상</th></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>커피숍, 도서관 등에서 하거나 모임을 만들어 다른 사람들과 함께 함</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>사회적 촉진</td></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>지나치게 어렵거나<br>도전이 필요한 과제</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>"
        ),
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"],
        q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 비교적 쉬운 과제/취미, ㉡ 차분하게 혼자 집중하는 시간을 가짐, ㉢ 사회적 억제",
        q2_first_sentence="과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.",
        q2_prompt_kwargs={'extra_criteria': '사회적 촉진/억제 개념이 지문 내용을 바탕으로 반영되어야 함.'},
        q3_plan_html=(
            "<b>[영상 기획안]</b><br>"
            "◦ 주제: 사회적 촉진과 억제를 활용한 스마트한 공부법<br><br>"
            "<b>[장면 1] 쉬운 과제를 할 때</b><br>"
            "◦ 시각 요소: 백색소음이 있는 밝은 도서관에서 친구들과 가볍게 미소 지으며 공부하는 학생들의 모습을 넓은 화면(풀샷)으로 보여줌.<br>"
            "◦ 청각 요소: 경쾌하고 리듬감 있는 배경음악과 함께 사람들의 가벼운 발소리와 책장 넘기는 소리를 깔아줌.<br><br>"
            "<b>[장면 2] 어려운 과제를 할 때</b><br>"
            "◦ 시각 요소: ( Ⓐ )<br>"
            "◦ 청각 요소: ( Ⓑ )"
        ),
        q3_prompt_kwargs={'extra_criteria': "'혼자 집중', '사회적 억제 방지' 등 지문의 핵심 내용이 효과 서술에 반영되어야 함."},
    )

# ── 탭 2: 정전기 ──────────────────────────────────────
with tab2:
    st.subheader("💡 [실전 적용 2] 전압은 높지만 위험하지 않은 정전기", anchor=False)
    render_set(
        set_key='set2',
        passage_html=(
            "[기자] 겨울철 불청객인 '정전기'란 정확히 무엇인지 설명 부탁드립니다.<br><br>"
            "[전문가] 정전기란 전하가 정지 상태로 있어 그 분포가 시간적으로 변화하지 않는 전기, 그리고 그로 인한 전기 현상을 말합니다. "
            "쉽게 설명하면 흐르지 않고 머물러 있는 전기라고 해서 '움직이지 아니하여 조용하다.'는 뜻을 가진 한자 '정(靜)'을 써서 정전기라고 부르는 것이죠.<br><br>"
            "[기자] 우리가 실생활에서 쓰는 전기와는 어떻게 다른가요? 물에 비유해서 설명해 주시면 이해가 쉬울 것 같습니다.<br><br>"
            "[전문가] 아주 좋은 비유가 될 수 있습니다. 우리가 실생활에서 쓰는 전기가 '흐르는 물'이라면, 정전기는 '높은 곳에 고여 있는 물'이라고 할 수 있습니다.<br><br>"
            "[기자] 정전기가 일어날 때 찌릿한 느낌이 드는데, 혹시 위험하지는 않은가요?<br><br>"
            "[전문가] 정전기의 전압은 매우 높지만, 우리가 실생활에서 쓰는 전기와는 다르게 전하가 이동하지 않고 머물러 있어 위험하지는 않습니다. "
            "어마어마하게 높은 곳에 고여 있는 물이지만 떨어지지 않고 있어서 별 피해가 없는 것과 같다고 이해하시면 됩니다."
        ),
        q1_table_html=(
            "<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'>"
            "<tr style='background-color:#e2e8f0;'>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:20%;'>대상</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:25%;'>물의 상태에 비유</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:25%;'>전하의 상태</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:30%;'>위험성</th></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>실생활 전기</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>흐르는 물</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>전하가 이동함</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>감전 등의 위험이 있음</td></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>정전기</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>"
        ),
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"],
        q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 높은 곳에 고여 있는 물, ㉡ 전하가 이동하지 않고 머물러 있음, ㉢ 위험하지 않음(별 피해가 없음)",
        q2_first_sentence="겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.",
        q2_prompt_kwargs={'extra_criteria': '정전기의 전하 정지 특성과 위험하지 않은 이유가 지문을 근거로 서술되어야 함.'},
        q3_plan_html=(
            "<b>[영상 기획안]</b><br>"
            "◦ 주제: 전압은 높지만 위험하지 않은 정전기의 비밀<br><br>"
            "<b>[장면 1] 실생활 전기 (흐르는 물)</b><br>"
            "◦ 시각 요소: 거대한 폭포수가 콸콸 쏟아져 내려오며 물레방아를 힘차게 돌리는 역동적인 그래픽을 보여줌.<br>"
            "◦ 청각 요소: 물이 거세게 부딪히는 웅장하고 큰 소리를 배경음으로 사용함.<br><br>"
            "<b>[장면 2] 정전기 (고여 있는 물)</b><br>"
            "◦ 시각 요소: ( Ⓐ )<br>"
            "◦ 청각 요소: ( Ⓑ )"
        ),
        q3_prompt_kwargs={'extra_criteria': "'전하가 이동하지 않고 고여 있는 성질', '별 피해가 없음' 등 지문의 내용이 효과에 반드시 포함되어야 함."},
    )

# ── 탭 3: 인공지능의 예술 ─────────────────────────────
with tab3:
    st.subheader("💡 [실전 적용 3] 인공 지능이 그린 그림을 바라보는 시각", anchor=False)
    render_set(
        set_key='set3',
        passage_html=(
            "[기자] 최근 생성형 인공 지능이 그린 그림이 미술계에서 큰 화제를 모으고 있습니다. 어떤 작품인지 소개해 주실 수 있을까요?<br><br>"
            "[전문가] 네, 대표적으로 「에드몽 드 벨라미」라는 작품이 있습니다. 이 작품은 14~20세기에 그려진 초상화 1만 5,000점을 토대로 알고리즘과 데이터를 사용해 그려졌습니다. "
            "뉴욕 크리스티 경매에서 최종 낙찰가 43만 2,000달러에 판매되어 큰 놀라움을 주었죠.<br><br>"
            "[기자] 그렇다면 이 그림을 인간이 만든 예술 작품과 같다고 볼 수 있을까요?<br><br>"
            "[전문가] 올림픽 경기를 예로 들어 볼게요. 우리가 올림픽에 열광하는 이유는 선수들이 경기를 위해 기울인 노력이나 열정을 알기 때문입니다. "
            "반면 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내더라도 우리의 마음을 울리지는 못하지요. "
            "이처럼 인간의 작품에는 작가의 고유한 감정이나 철학, 그리고 작가가 살아온 삶의 경험, 세상을 바라보는 관점, 그를 둘러싼 환경 같은 내외부적인 요소가 종합적으로 담겨 있으므로 예술로 볼 수 있습니다. "
            "하지만 인공 지능은 감정도 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 이를 예술로 보기는 어렵습니다.<br><br>"
            "[기자] 그렇다면 인공 지능이 그린 그림은 가치가 전혀 없는 것인가요?<br><br>"
            "[전문가] 그렇지는 않습니다. 비록 인간과 같은 감정은 없더라도, 기존 미술계에 큰 변화를 가져왔다는 점에서 분명한 의미가 있습니다. "
            "또한 앞으로 우리가 알고 있던 예술의 범주를 확장할 수 있다는 점에서 상징적인 가치를 지닙니다."
        ),
        q1_table_html=(
            "<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'>"
            "<tr style='background-color:#e2e8f0;'>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:15%;'>대상</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:25%;'>올림픽 경기에 비유</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:35%;'>예술로 볼 수 있는가<br>(근거 포함)</th>"
            "<th style='padding:15px;border:1px solid #cbd5e1;width:25%;'>예술로서의 가치</th></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>인간의 예술</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>인간 선수의 노력과<br>열정이 담긴 경기</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>작가의 경험, 관점, 환경이 담겨<br>있으므로 예술이다.</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>감상자에게<br>남다른 감동을 줌</td></tr>"
            "<tr><td style='padding:15px;border:1px solid #cbd5e1;'>인공 지능의 예술</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td>"
            "<td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>"
        ),
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"],
        q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 로봇이 실수 없이 완벽하게 피겨 스케이팅을 해내는 것, ㉡ 감정이나 철학/이야기가 없어 예술로 보기 어려움, ㉢ 미술계 변화 유발 및 예술 범주 확장이라는 상징적 가치",
        q2_first_sentence="인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 올바르게 생각해야 한다.",
        q2_prompt_kwargs={'extra_criteria': '인공 지능 예술의 한계와 가치가 모두 지문을 근거로 반영되어야 함.'},
        q3_plan_html=(
            "<b>[영상 기획안]</b><br>"
            "◦ 주제: 인간의 감정이 담긴 진정한 예술의 가치<br><br>"
            "<b>[장면 1] 감정이 없는 완벽한 기술</b><br>"
            "◦ 시각 요소: 로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 해내지만 우리의 마음을 울리지는 못하는 동영상을 보여줌.<br>"
            "◦ 청각 요소: 기계음이나 일정한 박자의 메트로놈 소리를 깔아 차갑고 정형화된 분위기를 조성함.<br><br>"
            "<b>[장면 2] 마음에 울림을 주는 진정한 예술</b><br>"
            "◦ 시각 요소: ( Ⓐ )<br>"
            "◦ 청각 요소: ( Ⓑ )"
        ),
        q3_prompt_kwargs={'extra_criteria': "'작가의 감정, 경험, 철학', '마음을 울리는 감동' 등 지문의 인간 예술 특성이 효과 서술에 포함되어야 함."},
    )

# ── 탭 4: 복습할 내용 ─────────────────────────────────
with tab4:
    st.subheader("📚 제출한 답안 피드백 모아보기", anchor=False)
    if total_done == 0:
        st.info("아직 제출된 문항이 없습니다. 각 세트 탭에서 문항을 풀어 주세요!")
    else:
        set_titles = {
            'set1': '실전 적용 1 (사회적 촉진과 억제)',
            'set2': '실전 적용 2 (정전기)',
            'set3': '실전 적용 3 (인공지능의 예술)',
        }
        q_titles = {1: '1번 빈칸 채우기', 2: '2번 설명문 쓰기', 3: '3번 영상 기획'}
        for set_key, set_title in set_titles.items():
            any_done = any(st.session_state.completed[set_key].values())
            if any_done:
                st.markdown(f"### 📌 {set_title}")
                for q_num, q_title in q_titles.items():
                    if st.session_state.completed[set_key][q_num]:
                        with st.expander(f"  └ {q_title} 피드백", expanded=True):
                            st.write(st.session_state.feedback[set_key][q_num])
                st.markdown("---")
