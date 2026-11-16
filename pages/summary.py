"""요약 페이지: 이번 주 · 지난주 전체 가동률, 목표와의 차이, 장비별 이번 주 가동률."""
from pathlib import Path

import pandas as pd
import streamlit as st

import calc

DATA = Path(__file__).resolve().parents[1] / "data"
PREV_FILE, CUR_FILE = "readiness_W44.csv", "readiness_W45.csv"
TARGET = 90.0  # 목표 가동률(%)


@st.cache_data
def load(name: str) -> pd.DataFrame:
    return calc.load_readiness(DATA / name)


st.title("📊 가동률 요약")
st.info("교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람 정보가 아닙니다.")

prev, cur = load(PREV_FILE), load(CUR_FILE)
prev_rate, cur_rate = calc.total_rate(prev), calc.total_rate(cur)

c1, c2, c3 = st.columns(3)
c1.metric("이번 주 전체 가동률 (W45)", f"{cur_rate:.1f}%", f"{cur_rate - prev_rate:+.1f}%p")
c2.metric("지난주 전체 가동률 (W44)", f"{prev_rate:.1f}%")
c3.metric(f"목표 {TARGET:.0f}%와의 차이", f"{cur_rate - TARGET:+.1f}%p",
          "목표 달성" if cur_rate >= TARGET else "목표 미달",
          delta_color="normal" if cur_rate >= TARGET else "inverse")
st.caption("가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100 (정정 행 포함)")

st.subheader("장비별 이번 주 가동률 (W45)")
by_eq = calc.rate_by_equipment(cur)
by_eq["장비"] = by_eq["장비코드"] + " " + by_eq["장비명"]
st.bar_chart(by_eq, x="장비", y="가동률", horizontal=True, y_label="가동률 (%)", x_label="")
