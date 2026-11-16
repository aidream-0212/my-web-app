"""주간 비교 페이지: 지난주(W44) → 이번 주(W45) 장비별 가동률 증감과 비고 기록."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
PREV_FILE, CUR_FILE = "readiness_W44.csv", "readiness_W45.csv"

RATE_COLS = {
    "가동률_이전": st.column_config.NumberColumn("지난주 (%)", format="%.1f"),
    "가동률_이번": st.column_config.NumberColumn("이번 주 (%)", format="%.1f"),
    "증감": st.column_config.NumberColumn("증감 (%p)", format="%+.1f"),
}


@st.cache_data
def load(name: str) -> pd.DataFrame:
    return calc.load_readiness(DATA / name)


st.title("📈 주간 비교")
st.info("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람 정보가 아닙니다.")
st.caption("W44(지난주) → W45(이번 주) · 가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100 (정정 행 포함)")

prev, cur = load(PREV_FILE), load(CUR_FILE)
cmp = calc.compare_weeks(prev, cur)  # 증감이 큰 순서

up = cmp[cmp["증감"] > 0].head(3)
down = cmp[cmp["증감"] < 0].sort_values("증감").head(3)

left, right = st.columns(2)
with left:
    st.subheader("상승 상위 3")
    if up.empty:
        st.caption("가동률이 오른 장비가 없습니다.")
    else:
        st.dataframe(up, hide_index=True, column_config=RATE_COLS, alt="가동률이 가장 많이 오른 장비 3대")
with right:
    st.subheader("하락 상위 3")
    if down.empty:
        st.caption("가동률이 내린 장비가 없습니다.")
    else:
        st.dataframe(down, hide_index=True, column_config=RATE_COLS, alt="가동률이 가장 많이 내린 장비 3대")

st.subheader("전체 장비 (증감이 큰 순서)")
st.dataframe(cmp, hide_index=True, column_config=RATE_COLS, alt="장비 12대의 지난주 · 이번 주 가동률과 증감")

st.subheader("비고가 있는 기록")
notes = pd.concat([prev.assign(주차="W44"), cur.assign(주차="W45")], ignore_index=True)
notes = notes[notes["비고"].fillna("").astype(str).str.strip() != ""]
if notes.empty:
    st.caption("비고가 적힌 기록이 없습니다.")
else:
    st.dataframe(
        notes[["주차", "일자", "장비코드", "장비명", "계획시간", "가동시간", "비고"]],
        hide_index=True,
        alt="비고 칸에 글이 있는 일별 기록",
    )
