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
# 채점 로직 함수들
# ══════════════════════════════════════════════════════

def is_valid(val, kws):
    val_clean = val.replace(" ", "")
    if len(val_clean) < 3:
        return False
    return any(kw.replace(" ", "") in val_clean for kw in kws)

def _draw_q3_feedback(ans, q3_grade):
    vis_el  = ans.get('q3_vis_el', '')
    vis_eff = ans.get('q3_vis_eff', '')
    aud_el  = ans.get('q3_aud_el', '')
    aud_eff = ans.get('q3_aud_eff', '')

    def grade_element(el):
        if not el.strip(): return False, "❌ 요소가 미입력되었습니다."
        return True, "✅ 창작 요소 확인"

    def grade_effect(eff, grade_cfg):
        if not eff.strip(): return False, "❌ 효과가 미입력되었습니다."
        eff_clean = eff.replace(" ", "")
        has_kw = any(kw.replace(" ", "") in eff_clean for kw in grade_cfg['eff_kws'])
        if not has_kw: return False, f"❌ {grade_cfg['eff_msg']}"
        return True, "✅ 지문 근거 포함 완료"

    def render_pair(label, el, eff, grade_cfg):
        el_ok, el_msg = grade_element(el)
        eff_ok, eff_msg = grade_effect(eff, grade_cfg)
        box_color = "#22c55e" if (el_ok and eff_ok) else "#ef4444"
        bg_color = "#f0fdf4" if (el_ok and eff_ok) else "#fef2f2"
        
        st.markdown(
            f"<div style='background:{bg_color}; border-left:4px solid {box_color}; padding:12px 16px; border-radius:6px; margin:6px 0;'>"
            f"<div style='margin-bottom:6px;'><b>{label} 요소:</b> {el if el else '(미입력)'} <span style='font-size:13px; color:{'#15803d' if el_ok else '#dc2626'}; margin-left:4px;'>{el_msg}</span></div>"
            f"<div><b>{label} 효과:</b> {eff if eff else '(미입력)'} <br><span style='font-size:13px; color:{'#15803d' if eff_ok else '#dc2626'};'>{eff_msg}</span></div>"
            f"</div>", unsafe_allow_html=True)

    render_pair("Ⓐ 시각", vis_el, vis_eff, q3_grade['vis'])
    render_pair("Ⓑ 청각", aud_el, aud_eff, q3_grade['aud'])
    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
    with st.expander("📖 모범 답안 보기"):
        st.markdown(q3_grade['model'])

def check_q2_issues(a1, a2, passage_keywords):
    issues = []
    VALID_METHODS = ['정의', '예시', '인과', '비교와대조', '분류와구분', '분석']
    METHOD_DISPLAY = {
        '정의': '정의', '예시': '예시', '인과': '인과',
        '비교와대조': '비교와 대조', '분류와구분': '분류와 구분', '분석': '분석'
    }

    a1_clean = a1.replace(" ", "")
    a2_clean = a2.replace(" ", "")
    combined_clean = a1_clean + a2_clean

    def extract_method(sent_clean):
        for m in VALID_METHODS:
            if m in sent_clean:
                return m
        return None

    m1 = extract_method(a1_clean)
    m2 = extract_method(a2_clean)

    if m1 is None:
        if '(' in a1 and ')' in a1:
            issues.append("(1) 괄호 안의 명칭이 허용된 6가지에 해당하지 않아요.")
        else:
            issues.append("(1) 문장 끝에 설명 방법을 괄호로 표기하지 않았어요.")
            
    if m2 is None:
        if '(' in a2 and ')' in a2:
            issues.append("(2) 괄호 안의 명칭이 허용된 6가지에 해당하지 않아요.")
        else:
            issues.append("(2) 문장 끝에 설명 방법을 괄호로 표기하지 않았어요.")

    if m1 and m2 and m1 == m2:
        issues.append(f"문장 (1)과 (2)에 같은 설명 방법 '{METHOD_DISPLAY[m1]}'이(가) 중복됐어요.")

    has_passage_kw = any(kw.replace(" ", "") in combined_clean for kw in passage_keywords)
    if not has_passage_kw:
        issues.append("지문에 없는 외부 지식이 사용된 것으로 보여요. 윗글의 단어나 내용을 활용해 주세요.")

    return issues

