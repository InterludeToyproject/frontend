import streamlit as st
import requests

st.set_page_config(page_title="대시보드", page_icon="📈", layout="wide")
st.title("📈 RegRadar 대시보드")

API_URL = "http://127.0.0.1:8000"

tab1, tab2 = st.tabs(["📈 심의 현황", "🛡️ 보안 모니터링"])

with tab1:
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

    st.markdown("---")
    st.subheader("🤖 규칙 자동 추출")
    st.caption("규제문서를 AI가 분석하여 심의 규칙을 자동으로 생성합니다")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("버튼을 누르면 7개 규제문서를 AI가 분석하여 새로운 심의 규칙을 자동 추출합니다")
    with col2:
        extract_btn = st.button(
            "🔍 규칙 자동 추출",
            type="primary",
            use_container_width=True,
            key="btn_extract"
        )

    if extract_btn:
        with st.spinner("규제문서 분석 중... (1~2분 소요)"):
            try:
                resp = requests.post(f"{API_URL}/extract-rules")
                extract_result = resp.json()
                st.success(f"✅ {extract_result.get('message')}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("전체 규칙", f"{extract_result.get('total_rules', 0)}개")
                with col2:
                    st.metric("신규 추출", f"{extract_result.get('newly_added', 0)}개")
                with col3:
                    dynamic = extract_result.get("dynamic_rules", {})
                    st.metric("동적 규칙", f"{dynamic.get('total', 0)}개")
            except Exception as e:
                st.error(f"실패: {e}")

with tab2:
    st.subheader("🛡️ 보안 모니터링")
    st.caption("프롬프트 인젝션 및 심의 시스템 무력화 시도를 실시간 탐지합니다")

    try:
        sec_resp = requests.get(f"{API_URL}/security/logs")
        sec_data = sec_resp.json()
        stats = sec_data.get("stats", {})
        logs = sec_data.get("logs", [])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("전체 보안 이벤트", f"{stats.get('total', 0)}건")
        with col2:
            st.metric("🔴 HIGH 위협", f"{stats.get('high', 0)}건")
        with col3:
            st.metric("🚫 차단 처리", f"{stats.get('blocked', 0)}건")

        st.markdown("---")
        st.subheader("📋 보안 이벤트 로그")

        if logs:
            threat_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            for log in logs:
                with st.expander(
                    f"{threat_color.get(log['threat_level'], '⚪')} "
                    f"[{log['threat_level']}] "
                    f"{'🚫 차단' if log['blocked'] else '⚠️ 경고'} | "
                    f"{log['created_at'][:16]}"
                ):
                    st.write(f"**탐지 내용:** {log['content_preview']}...")
                    st.write(f"**탐지 패턴:** {log['detected_patterns']}")
                    st.write(f"**처리:** {'차단' if log['blocked'] else '모니터링'}")
        else:
            st.success("✅ 보안 위협 탐지 없음")

    except Exception as e:
        st.error(f"서버 연결 실패: {e}")