import streamlit as st
from modules.DB import SupabaseDB
from datetime import datetime

def get_user_id():
    return st.session_state.get("id")

def chatbot_page2():
    from datetime import datetime
    today_date = datetime.now().strftime("%Y-%m-%d")
    st.title(f"📊 개인 포트폴리오 분석 리포트 - {today_date}")

    username = get_user_id()
    supabase = SupabaseDB()

    # DB에서 리포트 불러오기
    if "report_data" not in st.session_state:
        with st.spinner("📦 DB에서 리포트를 불러오는 중입니다..."):
            report = supabase.get_individual_report(username)
            if not report:
                st.error("❌ DB에 저장된 리포트가 없습니다. 관리자에게 문의하세요.")
                st.stop()
            st.session_state["report_data"] = report
    else:
        report = st.session_state["report_data"]

    # 섹션 순서 정의
    sections = [
        ("📋 요약", "summary"),
        ("📈 마이데이터 분석", "mydata"),
        ("👤 투자 성향 진단", "investment_style"),
        ("💰 재무 건전성 평가", "financial_status"),
        ("📊 포트폴리오 전략", "portfolio"),
        ("⚠️ 위험관리 전략", "scenario"),
        ("📅 실행 로드맵", "action_guide"),
        ("📚 부록", "appendix")
    ]
    
    # 각 섹션 표시
    for title, key in sections:
        try:
            if isinstance(report, dict) and key in report:
                st.markdown(f"### {title}")
                if isinstance(report[key], dict) and "content" in report[key]:
                    content = report[key]["content"]
                    st.markdown(content)
                else:
                    content = report[key]  # 직접 내용이 있는 경우
                    st.markdown(content)
                st.markdown("---")
        except Exception as e:
            st.error(f"섹션 '{key}' 표시 중 오류 발생: {str(e)}")