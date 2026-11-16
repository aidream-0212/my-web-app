"""가동률 계산 함수 (AGENTS.md '고정 약속').

가동률 = 가동시간 합계 ÷ 계획시간 합계 × 100 (소수 첫째 자리).
일별 가동률의 평균을 쓰지 않고, 가동시간이 음수인 정정 행도 합계에 포함한다.
"""
from __future__ import annotations

import pandas as pd

PLAN, RUN = "계획시간", "가동시간"
KEYS = ["장비코드", "장비명"]


def _rate(run_sum, plan_sum):
    """합계 ÷ 합계 × 100. 계획시간 합계가 0이면 NaN."""
    if isinstance(plan_sum, pd.Series):
        return (run_sum / plan_sum.where(plan_sum != 0) * 100).round(1)
    return float("nan") if plan_sum == 0 else round(float(run_sum) / float(plan_sum) * 100, 1)


def load_readiness(path) -> pd.DataFrame:
    """CSV를 읽는다. 열 '계획시간(h)' · '가동시간(h)'는 '계획시간' · '가동시간'으로 바꾼다."""
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.rename(columns={"계획시간(h)": PLAN, "가동시간(h)": RUN})
    df[PLAN] = pd.to_numeric(df[PLAN])
    df[RUN] = pd.to_numeric(df[RUN])
    return df


def total_rate(df: pd.DataFrame) -> float:
    """전체 가동률(%), 소수 첫째 자리."""
    return float(_rate(df[RUN].sum(), df[PLAN].sum()))


def rate_by_equipment(df: pd.DataFrame) -> pd.DataFrame:
    """장비별 가동률. 열: 장비코드 · 장비명 · 계획시간 · 가동시간 · 가동률."""
    out = df.groupby(KEYS, as_index=False)[[PLAN, RUN]].sum()
    out["가동률"] = _rate(out[RUN], out[PLAN])
    return out[KEYS + [PLAN, RUN, "가동률"]]


def compare_weeks(prev: pd.DataFrame, cur: pd.DataFrame) -> pd.DataFrame:
    """두 주 장비별 가동률 비교. 열: 장비코드 · 장비명 · 가동률_이전 · 가동률_이번 · 증감 (증감이 큰 순서)."""
    p = rate_by_equipment(prev)[KEYS + ["가동률"]].rename(columns={"가동률": "가동률_이전"})
    c = rate_by_equipment(cur)[KEYS + ["가동률"]].rename(columns={"가동률": "가동률_이번"})
    out = p.merge(c, on=KEYS, how="outer")
    out["증감"] = (out["가동률_이번"] - out["가동률_이전"]).round(1)
    return out.sort_values("증감", ascending=False, na_position="last").reset_index(drop=True)
