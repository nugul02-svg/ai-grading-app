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

    render_pair("Ⓐ 시각", vis_el, vis_eff, q3_
