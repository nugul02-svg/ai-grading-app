import streamlit as st

st.set_page_config(page_title="서·논술형 답안 작성 연습", page_icon="💯", layout="wide")

# --- 세션 상태 초기화 ---
for key, default in [
    ('step', {'set1': 1, 'set2': 1, 'set3': 1}),
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
    labels = ["1번  빈칸 채우기", "2번  설명문 쓰기", "3번  영상 기획"]
    cols = st.columns(3)
    for i, (col, label) in enumerate(zip(cols, labels), start=1):
        with col:
            if i == current:
                st.markdown(
                    f"<div style='background:#1d6fc4; border-radius:8px; padding:11px; "
                    f"text-align:center; color:#fff; font-size:14px; font-weight:bold;'>"
                    f"✏️ {label}</div>",
                    unsafe_allow_html=True)
            elif completed_dict[i]:
                if st.button(f"✅ {label}", key=f"step_{set_key}_{i}", use_container_width=True):
                    st.session_state.step[set_key] = i
                    st.rerun()
            else:
                if st.button(f"⬜ {label}", key=f"step_{set_key}_{i}", use_container_width=True):
                    st.session_state.step[set_key] = i
                    st.rerun()

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
# [수정 1] import re 제거 — 공백 제거 방식으로 통일
# [수정 2] is_valid / is_valid_review를 루프 밖 모듈 수준 함수로 분리
# ══════════════════════════════════════════════════════

def is_valid(val, kws):
    """1번 채점: 공백 제거 후 키워드 포함 여부 + 최소 3글자"""
    val_clean = val.replace(" ", "")
    if len(val_clean) < 3:
        return False
    return any(kw.replace(" ", "") in val_clean for kw in kws)


def check_q2_issues(a1, a2, passage_keywords):
    """
    2번 채점 공통 로직.
    - 허용 설명방법 6가지만 인정
    - 괄호 표기 여부 확인
    - 중복 설명방법 감지
    - 외부 지식 감지
    - 공식 패턴 강요 없음 (형식보다 내용 우선)
    """
    issues = []
    # 허용된 설명방법 6가지만 인정
    VALID_METHODS = ['정의', '예시', '인과', '비교와대조', '분류와구분', '분석']
    METHOD_DISPLAY = {
        '정의': '정의', '예시': '예시', '인과': '인과',
        '비교와대조': '비교와 대조', '분류와구분': '분류와 구분', '분석': '분석'
    }

    a1_clean = a1.replace(" ", "")
    a2_clean = a2.replace(" ", "")
    combined_clean = a1_clean + a2_clean

    # 각 문장에서 허용된 설명방법 추출
    def extract_method(sent_clean):
        for m in VALID_METHODS:
            if m in sent_clean:
                return m
        return None

    m1 = extract_method(a1_clean)
    m2 = extract_method(a2_clean)

    # 괄호 표기 + 허용 설명방법 사용 여부 확인
    if m1 is None:
        # 혹시 허용되지 않은 명칭을 쓴 건지 확인
        has_any_bracket = '(' in a1 and ')' in a1
        if has_any_bracket:
            issues.append(
                "(1) 괄호 안에 쓴 설명 방법 명칭이 허용된 6가지(정의·예시·인과·비교와 대조·분류와 구분·분석)에 해당하지 않아요. "
                "정확한 명칭으로 다시 적어주세요."
            )
        else:
            issues.append("(1) 문장 끝에 사용한 설명 방법을 괄호로 표기하지 않았어요. 예: 문장 내용. (인과)")
    if m2 is None:
        has_any_bracket = '(' in a2 and ')' in a2
        if has_any_bracket:
            issues.append(
                "(2) 괄호 안에 쓴 설명 방법 명칭이 허용된 6가지(정의·예시·인과·비교와 대조·분류와 구분·분석)에 해당하지 않아요. "
                "정확한 명칭으로 다시 적어주세요."
            )
        else:
            issues.append("(2) 문장 끝에 사용한 설명 방법을 괄호로 표기하지 않았어요. 예: 문장 내용. (비교와 대조)")

    # 중복 설명방법 감지 (두 문장 모두 표기한 경우에만)
    if m1 and m2 and m1 == m2:
        issues.append(
            f"(1)과 (2) 모두 '{METHOD_DISPLAY[m1]}'을(를) 사용했어요. "
            f"두 문장에는 서로 다른 설명 방법이 쓰여야 합니다."
        )

    # 외부 지식 감지: 지문 키워드가 하나도 없으면 의심
    has_passage_kw = any(kw.replace(" ", "") in combined_clean for kw in passage_keywords)
    if not has_passage_kw:
        issues.append(
            "윗글에 제시된 내용을 활용하지 않은 것으로 보여요. "
            "지문의 핵심 표현을 문장에 포함해야 해요. (외부 지식 활용 시 오답)"
        )

    return issues


# ══════════════════════════════════════════════════════
# 피드백 렌더링 함수
# ══════════════════════════════════════════════════════

def _draw_checklist_feedback(checks, model_answer):
    st.markdown(
        "<div style='background:#fef2f2; border:1px solid #fca5a5; border-radius:8px; "
        "padding:14px 18px; margin-bottom:4px;'>"
        "<span style='color:#dc2626; font-weight:bold; font-size:15px;'>"
        "✖ 다음 조건을 확인하세요:</span></div>",
        unsafe_allow_html=True)
    for item in checks:
        st.markdown(
            f"<div style='display:flex; align-items:flex-start; gap:8px; "
            f"padding:8px 4px; border-bottom:1px solid #f0f0f0;'>"
            f"<span style='color:#f59e0b; font-size:16px; flex-shrink:0;'>⚠️</span>"
            f"<span style='font-size:14px; color:#374151; line-height:1.6;'>{item}</span>"
            f"</div>",
            unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    with st.expander("📖 모범 답안 보기"):
        st.markdown(model_answer)


def _draw_q2_feedback(examples, model_answer, a1, a2, passage_keywords, content_checks):
    """2번 피드백: 조건 오류 → 내용 정확성 → 예시 문장 순서로 표시"""
    issues = check_q2_issues(a1, a2, passage_keywords)

    # 조건 오류가 있으면 먼저 표시
    if issues:
        st.markdown(
            "<div style='background:#fef2f2; border:1px solid #fca5a5; border-radius:8px; "
            "padding:12px 16px; margin-bottom:4px;'>"
            "<span style='color:#dc2626; font-weight:bold;'>✖ 다음 조건을 확인하세요:</span></div>",
            unsafe_allow_html=True)
        for item in issues:
            st.markdown(
                f"<div style='display:flex; align-items:flex-start; gap:8px; "
                f"padding:8px 4px; border-bottom:1px solid #f0f0f0;'>"
                f"<span style='color:#f59e0b; flex-shrink:0;'>⚠️</span>"
                f"<span style='font-size:14px; color:#374151; line-height:1.6;'>{item}</span></div>",
                unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # 내용 정확성 채점: 학생 답안에 지문 정보가 실제로 담겼는지 확인
    combined = (a1 + a2).replace(" ", "")
    content_issues = []
    for check_kws, feedback_msg in content_checks:
        if not any(kw.replace(" ", "") in combined for kw in check_kws):
            content_issues.append(feedback_msg)

    if content_issues:
        st.markdown(
            "<div style='background:#fff7ed; border:1px solid #fed7aa; border-radius:8px; "
            "padding:12px 16px; margin-bottom:4px;'>"
            "<span style='color:#c2410c; font-weight:bold;'>📋 내용 정확성을 확인하세요:</span></div>",
            unsafe_allow_html=True)
        for item in content_issues:
            st.markdown(
                f"<div style='display:flex; align-items:flex-start; gap:8px; "
                f"padding:8px 4px; border-bottom:1px solid #f0f0f0;'>"
                f"<span style='color:#f59e0b; flex-shrink:0;'>⚠️</span>"
                f"<span style='font-size:14px; color:#374151; line-height:1.6;'>{item}</span></div>",
                unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # 예시 문장: 항상 표시 (조건/내용 오류 시 펼친 상태)
    has_any_issue = bool(issues) or bool(content_issues)
    with st.expander("📚 설명 방법별 예시 문장 보기", expanded=has_any_issue):
        st.markdown("설명 방법의 **표지어 부분**은 <b style='color:#dc2626;'>적색 볼드</b>로 표시했어요.", unsafe_allow_html=True)
        for method, ex in examples.items():
            st.markdown(
                f"<div style='margin-bottom:10px; padding:10px 14px; background:#f9fafb; "
                f"border-radius:6px; border-left:3px solid #3b82f6;'>"
                f"<span style='font-weight:700; color:#1d4ed8;'>[{method}]</span> {ex}</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# 세트별 문항 렌더링 함수
# ══════════════════════════════════════════════════════

def render_set(set_key, passage_html, q1_table_html, q1_labels,
               q1_answer_keys, q1_correct, q1_keywords, q1_hints,
               q2_first_sentence, q2_examples, q2_model, q2_passage_keywords, q2_content_checks,
               q3_plan_html, q3_checks, q3_model):
    current = st.session_state.step[set_key]
    completed = st.session_state.completed[set_key]

    draw_blue_box(passage_html)
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
            st.session_state.completed[set_key][1] = True
            st.rerun()

        if completed[1]:
            ans = st.session_state.answers[set_key]
            vals = [ans.get(k, '') for k in q1_answer_keys]
            results = [is_valid(val, kws) for val, kws in zip(vals, q1_keywords)]
            all_correct = all(results)
            labels = ['㉠', '㉡', '㉢']

            if all_correct:
                st.success("🎉 모두 정답이에요!")
            else:
                st.warning("✏️ 아쉬운 부분이 있어요. 아래 안내를 참고해 보완해 보세요!")

            for i, (label, val, matched) in enumerate(zip(labels, vals, results)):
                if matched:
                    st.markdown(
                        f"<div style='background:#f0fdf4; border-left:4px solid #22c55e; "
                        f"padding:10px 14px; border-radius:6px; margin:6px 0;'>"
                        f"✅ <b>{label}</b>: {val}</div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='background:#fef2f2; border-left:4px solid #ef4444; "
                        f"padding:10px 14px; border-radius:6px; margin:6px 0;'>"
                        f"❌ <b>{label}</b>: {val if val else '(미입력)'}<br>"
                        f"<span style='font-size:13px; color:#374151; margin-top:4px; display:block;'>"
                        f"📝 보완 방법: {q1_hints[i]}</span></div>",
                        unsafe_allow_html=True)

            with st.expander("📖 모범 답안 보기"):
                for hint in q1_correct.split(','):
                    st.markdown(f"- {hint.strip()}")

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
            st.session_state.completed[set_key][2] = True
            st.rerun()

        if completed[2]:
            _draw_q2_feedback(
                q2_examples, q2_model,
                st.session_state.answers[set_key].get('q2_1', ''),
                st.session_state.answers[set_key].get('q2_2', ''),
                q2_passage_keywords,
                q2_content_checks
            )

    # ── 3번: 영상 기획 ───────────────────────────────
    elif current == 3:
        st.markdown("**[서·논술형 3]** 윗글을 바탕으로 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        draw_blue_info_box(q3_plan_html)

        with st.form(f"form_{set_key}_q3"):
            st.markdown("**(1) Ⓐ 시각 요소**")
            vis_el = st.text_area("시각 요소:", height=68,
                placeholder="'~한 사진', '~한 이미지', '~한 그래픽' 등 구체적인 매체 형태로 작성하세요.",
                value=st.session_state.answers[set_key].get('q3_vis_el', ''),
                label_visibility="collapsed")
            st.markdown("<span style='font-size:13px; color:#6b7280;'>효과</span>", unsafe_allow_html=True)
            vis_eff = st.text_area("시각 효과:", height=80,
                placeholder="위 시각 요소가 지문의 어떤 내용을 전달하는 데 효과적인지 지문 근거와 함께 서술하세요.",
                value=st.session_state.answers[set_key].get('q3_vis_eff', ''),
                label_visibility="collapsed")
            st.markdown("---")
            st.markdown("**(2) Ⓑ 청각 요소**")
            aud_el = st.text_area("청각 요소:", height=68,
                placeholder="'~한 배경음악', '~하는 효과음' 등 구체적인 소리 형태로 작성하세요.",
                value=st.session_state.answers[set_key].get('q3_aud_el', ''),
                label_visibility="collapsed")
            st.markdown("<span style='font-size:13px; color:#6b7280;'>효과</span>", unsafe_allow_html=True)
            aud_eff = st.text_area("청각 효과:", height=80,
                placeholder="위 청각 요소가 지문의 어떤 내용을 전달하는 데 효과적인지 지문 근거와 함께 서술하세요.",
                value=st.session_state.answers[set_key].get('q3_aud_eff', ''),
                label_visibility="collapsed")
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key]['q3_vis_el']  = vis_el
            st.session_state.answers[set_key]['q3_vis_eff'] = vis_eff
            st.session_state.answers[set_key]['q3_aud_el']  = aud_el
            st.session_state.answers[set_key]['q3_aud_eff'] = aud_eff
            st.session_state.completed[set_key][3] = True
            st.rerun()

        if completed[3]:
            _draw_checklist_feedback(q3_checks, q3_model)


# ══════════════════════════════════════════════════════
# 상단 UI
# ══════════════════════════════════════════════════════
draw_side_guide()
st.title("✏️ [국어] 서·논술형 답안 작성 연습", anchor=False)
st.markdown("작성한 답안을 입력한 뒤 문제의 조건에 맞게 작성하였는지 확인하세요. 수업 시간에 배운 내용이 답안 작성의 초점이에요 😉")
st.markdown("---")

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
        q1_keywords=[['쉬운 과제', '쉬운 취미', '노력이 필요 없는', '비교적 쉬운'], ['혼자 집중', '차분하게 혼자', '혼자 하는 시간'], ['사회적 억제']],
        q1_hints=[
            "'쉽다', '취미' 처럼 단어만 쓰면 안 돼요. '비교적 쉬운 과제'처럼 의미가 통하는 구(절)로 작성하세요.",
            "'혼자'라고만 적으면 부족해요. 어떻게 혼자 해야 하는지('차분하게 혼자', '혼자 집중' 등) 명확히 적으세요.",
            "해당 심리 현상의 정확한 전체 용어인 '사회적 억제'를 모두 적어주세요."
        ],
        q2_first_sentence="과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.",
        q2_examples={
            "정의": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 '사회적 촉진'이나 '사회적 억제'의 정의가 직접 제시되지 않으므로 정의 방법을 적용하기 어렵습니다.</span>",
            "예시": "<b style='color:#dc2626;'>예를 들어</b>, 비교적 쉬운 과제라면 커피숍이나 도서관처럼 사람이 많은 공간에서 하거나 공부 모임을 만들어 함께하는 것이 학습 효율을 높일 수 있다. (예시)",
            "인과": "지나치게 어렵거나 도전이 필요한 과제는 타인의 존재가 수행을 방해하기 <b style='color:#dc2626;'>때문에</b> 차분하게 혼자 집중하는 시간을 갖는 것이 효율적이다. (인과)",
            "비교와 대조": "비교적 쉬운 과제는 여럿이 함께하는 환경이 효율적인 <b style='color:#dc2626;'>반면</b>, 지나치게 어렵거나 도전이 필요한 과제는 혼자 차분하게 집중하는 환경이 효율적이다. (비교와 대조)",
            "분석": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 과제나 학습 전략을 구성 요소로 나누어 설명하는 내용이 없으므로 분석 방법을 적용하기 어렵습니다.</span>",
            "분류와 구분": "과제는 <b style='color:#dc2626;'>난이도를 기준으로</b> 비교적 쉬운 과제와 지나치게 어려운 과제로 <b style='color:#dc2626;'>나뉘며</b>, 각각에 알맞은 학습 환경이 다르게 적용된다. (분류와 구분)"
        },
        q2_model=(
            "**(1) 비교적 쉬운 과제나 취미 활동을 할 때는 커피숍이나 도서관처럼 다른 사람이 있는 공간에서 하거나, "
            "공부 모임을 만들어 함께하는 것이 더 효율적이다. (예시)**\n\n"
            "**(2) 반면 지나치게 어렵거나 도전이 필요한 과제를 할 때는 익숙해질 때까지 차분하게 혼자 집중하는 "
            "시간을 갖는 것이 효율적인데, 이는 타인의 존재가 오히려 수행을 방해하는 사회적 억제 현상이 나타나기 "
            "때문이다. (인과)**"
        ),
        q2_passage_keywords=['커피숍', '도서관', '공부 모임', '사회적 촉진', '사회적 억제', '차분', '혼자', '어렵', '쉬운', '취미', '과제', '난이도'],
        q2_content_checks=[
            # (확인 키워드 목록, 미포함 시 피드백 메시지)
            (['쉬운과제','쉬운취미','비교적쉬운','노력이필요없는','쉬운과목'],
             "(1)·(2) 중 하나는 '비교적 쉬운 과제/취미'에 대한 내용을 담아야 해요. 지문은 쉬운 과제와 어려운 과제를 대비해서 설명하고 있어요."),
            (['사회적억제','사회적촉진'],
             "지문의 핵심 개념인 '사회적 촉진' 또는 '사회적 억제'가 문장에 포함되지 않았어요. 설명방법을 활용한 문장에도 지문의 핵심 개념이 드러나야 해요."),
        ],
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
        q3_checks=[
            "시각/청각 요소가 '어려운 과제 → 혼자 집중하는 차분한 환경'이라는 지문의 핵심 내용을 반영해야 합니다.",
            "효과 서술에 윗글의 근거(예: '사회적 억제', '혼자 집중해야 효율이 오름')가 구체적으로 포함되어야 합니다.",
            "'보기 좋다', '집중이 잘 된다'처럼 주관적 표현만 쓰면 오답입니다. 지문 근거와 연결해야 합니다.",
        ],
        q3_model=(
            "**(예시 답안)**\n\n"
            "Ⓐ 시각 요소: 창문이 없는 조용한 독서실에서 혼자 책상에 앉아 문제를 푸는 학생의 모습을 클로즈업으로 보여줌.\n"
            "효과: 지나치게 어렵거나 도전이 필요한 과제는 익숙해질 때까지 차분하게 혼자 집중해야 한다는 지문의 내용을 시각적으로 전달한다.\n\n"
            "Ⓑ 청각 요소: 시계 초침 소리만 들리는 고요한 배경음을 사용함.\n"
            "효과: 타인의 존재가 없는 조용한 환경에서 혼자 집중해야 학습 효율이 높아진다는 지문의 내용을 청각적으로 강조한다."
        ),
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
        q1_keywords=[['고여 있는 물', '고인 물'], ['이동하지 않', '머물러 있', '정지해 있'], ['위험하지 않', '피해가 없', '안전하']],
        q1_hints=[
            "'물'이나 '고여' 단독으로는 틀립니다. '높은 곳에 고여 있는 물'이라는 전체 비유 대상을 적어주세요.",
            "'이동', '정지' 단어만으로는 안 됩니다. '이동하지 않는다', '머물러 있다' 처럼 구체적인 서술형으로 쓰세요.",
            "단순히 '안전'이라고 쓰기보다 지문의 표현을 빌려 '위험하지 않다' 또는 '피해가 없다'로 정확히 서술하세요."
        ],
        q2_first_sentence="겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.",
        q2_examples={
            "정의": "정전기<b style='color:#dc2626;'>란</b> 전하가 정지 상태로 있어 흐르지 않고 머물러 있는 전기<b style='color:#dc2626;'>를 말한다</b>. (정의)",
            "예시": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 정전기의 구체적 사례를 나열하는 내용이 없으므로 예시 방법을 적용하기 어렵습니다.</span>",
            "인과": "정전기는 전하가 이동하지 않고 머물러 있기 <b style='color:#dc2626;'>때문에</b> 전압이 아무리 높아도 위험하지 않다. (인과)",
            "비교와 대조": "실생활 전기가 흐르는 물처럼 전하가 이동하는 <b style='color:#dc2626;'>반면</b>, 정전기는 높은 곳에 고여 있는 물처럼 전하가 이동하지 않고 머물러 있어 위험하지 않다. (비교와 대조)",
            "분석": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 정전기의 구성 요소를 나누어 설명하는 내용이 없으므로 분석 방법을 적용하기 어렵습니다.</span>",
            "분류와 구분": "전기는 전하의 이동 여부를 <b style='color:#dc2626;'>기준으로</b> 전하가 이동하는 실생활 전기와 전하가 머물러 있는 정전기로 <b style='color:#dc2626;'>나뉜다</b>. (분류와 구분)"
        },
        q2_model=(
            "**(1) 정전기란 전하가 정지 상태로 있어 흐르지 않고 머물러 있는 전기를 말한다. (정의)**\n\n"
            "**(2) 실생활 전기가 흐르는 물처럼 전하가 이동하는 반면, 정전기는 높은 곳에 고여 있는 물처럼 "
            "전하가 이동하지 않고 머물러 있어 전압이 높아도 위험하지 않다. (비교와 대조)**"
        ),
        q2_passage_keywords=['정전기', '전하', '흐르는 물', '고여', '이동', '머물', '위험', '전압', '실생활', '정(靜)'],
        q2_content_checks=[
            (['전하가이동','이동하지않','머물러있','정지','흐르지않'],
             "정전기의 핵심 특성인 '전하가 이동하지 않고 머물러 있음'이 문장에 드러나지 않았어요. 이것이 정전기를 설명하는 핵심 내용이에요."),
            (['위험하지않','피해가없','안전'],
             "정전기가 '위험하지 않다'는 내용이 빠져 있어요. 지문의 결론에 해당하는 중요한 정보예요."),
        ],
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
        q3_checks=[
            "시각/청각 요소가 '전하가 이동하지 않고 고여 있는 정전기의 성질'을 반영해야 합니다.",
            "효과 서술에 윗글의 근거(예: '떨어지지 않아 피해가 없음', '전하가 머물러 있음')가 포함되어야 합니다.",
            "'조용하다', '안정적이다'처럼 근거 없는 주관적 표현만 쓰면 오답입니다. 지문 내용과 연결해야 합니다.",
        ],
        q3_model=(
            "**(예시 답안)**\n\n"
            "Ⓐ 시각 요소: 높은 절벽 위에 잔잔하게 고여 있는 물이 전혀 움직이지 않는 모습을 정지된 화면으로 보여줌.\n"
            "효과: 정전기는 전하가 이동하지 않고 머물러 있어 아무리 높은 곳에 고여 있어도 떨어지지 않으면 피해가 없다는 지문의 내용을 시각적으로 전달한다.\n\n"
            "Ⓑ 청각 요소: 아무런 소리도 없는 완전한 무음 또는 매우 잔잔한 배경음을 사용함.\n"
            "효과: 전하가 이동하지 않고 정지해 있는 정전기의 특성을 청각적으로 표현하여, 전압은 높지만 위험하지 않다는 지문의 핵심 내용을 강조한다."
        ),
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
        q1_keywords=[['로봇이 완벽하게', '로봇이 실수 없이', '완벽한 기술'], ['감정이 없', '철학이 없', '이야기가 없', '예술로 보기 어렵'], ['미술계 변화', '범주 확장', '상징적 가치', '상징적 의미']],
        q1_hints=[
            "'로봇', '완벽' 등 단어만 나열하면 안 됩니다. '로봇이 완벽하게 피겨 스케이팅을 해내는 것'처럼 전체 비유의 내용을 적어야 해요.",
            "'감정', '철학' 만 적지 말고, '감정이나 철학이 없어 예술로 보기 어렵다'는 구(절) 단위로 작성하세요.",
            "'미술계 변화', '예술 범주 확장', '상징적 가치' 중 하나 이상의 구절이 반드시 포함되게 쓰세요."
        ],
        q2_first_sentence="인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 올바르게 생각해야 한다.",
        q2_examples={
            "정의": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 '예술'이나 '인공 지능'의 개념을 직접 정의하는 내용이 없으므로 정의 방법을 적용하기 어렵습니다.</span>",
            "예시": "인간 예술의 가치를 보여주는 사례로, <b style='color:#dc2626;'>예를 들어</b> 올림픽 선수가 기울인 노력과 열정이 담긴 경기는 보는 이의 마음을 울린다. (예시)",
            "인과": "인공 지능은 감정도 느끼지 못하고 독자적인 철학이나 이야기가 없기 <b style='color:#dc2626;'>때문에</b> 그 결과물을 예술로 보기 어렵다. (인과)",
            "비교와 대조": "인간의 작품에는 작가의 감정, 경험, 관점이 담겨 있어 감동을 주는 <b style='color:#dc2626;'>반면</b>, 인공 지능의 그림에는 감정이나 독자적인 철학이 없어 예술로 보기 어렵다. (비교와 대조)",
            "분석": "<span style='color:#1d6fc4; font-weight:bold;'>이 지문에서는 예술 작품의 구성 요소를 나누어 설명하는 내용이 없으므로 분석 방법을 적용하기 어렵습니다.</span>",
            "분류와 구분": "그림은 감정과 철학의 유무를 <b style='color:#dc2626;'>기준으로</b> 인간의 예술과 인공 지능의 창작물로 <b style='color:#dc2626;'>나뉘며</b>, 둘은 예술적 가치 면에서 다르게 평가된다. (분류와 구분)"
        },
        q2_model=(
            "**(1) 인간의 예술에는 작가의 고유한 감정, 철학, 삶의 경험, 세상을 바라보는 관점 등이 담겨 있지만, "
            "인공 지능의 그림에는 감정도 독자적인 철학도 없기 때문에 예술로 보기 어렵다. (비교와 대조)**\n\n"
            "**(2) 그러나 인공 지능이 그린 그림은 기존 미술계에 큰 변화를 가져왔다는 점과, 앞으로 예술의 범주를 "
            "확장할 수 있다는 점에서 상징적인 가치를 지닌다. (인과)**"
        ),
        q2_passage_keywords=['인공 지능', '감정', '철학', '경험', '관점', '예술', '올림픽', '열정', '노력', '마음', '변화', '범주', '확장', '상징', '가치'],
        q2_content_checks=[
            (['감정이없','철학이없','이야기가없','예술로보기어렵','감정도느끼지못','독자적인철학'],
             "인공 지능이 예술로 보기 어려운 이유(감정·철학·이야기가 없음)가 문장에 드러나지 않았어요. 지문의 핵심 근거예요."),
            (['미술계변화','범주확장','범주를확장','상징적가치','상징적의미'],
             "인공 지능 예술의 가치(미술계 변화, 예술 범주 확장, 상징적 가치) 중 하나 이상이 문장에 포함되어야 해요."),
        ],
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
        q3_checks=[
            "시각/청각 요소가 '작가의 감정, 경험, 철학이 담긴 인간 예술의 특성'을 반영해야 합니다.",
            "효과 서술에 윗글의 근거(예: '마음을 울리는 감동', '선수의 노력과 열정')가 포함되어야 합니다.",
            "'아름답다', '감동적이다'처럼 근거 없는 주관적 표현만 쓰면 오답입니다. 지문 내용과 연결해야 합니다.",
        ],
        q3_model=(
            "**(예시 답안)**\n\n"
            "Ⓐ 시각 요소: 올림픽 피겨 선수가 실수를 이겨내며 눈물을 흘리는 감동적인 장면을 클로즈업으로 보여줌.\n"
            "효과: 인간의 작품에는 작가의 고유한 감정, 삶의 경험, 세상을 바라보는 관점이 담겨 있어 감상자의 마음을 울린다는 지문의 내용을 시각적으로 전달한다.\n\n"
            "Ⓑ 청각 요소: 선수가 연기를 마쳤을 때 관중들이 함성을 지르고 박수를 치는 소리를 배경음으로 사용함.\n"
            "효과: 올림픽에 열광하는 이유가 선수들의 노력과 열정을 알기 때문이라는 지문의 내용을 청각적으로 강조하여, 인간 예술만이 줄 수 있는 감동을 부각한다."
        ),
    )

# ── 탭 4: 복습할 내용 ─────────────────────────────────
with tab4:
    st.subheader("📚 제출한 답안 모아보기", anchor=False)
    st.markdown("💬 막히는 내용이 있으면 선생님께 찾아와 여쭤보세요 :)")
    st.markdown("---")
    if total_done == 0:
        st.info("아직 제출된 문항이 없습니다. 각 세트 탭에서 문항을 풀어 주세요!")
    else:
        review_data = {
            'set1': {
                'title': '🧠 사회적 촉진과 억제',
                'q1_keywords': [['쉬운 과제', '쉬운 취미', '노력이 필요 없는', '비교적 쉬운'],
                                 ['혼자 집중', '차분하게 혼자', '혼자 하는 시간'],
                                 ['사회적 억제']],
                'q1_hints': [
                    "'쉽다', '취미' 처럼 단어만 쓰면 안 돼요. '비교적 쉬운 과제'처럼 의미가 통하는 구(절)로 작성하세요.",
                    "'혼자'라고만 적으면 부족해요. 어떻게 혼자 해야 하는지('차분하게 혼자', '혼자 집중' 등) 명확히 적으세요.",
                    "해당 심리 현상의 정확한 전체 용어인 '사회적 억제'를 모두 적어주세요."
                ],
                'q1_correct': ['㉠ 비교적 쉬운 과제/취미', '㉡ 차분하게 혼자 집중하는 시간을 가짐', '㉢ 사회적 억제'],
                'q2_passage_keywords': ['커피숍', '도서관', '공부 모임', '사회적 촉진', '사회적 억제', '차분', '혼자', '어렵', '쉬운', '취미', '과제', '난이도'],
                'q3_checks': [
                    "시각/청각 요소가 '어려운 과제 → 혼자 집중하는 차분한 환경'이라는 지문의 핵심 내용을 반영해야 합니다.",
                    "효과 서술에 윗글의 근거(예: '사회적 억제', '혼자 집중해야 효율이 오름')가 구체적으로 포함되어야 합니다.",
                    "'보기 좋다', '집중이 잘 된다'처럼 주관적 표현만 쓰면 오답입니다. 지문 근거와 연결해야 합니다.",
                ],
            },
            'set2': {
                'title': '⚡ 정전기',
                'q1_keywords': [['고여 있는 물', '고인 물'],
                                 ['이동하지 않', '머물러 있', '정지해 있'],
                                 ['위험하지 않', '피해가 없', '안전하']],
                'q1_hints': [
                    "'물'이나 '고여' 단독으로는 틀립니다. '높은 곳에 고여 있는 물'이라는 전체 비유 대상을 적어주세요.",
                    "'이동', '정지' 단어만으로는 안 됩니다. '이동하지 않는다', '머물러 있다' 처럼 구체적인 서술형으로 쓰세요.",
                    "단순히 '안전'이라고 쓰기보다 지문의 표현을 빌려 '위험하지 않다' 또는 '피해가 없다'로 정확히 서술하세요."
                ],
                'q1_correct': ['㉠ 높은 곳에 고여 있는 물', '㉡ 전하가 이동하지 않고 머물러 있음', '㉢ 위험하지 않음(별 피해가 없음)'],
                'q2_passage_keywords': ['정전기', '전하', '흐르는 물', '고여', '이동', '머물', '위험', '전압', '실생활', '정(靜)'],
                'q3_checks': [
                    "시각/청각 요소가 '전하가 이동하지 않고 고여 있는 정전기의 성질'을 반영해야 합니다.",
                    "효과 서술에 윗글의 근거(예: '떨어지지 않아 피해가 없음', '전하가 머물러 있음')가 포함되어야 합니다.",
                    "'조용하다', '안정적이다'처럼 근거 없는 주관적 표현만 쓰면 오답입니다. 지문 내용과 연결해야 합니다.",
                ],
            },
            'set3': {
                'title': '🎨 인공지능의 예술',
                'q1_keywords': [['로봇이 완벽하게', '로봇이 실수 없이', '완벽한 기술'],
                                 ['감정이 없', '철학이 없', '이야기가 없', '예술로 보기 어렵'],
                                 ['미술계 변화', '범주 확장', '상징적 가치', '상징적 의미']],
                'q1_hints': [
                    "'로봇', '완벽' 등 단어만 나열하면 안 됩니다. '로봇이 완벽하게 피겨 스케이팅을 해내는 것'처럼 전체 비유의 내용을 적어야 해요.",
                    "'감정', '철학' 만 적지 말고, '감정이나 철학이 없어 예술로 보기 어렵다'는 구(절) 단위로 작성하세요.",
                    "'미술계 변화', '예술 범주 확장', '상징적 가치' 중 하나 이상의 구절이 반드시 포함되게 쓰세요."
                ],
                'q1_correct': ['㉠ 로봇이 실수 없이 완벽하게 피겨 스케이팅을 해내는 것', '㉡ 감정이나 철학/이야기가 없어 예술로 보기 어려움', '㉢ 미술계 변화 유발 및 예술 범주 확장이라는 상징적 가치'],
                'q2_passage_keywords': ['인공 지능', '감정', '철학', '경험', '관점', '예술', '올림픽', '열정', '노력', '마음', '변화', '범주', '확장', '상징', '가치'],
                'q3_checks': [
                    "시각/청각 요소가 '작가의 감정, 경험, 철학이 담긴 인간 예술의 특성'을 반영해야 합니다.",
                    "효과 서술에 윗글의 근거(예: '마음을 울리는 감동', '선수의 노력과 열정')가 포함되어야 합니다.",
                    "'아름답다', '감동적이다'처럼 근거 없는 주관적 표현만 쓰면 오답입니다. 지문 내용과 연결해야 합니다.",
                ],
            },
        }

        for set_key, rd in review_data.items():
            ans  = st.session_state.answers[set_key]
            comp = st.session_state.completed[set_key]
            if not any(comp.values()):
                continue

            st.markdown(f"### 📌 {rd['title']}")

            # ── 1번 복습 ──
            if comp[1]:
                vals = [ans.get(k, '') for k in ['q1_a', 'q1_b', 'q1_c']]
                # [수정 2] is_valid를 루프 밖 모듈 수준 함수로 호출
                results = [is_valid(v, kws) for v, kws in zip(vals, rd['q1_keywords'])]
                all_ok = all(results)
                labels = ['㉠', '㉡', '㉢']

                with st.expander(f"1번 빈칸 채우기 {'✅' if all_ok else '❌ 보완 필요'}", expanded=not all_ok):
                    for i, (label, val, matched) in enumerate(zip(labels, vals, results)):
                        if matched:
                            st.markdown(
                                f"<div style='background:#f0fdf4;border-left:4px solid #22c55e;"
                                f"padding:8px 12px;border-radius:6px;margin:4px 0;'>"
                                f"✅ <b>{label}</b>: {val}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f"<div style='background:#fef2f2;border-left:4px solid #ef4444;"
                                f"padding:8px 12px;border-radius:6px;margin:4px 0;'>"
                                f"❌ <b>{label}</b>: {val if val else '(미입력)'}<br>"
                                f"<span style='font-size:12px;color:#374151;'>📝 {rd['q1_hints'][i]}</span></div>",
                                unsafe_allow_html=True)
                    if not all_ok:
                        st.markdown("**모범 답안:**")
                        for c in rd['q1_correct']:
                            st.markdown(f"- {c}")

            # ── 2번 복습 ──
            if comp[2]:
                a1 = ans.get('q2_1', '')
                a2 = ans.get('q2_2', '')
                # [수정 4] 본 채점과 동일한 check_q2_issues 공통 함수 사용
                issues_2 = check_q2_issues(a1, a2, rd['q2_passage_keywords'])

                with st.expander(f"2번 설명문 쓰기 {'✅' if not issues_2 else '❌ 보완 필요'}", expanded=bool(issues_2)):
                    st.markdown(f"(1) {a1}")
                    st.markdown(f"(2) {a2}")
                    if issues_2:
                        st.markdown("**보완 필요:**")
                        for iss in issues_2:
                            st.markdown(f"⚠️ {iss}")

            # ── 3번 복습 ──
            if comp[3]:
                vis_el  = ans.get('q3_vis_el', '')
                vis_eff = ans.get('q3_vis_eff', '')
                aud_el  = ans.get('q3_aud_el', '')
                aud_eff = ans.get('q3_aud_eff', '')
                with st.expander("3번 영상 기획 — 체크리스트 확인", expanded=True):
                    st.markdown(f"**Ⓐ 시각 요소:** {vis_el}")
                    st.markdown(f"효과: {vis_eff}")
                    st.markdown(f"**Ⓑ 청각 요소:** {aud_el}")
                    st.markdown(f"효과: {aud_eff}")
                    st.markdown("**확인 사항:**")
                    for chk in rd['q3_checks']:
                        st.markdown(f"⚠️ {chk}")

            st.markdown("---")