def _draw_q2_feedback(examples, model_answer, a1, a2, passage_keywords):
    issues = check_q2_issues(a1, a2, passage_keywords)

    def render_sent_result(label, sent, is_p1):
        if not sent.strip():
            st.markdown(f"<div style='background:#f5f5f5; border-left:4px solid #d1d5db; padding:10px 14px; border-radius:6px; margin:6px 0; color:#9ca3af;'><b>{label}</b> (미입력)</div>", unsafe_allow_html=True)
            return
        
        sent_issues = [iss for iss in issues if label in iss]
        if not is_p1 and "중복됐다" in "".join(issues): 
            sent_issues.append("문장 (1)과 (2)에 동일한 설명 방법이 중복 사용되었습니다.")
            
        def sent_has_any_kw(s, kws):
            sc = s.replace(" ", "")
            return any(kw.replace(" ", "") in sc for kw in kws)

        if not sent_issues and ("외부 지식" not in "".join(issues) or sent_has_any_kw(sent, passage_keywords)):
            st.markdown(f"<div style='background:#f0fdf4; border-left:4px solid #22c55e; padding:10px 14px; border-radius:6px; margin:6px 0;'>✅ <b>{label}</b>: {sent}</div>", unsafe_allow_html=True)
        else:
            display_issues = sent_issues if sent_issues else [iss for iss in issues if "외부 지식" in iss]
            prob_html = "".join(f"<div style='margin-top:6px; font-size:12px; color:#b45309;'>⚠️ {p}</div>" for p in display_issues)
            st.markdown(f"<div style='background:#fef2f2; border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; margin:6px 0;'>❌ <b>{label}</b>: {sent}{prob_html}</div>", unsafe_allow_html=True)

    render_sent_result("(1)", a1, is_p1=True)
    render_sent_result("(2)", a2, is_p1=False)
    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

    has_any_issue = bool(issues)
    with st.expander("📚 설명 방법별 예시 문장 보기", expanded=has_any_issue):
        st.markdown("설명 방법의 <b>표지어 부분</b>은 <b style='color:#dc2626;'>적색 볼드</b>로 표시했어요.", unsafe_allow_html=True)
        for method, ex in examples.items():
            st.markdown(f"<div style='margin-bottom:10px; padding:10px 14px; background:#f9fafb; border-radius:6px; border-left:3px solid #3b82f6;'><span style='font-weight:700; color:#1d4ed8;'>[{method}]</span> {ex}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# 세트별 문항 렌더링 함수
# ══════════════════════════════════════════════════════

def render_set(set_key, passage_html, q1_table_html, q1_labels,
               q1_answer_keys, q1_correct, q1_keywords, q1_hints,
               q2_first_sentence, q2_examples, q2_model, q2_passage_keywords,
               q3_plan_html, q3_grade):
    current = st.session_state.step[set_key]
    completed = st.session_state.completed[set_key]

    draw_blue_box(passage_html)
    step_indicator(set_key, current, completed)
    st.markdown("---")

    if current == 1:
        st.markdown("**[서·논술형 1]** 윗글을 요약하여 표로 정리하였다. 빈칸 ㉠~㉢에 들어갈 내용을 찾아 쓰시오.")
        st.markdown(q1_table_html, unsafe_allow_html=True)

        with st.form(f"form_{set_key}_q1"):
            inputs = {}
            for label, key in zip(q1_labels, q1_answer_keys):
                inputs[key] = st.text_input(label, placeholder="내용을 입력하세요.", value=st.session_state.answers[set_key].get(key, ""), key=f"text_input_{set_key}_{key}")
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

            if all_correct: st.success("🎉 모두 정답이에요!")
            else: st.warning("✏️ 아쉬운 부분이 있어요. 아래 안내를 참고해 보완해 보세요!")

            for i, (label, val, matched) in enumerate(zip(['㉠', '㉡', '㉢'], vals, results)):
                if matched:
                    st.markdown(f"<div style='background:#f0fdf4; border-left:4px solid #22c55e; padding:10px 14px; border-radius:6px; margin:6px 0;'>✅ <b>{label}</b>: {val}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:#fef2f2; border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; margin:6px 0;'>❌ <b>{label}</b>: {val if val else '(미입력)'}<br><span style='font-size:13px; color:#374151; display:block; margin-top:4px;'>📝 보완 방법: {q1_hints[i]}</span></div>", unsafe_allow_html=True)

            with st.expander("📖 모범 답안 보기"):
                for hint in q1_correct.split(','): st.markdown(f"- {hint.strip()}")

    elif current == 2:
        st.markdown("**[서·논술형 2]** 윗글을 활용하여 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용을 &lt;조건&gt;에 맞추어 작성하시오.")
        draw_gray_box(cond_q2)
        draw_blue_info_box(f"첫 문장: {q2_first_sentence}")

        with st.form(f"form_{set_key}_q2"):
            a1 = st.text_area("(1) 첫 번째 문장:", height=80, placeholder="문장 끝에 (설명방법)을 적으세요.", value=st.session_state.answers[set_key].get('q2_1', ''), key=f"q2_1_{set_key}")
            a2 = st.text_area("(2) 두 번째 문장:", height=80, placeholder="문장 끝에 (설명방법)을 적으세요.", value=st.session_state.answers[set_key].get('q2_2', ''), key=f"q2_2_{set_key}")
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key]['q2_1'] = a1
            st.session_state.answers[set_key]['q2_2'] = a2
            st.session_state.completed[set_key][2] = True
            st.rerun()

        if completed[2]:
            _draw_q2_feedback(q2_examples, q2_model, st.session_state.answers[set_key].get('q2_1', ''), st.session_state.answers[set_key].get('q2_2', ''), q2_passage_keywords)

    elif current == 3:
        st.markdown("**[서·논술형 3]** 윗글을 바탕으로 영상을 제작하려 한다. 다음 기획안을 보고 물음에 답하시오.")
        draw_gray_box(cond_q3)
        draw_blue_info_box(q3_plan_html)

        with st.form(f"form_{set_key}_q3"):
            st.markdown("**(1) Ⓐ 시각 요소**")
            vis_el = st.text_area("시각 요소:", height=68, placeholder="'~한 사진' 등 구체적인 매체 형태로 작성하세요.", value=st.session_state.answers[set_key].get('q3_vis_el', ''), label_visibility="collapsed", key=f"q3_vis_el_{set_key}")
            st.markdown("<span style='font-size:13px; color:#6b7280;'>효과</span>", unsafe_allow_html=True)
            vis_eff = st.text_area("시각 효과:", height=80, placeholder="지문 근거와 함께 서술하세요.", value=st.session_state.answers[set_key].get('q3_vis_eff', ''), label_visibility="collapsed", key=f"q3_vis_eff_{set_key}")
            st.markdown("---")
            st.markdown("**(2) Ⓑ 청각 요소**")
            aud_el = st.text_area("청각 요소:", height=68, placeholder="'~한 배경음악' 등 구체적인 소리 형태로 작성하세요.", value=st.session_state.answers[set_key].get('q3_aud_el', ''), label_visibility="collapsed", key=f"q3_aud_el_{set_key}")
            st.markdown("<span style='font-size:13px; color:#6b7280;'>효과</span>", unsafe_allow_html=True)
            aud_eff = st.text_area("청각 효과:", height=80, placeholder="지문 근거와 함께 서술하세요.", value=st.session_state.answers[set_key].get('q3_aud_eff', ''), label_visibility="collapsed", key=f"q3_aud_eff_{set_key}")
            submitted = st.form_submit_button("제출하고 피드백 받기")

        if submitted:
            st.session_state.answers[set_key]['q3_vis_el']  = vis_el
            st.session_state.answers[set_key]['q3_vis_eff'] = vis_eff
            st.session_state.answers[set_key]['q3_aud_el']  = aud_el
            st.session_state.answers[set_key]['q3_aud_eff'] = aud_eff
            st.session_state.completed[set_key][3] = True
            st.rerun()

        if completed[3]:
            _draw_q3_feedback(st.session_state.answers[set_key], q3_grade)

