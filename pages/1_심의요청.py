import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="심의 요청", page_icon="📝", layout="wide")
st.title("📝 콘텐츠 심의 요청")

API_URL = "http://127.0.0.1:8000"

if "content_input" not in st.session_state:
    st.session_state["content_input"] = ""

st.markdown("**테스트 예시:**")
col_a, col_b = st.columns(2)
with col_a:
    if st.button("❌ 위반 예시 불러오기", key="btn_bad"):
        st.session_state["content_input"] = "이 상품은 원금 보장되는 고수익 투자 상품입니다. 업계 최고의 수익률을 자랑하며 손실 위험이 전혀 없습니다. 지금만 가입 가능한 한정 특가 상품이니 지금 바로 신청하세요."
with col_b:
    if st.button("✅ 정상 예시 불러오기", key="btn_good"):
        st.session_state["content_input"] = "본 상품은 투자 원금 손실 가능성이 있습니다. 과거 수익률이 미래 수익을 보장하지 않습니다. 가입 전 상품 설명서를 반드시 확인하시기 바랍니다."

with st.form("review_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        content = st.text_area(
            "심의 대상 콘텐츠",
            value=st.session_state["content_input"],
            height=200,
            placeholder="심의할 마케팅 문구, 광고 문자, 공지사항 등을 입력하세요..."
        )
    with col2:
        content_type = st.selectbox(
            "콘텐츠 유형",
            ["마케팅문자", "이메일", "SNS게시물", "웹배너", "공지사항", "약관"]
        )
        author = st.text_input("작성자", placeholder="홍길동")
        submitted = st.form_submit_button(
            "🔍 심의 요청",
            use_container_width=True,
            type="primary"
        )

if submitted and content:
    with st.spinner("🤖 AI 심의 중..."):
        try:
            response = requests.post(
                f"{API_URL}/scan-content",
                json={
                    "content": content,
                    "content_type": content_type,
                    "author": author or "미입력"
                }
            )
            result = response.json()
            st.session_state["last_result"] = result
        except Exception as e:
            st.error(f"서버 연결 실패: {e}")

if "last_result" in st.session_state:
    result = st.session_state["last_result"]

    st.markdown("---")
    st.subheader("📊 심의 결과")

    risk = result.get("overall_risk", "UNKNOWN")
    risk_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "SAFE": "✅"}
    risk_label = {"HIGH": "즉시 수정 필요", "MEDIUM": "검토 필요", "LOW": "모니터링", "SAFE": "승인 가능"}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("위험도", f"{risk_color.get(risk, '⚪')} {risk}", risk_label.get(risk, ""))
    with col2:
        st.metric("Rule 탐지", f"{len(result.get('rule_violations', []))}건")
    with col3:
     st.metric("AI 탐지", f"{len(result.get('ai_violations', []))}건")
    with col4:
        confidence = result.get("confidence", 0)
        verified = result.get("verified", False)
        st.metric(
            "AI 신뢰도",
            f"{int(confidence * 100)}%",
            "✅ 검증완료" if verified else "⚠️ 재검토"
        )
    if result.get("pii_detected"):
        st.warning(f"⚠️ 개인정보 {len(result['pii_detected'])}건 탐지 → 자동 마스킹 처리됨")
        for pii in result["pii_detected"]:
            st.caption(f"  [{pii['type']}] {pii['original']}")

    st.info(f"📝 {result.get('summary', '')}")

    # 하이라이팅된 원문 표시
    st.subheader("🔍 위반 문구 하이라이팅")
    highlighted = result.get("highlighted_content", "")
    if highlighted:
        st.components.v1.html(
            f"""
            <div style="font-family:'맑은 고딕',sans-serif;">
                {highlighted}
            </div>
            """,
            height=300,
            scrolling=True
        )
    else:
        st.text(result.get("content", ""))
    
    st.subheader("⚠️ 위반 항목")
    tab1, tab2 = st.tabs(["Rule Engine 탐지", "AI 판단"])

    with tab1:
        rule_violations = result.get("rule_violations", [])
        if rule_violations:
            for v in rule_violations:
                severity_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                with st.expander(f"{severity_color.get(v['severity'], '⚪')} [{v['severity']}] {v['rule_name']}"):
                    st.write(f"**탐지 문구:** {v['flagged_text']}")
                    st.write(f"**근거 법령:** {v['law_reference']}")
        else:
            st.success("Rule Engine 탐지 없음")

    with tab2:
        ai_violations = result.get("ai_violations", [])
        if ai_violations:
            for v in ai_violations:
                severity_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                with st.expander(f"{severity_color.get(v.get('severity',''), '⚪')} [{v.get('severity','')}] {v.get('type','')}"):
                    st.write(f"**탐지 문구:** {v.get('flagged_text', '')}")
                    st.write(f"**근거 법령:** {v.get('law_reference', '')}")
        else:
            st.success("AI 탐지 없음")

    st.subheader("💡 수정 제안")
    for i, suggestion in enumerate(result.get("suggestions", []), 1):
        st.write(f"{i}. {suggestion}")

    with st.expander("📚 참조 법령 조문"):
        for ref in result.get("rag_references", []):
            st.caption(f"**{ref['law_name']}**")
            st.text(ref["content"])
            st.divider()

    st.markdown("---")
    st.subheader("✅ 심의 결정")
    review_id = result.get("review_id")
    col1, col2 = st.columns(2)
    with col1:
        reviewer = st.text_input("심의자 이름", key="reviewer")
        comment = st.text_area("의견", key="comment", height=80)
    with col2:
        st.write("")
        st.write("")
        if st.button("✅ 승인", use_container_width=True, type="primary", key="btn_approve"):
            if reviewer:
                requests.post(f"{API_URL}/approve", json={
                    "review_id": review_id,
                    "action": "approve",
                    "reviewer": reviewer,
                    "comment": comment
                })
                st.success("승인 완료")
            else:
                st.warning("심의자 이름을 입력하세요")
        if st.button("❌ 반려", use_container_width=True, key="btn_reject"):
            if reviewer:
                requests.post(f"{API_URL}/approve", json={
                    "review_id": review_id,
                    "action": "reject",
                    "reviewer": reviewer,
                    "comment": comment
                })
                st.error("반려 처리 완료")
            else:
                st.warning("심의자 이름을 입력하세요")
