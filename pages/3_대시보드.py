import streamlit as st
import requests

st.set_page_config(page_title="대시보드", page_icon="📈", layout="wide")
st.title("📈 심의 현황 대시보드")

API_URL = "http://127.0.0.1:8000"

# 통계
try:
    stats = requests.get(f"{API_URL}/stats").json()
    reviews = requests.get(f"{API_URL}/reviews").json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("전체 심의", f"{stats['total']}건")
    with col2:
        st.metric("⏳ 미처리", f"{stats['pending']}건")
    with col3:
        st.metric("✅ 승인", f"{stats['approved']}건")
    with col4:
        st.metric("🔴 HIGH 위험", f"{stats['high_risk']}건")

    st.markdown("---")
    st.subheader("최근 심의 이력")

    risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "SAFE": "✅"}
    status_color = {"PENDING": "⏳", "APPROVED": "✅", "REJECTED": "❌"}

    for r in reviews.get("reviews", []):
        with st.expander(
            f"{risk_color.get(r['overall_risk'], '⚪')} [{r['overall_risk']}] "
            f"{r['content_type']} | {r['author']} | "
            f"{status_color.get(r['approved'], '⏳')} {r['approved']} | "
            f"{r['created_at'][:16]}"
        ):
            st.write(r.get("summary", ""))

except Exception as e:
    st.error(f"서버 연결 실패: {e}")
    st.info("FastAPI 서버가 실행 중인지 확인하세요")
