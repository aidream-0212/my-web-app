"""정비 요청 페이지: 등록 · 목록(상태별) · 상태 변경. 저장 · 조회는 db.py 함수로만 한다."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc
import db

DATA = Path(__file__).resolve().parents[1] / "data"
EQUIP_FILE = "readiness_W45.csv"  # 장비 목록을 가져올 파일
ALL = "전체"
COLUMNS = {
    "id": "번호", "created_at": "등록 시각", "equipment_code": "장비코드", "장비명": "장비명",
    "title": "요청 내용", "priority": "우선순위", "requester_role": "요청자 역할", "status": "상태",
}


@st.cache_data
def equipment() -> dict[str, str]:
    """장비코드 → 장비명."""
    df = calc.load_readiness(DATA / EQUIP_FILE)
    eq = df[["장비코드", "장비명"]].drop_duplicates().sort_values("장비코드")
    return dict(zip(eq["장비코드"], eq["장비명"]))


EQUIP = equipment()

st.title("🔧 정비 요청")
st.info("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람 정보를 넣지 않습니다.")
st.caption(f"지금 저장소: **{db.backend_name()}**")

if msg := st.session_state.pop("req_msg", None):
    st.success(msg)

# ── 등록 ──────────────────────────────────────────────
st.subheader("요청 등록")
with st.form("req_form", clear_on_submit=True):
    code = st.selectbox("장비", list(EQUIP), format_func=lambda c: f"{c} {EQUIP[c]}")
    title = st.text_area("요청 내용", placeholder="예: 냉각 팬 소음 점검 요청")
    c1, c2 = st.columns(2)
    priority = c1.segmented_control("우선순위", db.PRIORITIES, default="보통")
    role = c2.text_input("요청자 역할명", placeholder="예: 정비 담당 (실명은 적지 않습니다)")
    submitted = st.form_submit_button("등록", type="primary")

if submitted:
    try:
        rid = db.add_request(code, title, priority or "", role)
    except ValueError as e:
        st.error(str(e))
    else:
        st.session_state["req_msg"] = f"{rid}번 요청을 '접수' 상태로 등록했습니다."
        st.rerun()

# ── 목록 ──────────────────────────────────────────────
st.subheader("요청 목록")
status = st.segmented_control("상태", [ALL, *db.STATUSES], default=ALL, key="req_filter") or ALL
reqs = db.list_requests(None if status == ALL else status)

if reqs.empty:
    st.caption("해당하는 요청이 없습니다.")
else:
    shown = reqs.assign(장비명=reqs["equipment_code"].map(EQUIP))[list(COLUMNS)].rename(columns=COLUMNS)
    st.dataframe(shown, hide_index=True, alt=f"정비 요청 목록 ({status})")

# ── 상태 변경 ─────────────────────────────────────────
st.subheader("상태 변경")
all_reqs = db.list_requests()
if all_reqs.empty:
    st.caption("등록된 요청이 없습니다.")
else:
    info = {int(r.id): f"{r.id}번 · {r.equipment_code} · {r.title} ({r.status})" for r in all_reqs.itertuples()}
    c1, c2, c3 = st.columns([3, 2, 1], vertical_alignment="bottom")
    rid = c1.selectbox("번호", list(info), format_func=info.get, key="req_id")
    new_status = c2.selectbox("바꿀 상태", db.STATUSES, key="req_new_status")
    if c3.button("변경", width="stretch"):
        db.update_status(rid, new_status)
        st.session_state["req_msg"] = f"{rid}번 요청을 '{new_status}' 상태로 바꿨습니다."
        st.rerun()