# ══════════════════════════════════════════════════════
# 메인 레이아웃 및 탭 실행
# ══════════════════════════════════════════════════════
draw_side_guide()

st.title("✏️ [국어] 서·논술형 답안 작성 연습", anchor=False)
st.markdown("작성한 답안을 입력한 뒤 문제의 조건에 맞게 작성하였는지 확인하세요. 😉")
st.markdown("---")

total_done = sum(sum(st.session_state.completed[s].values()) for s in ['set1', 'set2', 'set3'])
st.markdown(f"✅ 완료된 문항: {total_done} / 9")
st.progress(total_done / 9)

col1, col2 = st.columns([4, 1])
with col1: st.markdown("세트별 탭을 자유롭게 이동하면서, 각 세트 안에서 문항별로 즉각 피드백을 받을 수 있어요.")
with col2:
    if st.button("🔄 처음부터 다시 풀기", use_container_width=True):
        reset_all()
        st.rerun()

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🧠 사회적 촉진", "⚡ 정전기", "🎨 인공지능 예술", "📚 복습할 내용"])

with tab1:
    st.subheader("💡 [실전 적용 1] 과제 난이도와 사회적 촉진/억제", anchor=False)
    render_set(
        set_key='set1',
        passage_html="[기자] 사회적 촉진과 억제를 일상생활에 어떻게 적용할 수 있을까요?<br><br>[전문가] 비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제를 할 때는 커피숍이나 도서관에서 하거나 공부 모임을 만드는 것이 효율적일 수 있습니다. 반대로 지나치게 어렵거나 도전이 필요한 과제는 차분하게 혼자 집중하는 시간을 가지는 것이 좋습니다.",
        q1_table_html="<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'><tr style='background-color:#e2e8f0;'><th style='padding:15px;border:1px solid #cbd5e1;'>과제의 특성</th><th style='padding:15px;border:1px solid #cbd5e1;'>환경</th><th style='padding:15px;border:1px solid #cbd5e1;'>현상</th></tr><tr><td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td><td style='padding:15px;border:1px solid #cbd5e1;'>공부 모임 등 여럿이 함께함</td><td style='padding:15px;border:1px solid #cbd5e1;'>사회적 촉진</td></tr><tr><td style='padding:15px;border:1px solid #cbd5e1;'>어려운 과제</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>",
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"], q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 비교적 쉬운 과제/취미, ㉡ 차분하게 혼자 집중하는 시간을 가짐, ㉢ 사회적 억제",
        q1_keywords=[['쉬운 과제', '쉬운 취미', '노력이 필요 없는', '비교적 쉬운'], ['혼자 집중', '차분하게 혼자', '혼자 하는 시간'], ['사회적 억제']],
        # [수정] 의미 완성형 피드백 적용
        q1_hints=[
            "단답형으로 쓰면 의미가 부족해요. '비교적 쉬운 과제나 취미'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
            "단답형으로 쓰면 의미가 부족해요. '차분하게 혼자 집중'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
            "단어의 일부분만 쓰면 의미가 부족해요. '사회적 억제'라는 전체 용어를 명확하게 써주세요."
        ],
        q2_first_sentence="과제의 특성과 난이도에 따라 우리의 학습 효율을 높이는 방법은 다르게 적용되어야 한다.",
        q2_examples={
            "예시": "<b style='color:#dc2626;'>예를 들어</b>, 비교적 쉬운 과제라면 커피숍이나 도서관처럼 사람이 많은 공간에서 하는 것이 좋다. (예시)",
            "인과": "지나치게 어렵거나 도전이 필요한 과제는 방해받기 <b style='color:#dc2626;'>때문에</b> 혼자 집중하는 시간을 갖는 것이 효율적이다. (인과)",
            "비교와 대조": "쉬운 과제는 함께할 때 효율적인 <b style='color:#dc2626;'>반면</b>, 어려운 과제는 혼자 집중할 때 효율적이다. (비교와 대조)",
            "분류와 구분": "과제는 <b style='color:#dc2626;'>난이도를 기준으로</b> 쉬운 과제와 어려운 과제로 <b style='color:#dc2626;'>나뉜다</b>. (분류와 구분)"
        },
        q2_model="(1) 쉬운 과제는 함께(예시) (2) 어려운 과제는 혼자(인과)",
        q2_passage_keywords=['커피숍', '도서관', '공부 모임', '사회적 촉진', '사회적 억제', '차분', '혼자', '어렵', '쉬운', '취미', '과제', '난이도'],
        q3_plan_html="<b>[장면 2] 어려운 과제를 할 때</b><br>◦ 시각 요소: ( Ⓐ )<br>◦ 청각 요소: ( Ⓑ )",
        q3_grade={
            'vis': {'eff_kws': ['차분', '혼자', '사회적억제', '방해', '조용', '집중'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
            'aud': {'eff_kws': ['차분', '혼자', '사회적억제', '방해', '조용', '집중'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
            'model': "Ⓐ 독서실 혼자 공부하는 사진(효과: 혼자 집중해야 함 강조) / Ⓑ 무음(효과: 소음 차단)"
        }
    )

with tab2:
    st.subheader("💡 [실전 적용 2] 전압은 높지만 위험하지 않은 정전기", anchor=False)
    render_set(
        set_key='set2',
        passage_html="[기자] 정전기란 무엇인가요?<br><br>[전문가] 정전기란 전하가 정지 상태로 있어 그 분포가 변화하지 않고 흐르지 않는 전기를 말합니다. 우리가 쓰는 전기가 '흐르는 물'이라면, 정전기는 '높은 곳에 고여 있는 물'입니다. 정전기의 전압은 매우 높지만 전하가 이동하지 않고 머물러 있어 위험하지 않고 별 피해가 없습니다.",
        q1_table_html="<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'><tr style='background-color:#e2e8f0;'><th style='padding:15px;border:1px solid #cbd5e1;'>대상</th><th style='padding:15px;border:1px solid #cbd5e1;'>비유</th><th style='padding:15px;border:1px solid #cbd5e1;'>상태</th><th style='padding:15px;border:1px solid #cbd5e1;'>위험성</th></tr><tr><td style='padding:15px;border:1px solid #cbd5e1;'>정전기</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>",
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"], q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 높은 곳에 고여 있는 물, ㉡ 전하가 이동하지 않고 머물러 있음, ㉢ 위험하지 않음(별 피해가 없음)",
        q1_keywords=[['고여 있는 물', '고인 물', '고여있'], ['이동하지', '머물러', '정지해', '정지상태', '흐르지'], ['위험하지', '피해가없', '안전']],
        # [수정] 의미 완성형 피드백 적용
        q1_hints=[
            "단답형으로 쓰면 의미가 부족해요. '높은 곳에 고여 있는 물'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
            "단답형으로 쓰면 의미가 부족해요. '이동하지 않고 머물러 있다'처럼 의미가 완전하게 드러나도록 서술형으로 써주세요.",
            "단답형으로 쓰면 의미가 부족해요. 지문의 표현을 빌려 '위험하지 않다' 또는 '피해가 없다'처럼 완전한 의미로 서술해 주세요."
        ],
        q2_first_sentence="겨울철에 흔히 겪는 정전기는 우리가 평소 집에서 사용하는 전기와는 다른 뚜렷한 특징이 있다.",
        q2_examples={
            "정의": "정전기<b style='color:#dc2626;'>란</b> 전하가 정지 상태로 있어 흐르지 않는 전기<b style='color:#dc2626;'>를 말한다</b>. (정의)",
            "인과": "전하가 이동하지 않고 머물러 있기 <b style='color:#dc2626;'>때문에</b> 위험하지 않다. (인과)",
            "비교와 대조": "실생활 전기가 흐르는 물인 <b style='color:#dc2626;'>반면</b>, 정전기는 고여 있는 물과 같다. (비교와 대조)",
            "분류와 구분": "전기는 전하의 이동 여부를 <b style='color:#dc2626;'>기준으로</b> 실생활 전기와 정전기로 <b style='color:#dc2626;'>나뉜다</b>. (분류와 구분)"
        },
        q2_model="(1) 정전기 정의 (2) 고여있는 물 비유와 안전성 대조",
        q2_passage_keywords=['정전기', '전하', '흐르는 물', '고여', '이동', '머물', '위험', '전압', '실생활', '정(靜)', '조용', '피해', '현상', '정지상태'],
        q3_plan_html="<b>[장면 2] 정전기 (고여 있는 물)</b><br>◦ 시각 요소: ( Ⓐ )<br>◦ 청각 요소: ( Ⓑ )",
        q3_grade={
            'vis': {'eff_kws': ['이동하지않', '머물러', '피해가없', '떨어지지않', '위험하지', '고여있', '고인물', '정지', '전압', '흐르지', '조용하', '높은곳'], 'eff_msg': "지문의 표현을 근거로 효과를 서술해 주세요."},
            'aud': { 'eff_kws': ['이동하지않', '머물러', '피해가없', '떨어지지않', '위험하지', '고여있', '고인물', '정지', '전압', '흐르지', '조용하', '높은곳'], 'eff_msg': "지문의 표현을 근거로 효과를 서술해 주세요."},
            'model': "Ⓐ 댐에 갇혀 고인 물 그래픽 / Ⓑ 고요하고 잔잔한 음향 효과"
        }
    )

with tab3:
    st.subheader("💡 [실전 적용 3] 인공 지능이 그린 그림을 바라보는 시각", anchor=False)
    render_set(
        set_key='set3',
        passage_html="[기자] 생성형 인공지능이 그린 그림을 인간의 예술과 같다고 볼 수 있나요?<br><br>[전문가] 올림픽 경기를 예로 들면, 우리가 열광하는 이유는 선수들의 노력과 열정을 알기 때문입니다. 로봇이 실수 없이 완벽히 연기해도 울림을 주지 못하죠. 인간 작품에는 감정, 철학, 경험이 담겨 예술이지만 인공지능은 감정이 없고 철학이 없어 예술로 보기 어렵습니다. 그러나 미술계에 큰 변화를 주었고 예술 범주를 확장했다는 상징적 가치가 있습니다.",
        q1_table_html="<table style='width:100%;text-align:center;border-collapse:collapse;margin-bottom:20px;'><tr style='background-color:#e2e8f0;'><th style='padding:15px;border:1px solid #cbd5e1;'>대상</th><th style='padding:15px;border:1px solid #cbd5e1;'>비유</th><th style='padding:15px;border:1px solid #cbd5e1;'>예술인 이유</th><th style='padding:15px;border:1px solid #cbd5e1;'>가치</th></tr><tr><td style='padding:15px;border:1px solid #cbd5e1;'>인공지능</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉠</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉡</td><td style='padding:15px;border:1px solid #cbd5e1;'>㉢</td></tr></table>",
        q1_labels=["(1) ㉠:", "(2) ㉡:", "(3) ㉢:"], q1_answer_keys=['q1_a', 'q1_b', 'q1_c'],
        q1_correct="㉠ 로봇이 실수 없이 완벽하게 피겨 스케이팅을 해내는 것, ㉡ 감정이나 철학/이야기가 없어 예술로 보기 어려움, ㉢ 미술계 변화 유발 및 예술 범주 확장이라는 상징적 가치",
        q1_keywords=[['로봇이 완벽하게', '로봇이 실수 없이', '완벽한 기술'], ['감정이 없', '철학이 없', '이야기가 없', '예술로 보기 어렵'], ['미술계 변화', '범주 확장', '상징적 가치', '상징적 의미']],
        # [수정] 의미 완성형 피드백 적용
        q1_hints=[
            "단답형으로 쓰면 의미가 부족해요. '로봇이 완벽하게 피겨 스케이팅을 해내는 것'처럼 전체 비유의 내용을 이어서 써주세요.",
            "단답형으로 쓰면 의미가 부족해요. '감정이나 철학이 없어 예술로 보기 어렵다'처럼 완전한 의미로 서술해 주세요.",
            "단답형으로 쓰면 의미가 부족해요. '미술계 변화', '예술 범주 확장', '상징적 가치' 중 하나 이상의 의미가 완전하게 드러나도록 서술해 주세요."
        ],
        q2_first_sentence="인공 지능이 그린 그림이 늘어나는 요즘, 우리는 이 작품들을 어떤 눈으로 바라봐야 할지 올바르게 생각해야 한다.",
        q2_examples={
            "예시": "<b style='color:#dc2626;'>예를 들어</b> 올림픽 선수가 기울인 노력과 열정은 감동을 준다. (예시)",
            "인과": "인공지능은 감정과 철학이 없기 <b style='color:#dc2626;'>때문에</b> 예술로 보기 어렵다. (인과)",
            "비교와 대조": "인간은 감정을 담는 <b style='color:#dc2626;'>반면</b>, 인공지능은 감정이 없다. (비교와 대조)",
            "분류와 구분": "그림은 창작 주체를 <b style='color:#dc2626;'>기준으로</b> 인간의 예술과 인공지능 창작물로 <b style='color:#dc2626;'>나뉜다</b>. (분류와 구분)"
        },
        q2_model="(1) 인간과 AI의 감정 차이 대조 (2) 예술 범주 확장 가치 인과",
        q2_passage_keywords=['인공 지능', '감정', '철학', '경험', '관점', '예술', '올림픽', '열정', '노력', '마음', '변화', '범주', '확장', '상징', '가치', '로봇', '그림', '작품'],
        q3_plan_html="<b>[장면 2] 마음에 울림을 주는 진정한 예술</b><br>◦ 시각 요소: ( Ⓐ )<br>◦ 청각 요소: ( Ⓑ )",
        q3_grade={
            'vis': {'eff_kws': ['마음', '울리', '감정', '경험', '관점', '노력', '열정', '감동', '철학', '이야기'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
            'aud': {'eff_kws': ['마음', '울리', '감정', '경험', '관점', '노력', '열정', '감동', '열광', '호응', '환호'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
            'model': "Ⓐ 선수가 땀 흘리며 환희하는 사진 / Ⓑ 관객들의 우레와 같은 함성 소리"
        }
    )

with tab4:
    st.subheader("📚 제출한 답안 모아보기", anchor=False)
    st.markdown("💬 막히는 내용이 있으면 선생님께 찾아와 여쭤보세요 :)")
    st.markdown("---")
    
    # [복구 완료] 복습 탭에서 1, 2, 3번 문항 모두를 정상적으로 누적하여 보여주도록 수정했습니다.
    review_data = {
        'set1': {
            'title': '🧠 사회적 촉진과 억제',
            'q1_keywords': [['쉬운 과제', '쉬운 취미', '노력이 필요 없는', '비교적 쉬운'], ['혼자 집중', '차분하게 혼자', '혼자 하는 시간'], ['사회적 억제']],
            'q1_hints': [
                "단답형으로 쓰면 의미가 부족해요. '비교적 쉬운 과제나 취미'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
                "단답형으로 쓰면 의미가 부족해요. '차분하게 혼자 집중'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
                "단어의 일부분만 쓰면 의미가 부족해요. '사회적 억제'라는 전체 용어를 명확하게 써주세요."
            ],
            'q1_correct': ['㉠ 비교적 쉬운 과제/취미', '㉡ 차분하게 혼자 집중하는 시간을 가짐', '㉢ 사회적 억제'],
            'q2_passage_keywords': ['커피숍', '도서관', '공부 모임', '사회적 촉진', '사회적 억제', '차분', '혼자', '어렵', '쉬운', '취미', '과제', '난이도', '효율', '방해', '연습', '도전'],
            'q3_grade': {
                'vis': {'eff_kws': ['차분', '혼자', '사회적억제', '방해', '조용', '집중'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
                'aud': {'eff_kws': ['차분', '혼자', '사회적억제', '방해', '조용', '집중'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
                'model': "Ⓐ 독서실 혼자 공부하는 사진(효과: 혼자 집중해야 함 강조) / Ⓑ 무음(효과: 소음 차단)"
            }
        },
        'set2': {
            'title': '⚡ 정전기',
            'q1_keywords': [['고여 있는 물', '고인 물', '고여있'], ['이동하지', '머물러', '정지해', '정지상태', '흐르지'], ['위험하지', '피해가없', '안전']],
            'q1_hints': [
                "단답형으로 쓰면 의미가 부족해요. '높은 곳에 고여 있는 물'처럼 의미가 완전하게 드러나도록 이어서 써주세요.",
                "단답형으로 쓰면 의미가 부족해요. '이동하지 않고 머물러 있다'처럼 의미가 완전하게 드러나도록 서술형으로 써주세요.",
                "단답형으로 쓰면 의미가 부족해요. 지문의 표현을 빌려 '위험하지 않다' 또는 '피해가 없다'처럼 완전한 의미로 서술해 주세요."
            ],
            'q1_correct': ['㉠ 높은 곳에 고여 있는 물', '㉡ 전하가 이동하지 않고 머물러 있음', '㉢ 위험하지 않음(별 피해가 없음)'],
            'q2_passage_keywords': ['정전기', '전하', '흐르는 물', '고여', '이동', '머물', '위험', '전압', '실생활', '정(靜)', '조용', '피해', '현상', '정지상태'],
            'q3_grade': {
                'vis': {'eff_kws': ['이동하지않', '머물러', '피해가없', '떨어지지않', '위험하지', '고여있', '고인물', '정지', '전압', '흐르지', '조용하', '높은곳'], 'eff_msg': "지문의 표현을 근거로 효과를 서술해 주세요."},
                'aud': {'eff_kws': ['이동하지않', '머물러', '피해가없', '떨어지지않', '위험하지', '고여있', '고인물', '정지', '전압', '흐르지', '조용하', '높은곳'], 'eff_msg': "지문의 표현을 근거로 효과를 서술해 주세요."},
                'model': "Ⓐ 댐에 갇혀 고인 물 그래픽 / Ⓑ 고요하고 잔잔한 음향 효과"
            }
        },
        'set3': {
            'title': '🎨 인공지능의 예술',
            'q1_keywords': [['로봇이 완벽하게', '로봇이 실수 없이', '완벽한 기술'], ['감정이 없', '철학이 없', '이야기가 없', '예술로 보기 어렵'], ['미술계 변화', '범주 확장', '상징적 가치', '상징적 의미']],
            'q1_hints': [
                "단답형으로 쓰면 의미가 부족해요. '로봇이 완벽하게 피겨 스케이팅을 해내는 것'처럼 전체 비유의 내용을 이어서 써주세요.",
                "단답형으로 쓰면 의미가 부족해요. '감정이나 철학이 없어 예술로 보기 어렵다'처럼 완전한 의미로 서술해 주세요.",
                "단답형으로 쓰면 의미가 부족해요. '미술계 변화', '예술 범주 확장', '상징적 가치' 중 하나 이상의 의미가 완전하게 드러나도록 서술해 주세요."
            ],
            'q1_correct': ['㉠ 로봇이 실수 없이 완벽하게 피겨 스케이팅을 해내는 것', '㉡ 감정이나 철학/이야기가 없어 예술로 보기 어려움', '㉢ 미술계 변화 유발 및 예술 범주 확장이라는 상징적 가치'],
            'q2_passage_keywords': ['인공 지능', '감정', '철학', '경험', '관점', '예술', '올림픽', '열정', '노력', '마음', '변화', '범주', '확장', '상징', '가치', '로봇', '그림', '작품'],
            'q3_grade': {
                'vis': {'eff_kws': ['마음', '울리', '감정', '경험', '관점', '노력', '열정', '감동', '철학', '이야기'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
                'aud': {'eff_kws': ['마음', '울리', '감정', '경험', '관점', '노력', '열정', '감동', '열광', '호응', '환호'], 'eff_msg': "지문의 내용을 근거로 효과를 서술해 주세요."},
                'model': "Ⓐ 선수가 땀 흘리며 환희하는 사진 / Ⓑ 관객들의 우레와 같은 함성 소리"
            }
        }
    }

    if total_done == 0:
        st.info("아직 제출된 문항이 없습니다. 각 세트 탭에서 문항을 풀어 주세요!")
    else:
        for set_key, rd in review_data.items():
            ans  = st.session_state.answers.get(set_key, {})
            comp = st.session_state.completed.get(set_key, {})
            if not any(comp.values()):
                continue

            st.markdown(f"### 📌 {rd['title']}")

            # ── 1번 복습 ──
            if comp.get(1, False):
                vals = [ans.get(k, '') for k in ['q1_a', 'q1_b', 'q1_c']]
                results = [is_valid(v, rd['q1_keywords'][i]) for i, v in enumerate(vals)]
                all_ok = all(results)
                labels = ['㉠', '㉡', '㉢']

                with st.expander(f"1번 빈칸 채우기 {'✅' if all_ok else '❌ 보완 필요'}", expanded=not all_ok):
                    for i, (label, val, matched) in enumerate(zip(labels, vals, results)):
                        if matched:
                            st.markdown(f"<div style='background:#f0fdf4;border-left:4px solid #22c55e;padding:8px 12px;border-radius:6px;margin:4px 0;'>✅ <b>{label}</b>: {val}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='background:#fef2f2;border-left:4px solid #ef4444;padding:8px 12px;border-radius:6px;margin:4px 0;'>❌ <b>{label}</b>: {val if val else '(미입력)'}<br><span style='font-size:12px;color:#374151;'>📝 {rd['q1_hints'][i]}</span></div>", unsafe_allow_html=True)
                    if not all_ok:
                        st.markdown("**모범 답안:**")
                        for c in rd['q1_correct']:
                            st.markdown(f"- {c}")

            # ── 2번 복습 ──
            if comp.get(2, False):
                a1_rev = ans.get('q2_1', '')
                a2_rev = ans.get('q2_2', '')
                issues_rev = check_q2_issues(a1_rev, a2_rev, rd['q2_passage_keywords'])

                with st.expander(f"2번 설명문 쓰기 {'✅' if not issues_rev else '❌ 보완 필요'}", expanded=bool(issues_rev)):
                    st.markdown(f"(1) {a1_rev}")
                    st.markdown(f"(2) {a2_rev}")
                    if issues_rev:
                        st.markdown("**보완 필요:**")
                        for iss in issues_rev:
                            st.markdown(f"⚠️ {iss}")

            # ── 3번 복습 ──
            if comp.get(3, False):
                with st.expander("3번 영상 기획 피드백 확인", expanded=True):
                    _draw_q3_feedback(ans, rd['q3_grade'])

            st.markdown("---")
