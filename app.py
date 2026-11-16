"""장비 가동률 · 정비 요청 앱의 뼈대 (여러 페이지).

- 페이지 목록은 아래 PAGES에서 관리한다. 페이지 파일은 pages/ 에 둔다.
- 시작할 때 db.init_db()를 한 번 부른다 (표가 없으면 만든다).
"""
import streamlit as st

import db

st.set_page_config(page_title="장비 가동률", page_icon="🛠️", layout="wide")


@st.cache_resource
def _init_db_once() -> None:
    db.init_db()


_init_db_once()

PAGES = [
    st.Page("pages/summary.py", title="요약", icon="📊", default=True),
    st.Page("pages/equipment.py", title="장비별 상세", icon="🔍"),
    st.Page("pages/weekly.py", title="주간 비교", icon="📈"),
    st.Page("pages/requests.py", title="정비 요청", icon="🔧"),
]

nav = st.navigation(PAGES)

with st.sidebar:
    st.caption("※ 교육용 가상 데이터입니다. 실제 부대 · 장비 · 사람 정보가 아닙니다.")

nav.run()
