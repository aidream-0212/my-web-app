"""장비별 상세 페이지: 주차와 장비를 고르면 그 장비의 가동률 · 합계 · 일별 추이."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
WEEKS = {"W44 (지난주)": "readiness_W44.csv", "W45 (이번 주)": "readiness_W45.csv"}


@st.cache_data
def load(name: str) -> pd.DataFrame:
    return calc.load_readiness(DATA / name)


st.title("🔍 장비별 상세")
st.info("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람 정보가 아닙니다.")

week = st.segmented_control("주차", list(WEEKS), default="W45 (이번 주)", key="eq_week")
week = week or "W45 (이번 주)"  # 선택을 풀면 이번 주로 본다
df = load(WEEKS[week])

by_eq = calc.rate_by_equipment(df)
labels = (by_eq["장비코드"] + " " + by_eq["장비명"]).tolist()
choice = st.selectbox("장비", labels, key="eq_code")
code = choice.split(" ", 1)[0]

row = by_eq[by_eq["장비코드"] == code].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("가동률", f"{row['가동률']:.1f}%")
c2.metric("가동시간 합계", f"{row['가동시간']:g}h")
c3.metric("계획시간 합계", f"{row['계획시간']:g}h")
st.caption("가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100 (정정 행 포함)")

rows = df[df["장비코드"] == code]

st.subheader("일별 계획 · 가동시간")
daily = rows.groupby("일자", as_index=False)[["계획시간", "가동시간"]].sum()
st.line_chart(daily, x="일자", y=["계획시간", "가동시간"], x_label="일자", y_label="시간 (h)",
              alt=f"{choice} {week} 일별 계획시간과 가동시간")

st.subheader("일별 기록")
st.dataframe(
    rows[["일자", "계획시간", "가동시간", "비고"]],
    hide_index=True,
    alt=f"{choice} {week} 일별 계획 · 가동시간 기록",
)
if (rows["가동시간"] < 0).any():
    st.caption("가동시간이 음수인 행은 정정 행입니다. 지우지 않고 합계에 포함합니다. 그래프는 같은 날짜를 합쳐 그립니다.")
