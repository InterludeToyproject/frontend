import streamlit as st
import requests
import datetime

st.set_page_config(page_title="규제 변경", page_icon="📊", layout="wide")
st.title("📊 규제 변경 추적")
st.caption("최신 규제 업로드 시 기존 승인 콘텐츠를 자동으로 재검토합니다")

API_URL = "http://127.0.0.1:8000"

tab1, tab2 = st.tabs(["📤 규제 변경 업로드", "🔍 소급 위반 탐지"])

with tab1:
    st.subheader("신규/변경 규제 업로드")

    if "reg_text" not in st.session_state:
        st.session_state["reg_text"] = ""

    col1, col2 = st.columns([2, 1])

    with col1:
        regulation_name = st.selectbox(
            "규제 문서 선택",
            ["개인정보보호법", "개인정보보호법 시행령", "금융소비자보호법",
             "금융소비자보호법 시행령", "신용정보법", "전자금융감독규정", "기타 (직접 입력)"]
        )
        if regulation_name == "기타 (직접 입력)":
            regulation_name = st.text_input("규제명 직접 입력")

        regulation_text = st.text_area(
            "변경된 규제 내용 입력",
            value=st.session_state["reg_text"],
            height=250,
            placeholder="변경된 조문 내용을 붙여넣으세요..."
        )

    with col2:
        st.markdown("**변경 유형**")
        change_type = st.radio(
            "",
            ["신규 조항 추가", "기존 조항 개정", "조항 삭제", "해석 변경"],
            label_visibility="collapsed"
        )
        st.markdown("**시행일**")
        effective_date = st.date_input("", datetime.date.today())
        st.markdown("**영향도 예상**")
        impact_level = st.select_slider(
            "",
            options=["낮음", "보통", "높음", "매우높음"],
            value="보통",
            label_visibility="collapsed"
        )

    if st.button("📋 변경 예시 불러오기", key="btn_reg_example"):
        st.session_state["reg_text"] = """제17조(광고의 방법 및 절차)
① 금융상품판매업자등이 금융상품 광고를 하는 경우 다음 각 호의 사항을 포함하여야 한다.
1. 금융상품판매업자등의 명칭
2. 금융상품의 내용
3. 투자성 상품의 경우: 투자에 따른 위험 (원금손실 가능성 명시 의무화)
4. AI 생성 콘텐츠의 경우: AI 생성 여부 표시 의무 (신설)"""
        st.rerun()

    if st.button("🚀 규제 변경 등록 및 영향 분석", type="primary", key="btn_reg_submit"):
        if regulation_text:
            with st.spinner("규제 변경 분석 중..."):
                try:
                    response = requests.post(
                        f"{API_URL}/upload-regulation",
                        json={
                            "regulation_name": regulation_name,
                            "regulation_text": regulation_text
                        }
                    )
                    st.session_state["reg_result"] = response.json()
                except Exception as e:
                    st.error(f"서버 연결 실패: {e}")
        else:
            st.warning("규제 내용을 입력하세요")

    if "reg_result" in st.session_state:
        result = st.session_state["reg_result"]
        st.markdown("---")
        st.subheader("📋 변경 분석 결과")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("영향받은 콘텐츠", f"{result.get('affected_count', 0)}건")
        with col2:
            st.metric("즉시 수정 필요", f"{result.get('high_risk_count', 0)}건")
        with col3:
            st.metric("검토 필요", f"{result.get('medium_risk_count', 0)}건")

        st.info(f"📝 {result.get('summary', '')}")

        if result.get("affected_reviews"):
            st.subheader("⚠️ 영향받은 기존 콘텐츠")
            for review in result["affected_reviews"]:
                risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                with st.expander(
                    f"{risk_color.get(review.get('risk',''), '⚪')} "
                    f"[심의#{review.get('id','')}] "
                    f"{review.get('content_type','')} - "
                    f"{review.get('reason','')[:50]}"
                ):
                    st.write(f"**내용:** {review.get('content', '')[:200]}...")
                    st.write(f"**위반 이유:** {review.get('reason', '')}")
                    st.write(f"**권고:** {review.get('recommendation', '')}")

with tab2:
    st.subheader("기존 승인 콘텐츠 전체 재검토")
    st.caption("현재 적용된 규제 기준으로 기존 승인 콘텐츠를 다시 검토합니다")

    if "retro_result" not in st.session_state:
        st.session_state["retro_result"] = None

    col1, col2 = st.columns([2, 1])
    with col1:
        scan_query = st.text_input(
            "검토 기준 입력",
            placeholder="예: 원금보장 표현, AI 생성 콘텐츠 표시 의무..."
        )
    with col2:
        scan_type = st.selectbox(
            "검토 범위",
            ["전체 승인 콘텐츠", "최근 30일", "최근 90일", "마케팅문자만", "이메일만"]
        )

    if st.button("🔍 소급 위반 탐지 시작", type="primary", key="btn_retro_scan"):
        if scan_query:
            with st.spinner("기존 콘텐츠 재검토 중..."):
                try:
                    response = requests.post(
                        f"{API_URL}/retroactive-scan",
                        json={"query": scan_query, "scan_type": scan_type}
                    )
                    st.session_state["retro_result"] = response.json()
                except Exception as e:
                    st.error(f"서버 연결 실패: {e}")
        else:
            st.warning("검토 기준을 입력하세요")

    if st.session_state["retro_result"]:
        retro = st.session_state["retro_result"]
        st.markdown("---")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("검토 완료", f"{retro.get('total_scanned', 0)}건")
        with col2:
            st.metric("🔴 즉시 수정", f"{retro.get('high_count', 0)}건")
        with col3:
            st.metric("🟡 검토 필요", f"{retro.get('medium_count', 0)}건")

        if retro.get("flagged_reviews"):
            st.subheader("소급 위반 의심 콘텐츠")
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            sorted_reviews = sorted(
                retro["flagged_reviews"],
                key=lambda x: priority_order.get(x.get("risk", "LOW"), 2)
            )
            for review in sorted_reviews:
                risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                urgency = {"HIGH": "즉시 수정", "MEDIUM": "1주내 검토", "LOW": "모니터링"}
                with st.expander(
                    f"{risk_color.get(review.get('risk',''), '⚪')} "
                    f"[{urgency.get(review.get('risk',''), '')}] "
                    f"심의#{review.get('id','')} - "
                    f"{review.get('content_type', '')}"
                ):
                    st.write(f"**내용:** {review.get('content', '')[:200]}...")
                    st.write(f"**위반 이유:** {review.get('reason', '')}")
                    st.write(f"**권고사항:** {review.get('recommendation', '')}")
                    if st.button("재심의 요청", key=f"rescan_{review.get('id','')}"):
                        st.info("재심의 요청이 접수되었습니다")
        else:
            st.success("✅ 소급 위반 의심 콘텐츠 없음")
