import streamlit as st

st.set_page_config(
    page_title="RegRadar",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ RegRadar")
st.subheader("JB금융그룹 준법심의 AI Agent")

st.markdown("""
---
### 서비스 소개
RegRadar는 금융 마케팅 콘텐츠의 준법 위반 여부를 AI로 자동 심의합니다.

| 기능 | 설명 |
|---|---|
| 📝 심의 요청 | 콘텐츠 입력 후 즉시 AI 심의 |
| 📊 규제 변경 | 최신 규제 반영 및 소급 탐지 |
| 📈 대시보드 | 전체 심의 현황 모니터링 |

---
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("오늘의 심의", "0건")
with col2:
    st.metric("미처리", "0건")
with col3:
    st.metric("HIGH 위험", "0건")
