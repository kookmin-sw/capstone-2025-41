import streamlit as st
from modules.DB import SupabaseDB
from modules.investment_profile import InvestmentProfiler
import json

class MyPage:
    def __init__(self):
        self.db = SupabaseDB()
        if "editing_mode" not in st.session_state:
            st.session_state["editing_mode"] = False

    def show(self):
        # 페이지 제목과 설명
        st.title("👤 마이페이지")
        st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            font-weight: bold;
        }
        .info-box {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section-title {
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .masked-text {
            font-family: monospace;
            letter-spacing: 2px;
        }
        </style>
        """, unsafe_allow_html=True)

        # 사용자 정보 가져오기
        user = self.db.get_user(st.session_state["id"])
        if not user:
            st.error("사용자 정보를 찾을 수 없습니다.")
            return

        user = user[0]
        personal_data = user.get("personal", {})
        financial_data = personal_data.get("financial", {})
        investment_profile = personal_data.get("investment_profile", {})

        if st.session_state["editing_mode"]:
            # 수정 모드 UI
            tab1, tab2, tab3, tab4 = st.tabs(["🔑 계정 정보", "👤 개인 정보", "💰 재무 정보", "🧠 투자 성향"])
            
            with tab1:
                with st.container():
                    st.markdown('<div class="section-title">계정 정보</div>', unsafe_allow_html=True)
                    username = st.text_input("아이디", value=user.get("username", ""))
                    password = st.text_input("비밀번호", value="", type="password")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">API 정보</div>', unsafe_allow_html=True)
                    api_key = st.text_input("한국투자증권 APP Key", value=user.get("api_key", ""), type="password")
                    api_secret = st.text_input("APP Secret", value=user.get("api_secret", ""), type="password")
                    account_no = st.text_input("계좌번호", value=user.get("account_no", ""))
                    mock = st.checkbox("모의투자 계좌입니다", value=user.get("mock", False))
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                with st.container():
                    st.markdown('<div class="section-title">기본 정보</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        occupation = st.text_input("직업", value=financial_data.get("occupation", ""))
                        age = st.number_input("현재 나이", value=financial_data.get("age", 0), step=1)
                        family_structure = st.selectbox("가족 구성", ["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"], 
                                                      index=["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"].index(financial_data.get("family_structure", "싱글")))
                    with col2:
                        retirement_age = st.number_input("은퇴 예정 연령", value=financial_data.get("retirement_age", 65), step=1)
                        housing_type = st.selectbox("주거 형태", ["자가", "전세", "월세"], 
                                                  index=["자가", "전세", "월세"].index(financial_data.get("housing_type", "자가")))

                    st.markdown('<div class="section-title">재무 목표</div>', unsafe_allow_html=True)
                    short_term_goal = st.text_input("단기 목표 (1~2년)", value=financial_data.get("short_term_goal", ""))
                    mid_term_goal = st.text_input("중기 목표 (3~5년)", value=financial_data.get("mid_term_goal", ""))
                    long_term_goal = st.text_input("장기 목표 (10년 이상)", value=financial_data.get("long_term_goal", ""))

            with tab3:
                with st.container():
                    st.markdown('<div class="section-title">현금 흐름</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        monthly_income = st.number_input("월 실수령 수입 (만원)", value=float(financial_data.get("monthly_income", 0))/10000, step=1.0, key="monthly_income_input") * 10000
                    with col2:
                        fixed_expenses = st.number_input("고정 지출 (만원)", value=float(financial_data.get("fixed_expenses", 0))/10000, step=1.0, key="fixed_expenses_input") * 10000
                    with col3:
                        variable_expenses = st.number_input("변동 지출 (만원)", value=float(financial_data.get("variable_expenses", 0))/10000, step=1.0, key="variable_expenses_input") * 10000
                    monthly_savings = monthly_income - fixed_expenses - variable_expenses

                    st.markdown('<div class="section-title">부채 현황</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        mortgage = st.number_input("주택담보대출 (만원)", min_value=0, value=int(float(financial_data.get('mortgage', 0))/10000), step=1, key="mortgage_input") * 10000
                    with col2:
                        personal_loan = st.number_input("개인대출 (만원)", min_value=0, value=int(float(financial_data.get('personal_loan', 0))/10000), step=1, key="personal_loan_input") * 10000
                    with col3:
                        credit_card = st.number_input("신용카드 (만원)", min_value=0, value=int(float(financial_data.get('credit_card', 0))/10000), step=1, key="credit_card_input") * 10000
                    other_debt = st.number_input("기타 부채 (만원)", min_value=0, value=int(float(financial_data.get('other_debt', 0))/10000), step=1, key="other_debt_input") * 10000
                    
                    # 총 부채 계산
                    total_debt = mortgage + personal_loan + credit_card + other_debt
                    st.metric("총 부채 금액", f"{int(total_debt/10000):,}만원")
                    
                    # 월 부채 상환액 입력
                    monthly_debt_payment = st.number_input("월 부채 상환액 (만원)", min_value=0, value=int(float(financial_data.get('monthly_debt_payment', 0))/10000), step=1, key="monthly_debt_payment_input") * 10000
                    average_interest_rate = st.number_input("평균 이자율 (%)", value=float(financial_data.get('average_interest_rate', 0)), step=0.1, key="interest_rate_input")

                    st.markdown('<div class="section-title">보유 자산</div>', unsafe_allow_html=True)
                    
                    # 자산 정보를 3열로 나누어 표시
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.subheader("현금성 자산")
                        cash = st.number_input("현금 (만원)", min_value=0, value=int(float(financial_data.get('cash', 0))/10000), step=1, key="cash_input") * 10000
                        emergency_fund = st.number_input("비상금 (만원)", min_value=0, value=int(float(financial_data.get('emergency_fund', 0))/10000), step=1, key="emergency_fund_input") * 10000
                        savings = st.number_input("적금 (만원)", min_value=0, value=int(float(financial_data.get('savings', 0))/10000), step=1, key="savings_input") * 10000
                    
                    with col2:
                        st.subheader("투자 자산")
                        real_estate = st.number_input("부동산 (억원)", min_value=0.0, value=float(financial_data.get('real_estate', 0))/100000000, step=0.1, key="real_estate_input") * 100000000
                        funds = st.number_input("펀드 (만원)", min_value=0, value=int(float(financial_data.get('funds', 0))/10000), step=1, key="funds_input") * 10000
                        etfs = st.number_input("ETF (만원)", min_value=0, value=int(float(financial_data.get('etfs', 0))/10000), step=1, key="etfs_input") * 10000
                        crypto = st.number_input("가상화폐 (만원)", min_value=0, value=int(float(financial_data.get('crypto', 0))/10000), step=1, key="crypto_input") * 10000
                    
                    with col3:
                        st.subheader("보험/연금")
                        pension = st.number_input("연금 (만원)", min_value=0, value=int(float(financial_data.get('pension', 0))/10000), step=1, key="pension_input") * 10000
                        insurance = st.number_input("보험 (만원)", min_value=0, value=int(float(financial_data.get('insurance', 0))/10000), step=1, key="insurance_input") * 10000
                    
                    # 외화 자금 섹션
                    st.markdown('<div class="section-title">외화 자금</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        usd = st.number_input("USD (달러)", min_value=0.0, value=float(financial_data.get('foreign_currency', {}).get('usd', 0)), step=0.01, key="usd_input")
                        eur = st.number_input("EUR (유로)", min_value=0.0, value=float(financial_data.get('foreign_currency', {}).get('eur', 0)), step=0.01, key="eur_input")
                        jpy = st.number_input("JPY (엔)", min_value=0, value=int(financial_data.get('foreign_currency', {}).get('jpy', 0)), key="jpy_input")
                    with col2:
                        gbp = st.number_input("GBP (파운드)", min_value=0.0, value=float(financial_data.get('foreign_currency', {}).get('gbp', 0)), step=0.01, key="gbp_input")
                        cny = st.number_input("CNY (위안)", min_value=0.0, value=float(financial_data.get('foreign_currency', {}).get('cny', 0)), step=0.01, key="cny_input")

            with tab4:
                with st.container():
                    st.markdown('<div class="section-title">투자 성향 진단</div>', unsafe_allow_html=True)
                    
                    # 이전 투자 성향 정보 표시 (읽기 모드에서만)
                    if not st.session_state["editing_mode"]:
                        if investment_profile:
                            st.write("### 현재 투자 성향")
                            st.write(f"**투자 성향:** {investment_profile.get('investment_style', '미진단')}")
                            
                            if details := investment_profile.get('details'):
                                st.write("### 이전 응답 내역")
                                st.write(f"- 투자 경험: {details.get('investment_experience', '')}")
                                st.write(f"- 투자 가능 기간: {details.get('investment_horizon', '')}")
                                st.write(f"- 손실 감내 수준: {details.get('risk_tolerance', '')}")
                                st.write(f"- 기대 수익률: {details.get('expected_return', '')}")
                                st.write(f"- 중요 투자 요소: {details.get('investment_priority', '')}")
                                st.write(f"- 금융 이해도: {details.get('financial_knowledge', '')}")
                    
                    # 새로운 진단 실행 (수정 모드이거나 이전 진단 결과가 없는 경우)
                    if st.session_state["editing_mode"] or not investment_profile:
                        st.write("### 투자 성향 진단")
                        if st.session_state["editing_mode"]:
                            st.write("투자 성향을 다시 진단합니다. 각 질문에 답변해 주세요.")
                        result = InvestmentProfiler.get_investment_score(show_result=False)  # 수정 모드에서는 결과 표시 안 함
                        investment_profile = result

            col1, col2 = st.columns(2)
            with col1:
                if st.button("저장", type="primary"):
                    # 재무 정보
                    financial_data = {
                        "monthly_income": monthly_income,
                        "fixed_expenses": fixed_expenses,
                        "variable_expenses": variable_expenses,
                        "monthly_savings": monthly_savings,
                        "total_debt": total_debt,
                        "monthly_debt_payment": monthly_debt_payment,
                        "average_interest_rate": average_interest_rate,
                        "cash": cash,
                        "emergency_fund": emergency_fund,
                        "savings": savings,
                        "funds": funds,
                        "etfs": etfs,
                        "pension": pension,
                        "insurance": insurance,
                        "crypto": crypto,
                        "real_estate": real_estate,
                        "mortgage": mortgage,
                        "personal_loan": personal_loan,
                        "credit_card": credit_card,
                        "other_debt": other_debt,
                        "foreign_currency": {
                            "usd": usd,
                            "eur": eur,
                            "jpy": jpy,
                            "gbp": gbp,
                            "cny": cny
                        }
                    }

                    # 개인 정보
                    personal_info = {
                        "age": age,
                        "occupation": occupation,
                        "family_structure": family_structure,
                        "retirement_age": retirement_age,
                        "housing_type": housing_type,
                        "short_term_goal": short_term_goal,
                        "mid_term_goal": mid_term_goal,
                        "long_term_goal": long_term_goal
                    }

                    # DB 업데이트
                    updated_data = {
                        "username": username,
                        "password": password if password else user.get("password", ""),
                        "api_key": api_key if api_key else user.get("api_key", ""),
                        "api_secret": api_secret if api_secret else user.get("api_secret", ""),
                        "account_no": account_no,
                        "mock": mock,
                        "personal": json.dumps({
                            "financial": financial_data,
                            "personal_info": personal_info,
                            "investment_profile": investment_profile
                        }, ensure_ascii=False)
                    }

                    # 사용자 정보 업데이트
                    try:
                        self.db.update_user_info(st.session_state["id"], updated_data)
                        st.session_state["editing_mode"] = False
                        st.success("✅ 정보가 성공적으로 저장되었습니다!")
                        st.rerun()  # 저장 후 바로 보기 모드로 전환
                    except Exception as e:
                        st.error(f"저장 중 오류가 발생했습니다: {str(e)}")
            with col2:
                if st.button("취소", type="secondary"):
                    st.session_state["editing_mode"] = False
        else:
            # 읽기 모드 UI
            tab1, tab2, tab3, tab4 = st.tabs(["🔑 계정 정보", "👤 개인 정보", "💰 재무 정보", "🧠 투자 성향"])
            
            with tab1:
                st.markdown('<div class="section-title">계정 정보</div>', unsafe_allow_html=True)
                st.write(f"**아이디:** {user.get('username', '')}")
                st.write("**비밀번호:** ********")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">API 정보</div>', unsafe_allow_html=True)
                st.write("**한국투자증권 APP Key:** ", "*" * 20)
                st.write("**APP Secret:** ", "*" * 20)
                st.write(f"**계좌번호:** {user.get('account_no', '')}")
                st.write(f"**모의투자 계좌:** {'예' if user.get('mock', False) else '아니오'}")
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div class="section-title">기본 정보</div>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**직업:** {financial_data.get('occupation', '-')}")
                    st.write(f"**현재 나이:** {financial_data.get('age', 0)}세")
                    st.write(f"**가족 구성:** {financial_data.get('family_structure', '-')}")
                with col2:
                    st.write(f"**은퇴 예정 연령:** {financial_data.get('retirement_age', 65)}세")
                    st.write(f"**주거 형태:** {financial_data.get('housing_type', '-')}")
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">재무 목표</div>', unsafe_allow_html=True)
                st.write(f"**단기 목표 (1~2년):** {financial_data.get('short_term_goal', '-')}")
                st.write(f"**중기 목표 (3~5년):** {financial_data.get('mid_term_goal', '-')}")
                st.write(f"**장기 목표 (10년 이상):** {financial_data.get('long_term_goal', '-')}")
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                with st.container():
                    st.markdown('<div class="section-title">현금 흐름</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("월 실수령 수입", f"{int(financial_data.get('monthly_income', 0)):,}원")
                    with col2:
                        st.metric("고정 지출", f"{int(financial_data.get('fixed_expenses', 0)):,}원")
                    with col3:
                        st.metric("변동 지출", f"{int(financial_data.get('variable_expenses', 0)):,}원")
                    st.metric("월 평균 저축 가능액", f"{int(financial_data.get('monthly_savings', 0)):,}원", 
                             delta=f"{int(financial_data.get('monthly_savings', 0) - financial_data.get('fixed_expenses', 0) - financial_data.get('variable_expenses', 0)):,}원")

                    st.markdown('<div class="section-title">부채 현황</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 부채 금액", f"{int(financial_data.get('total_debt', 0)):,}원")
                    with col2:
                        st.metric("월 부채 상환액", f"{int(financial_data.get('monthly_debt_payment', 0)):,}원")
                    with col3:
                        st.metric("평균 이자율", f"{financial_data.get('average_interest_rate', 0)}%")

                    st.markdown('<div class="section-title">보유 자산</div>', unsafe_allow_html=True)
                    
                    # 자산 정보를 3열로 나누어 표시
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.subheader("현금성 자산")
                        st.metric("현금", f"{int(financial_data.get('cash', 0))/10000:,.0f}만원")
                        st.metric("비상금", f"{int(financial_data.get('emergency_fund', 0))/10000:,.0f}만원")
                        st.metric("적금", f"{int(financial_data.get('savings', 0))/10000:,.0f}만원")
                    
                    with col2:
                        st.subheader("투자 자산")
                        st.metric("부동산", f"{float(financial_data.get('real_estate', 0))/100000000:,.1f}억원")
                        st.metric("펀드", f"{int(financial_data.get('funds', 0))/10000:,.0f}만원")
                        st.metric("ETF", f"{int(financial_data.get('etfs', 0))/10000:,.0f}만원")
                        st.metric("가상화폐", f"{int(financial_data.get('crypto', 0))/10000:,.0f}만원")
                    
                    with col3:
                        st.subheader("보험/연금")
                        st.metric("연금", f"{int(financial_data.get('pension', 0))/10000:,.0f}만원")
                        st.metric("보험", f"{int(financial_data.get('insurance', 0))/10000:,.0f}만원")
                    
                    # 외화 자금 섹션
                    st.markdown('<div class="section-title">외화 자금</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        foreign_currency = financial_data.get('foreign_currency', {})
                        st.metric("USD (달러)", f"${float(foreign_currency.get('usd', 0)):,.2f}")
                        st.metric("EUR (유로)", f"€{float(foreign_currency.get('eur', 0)):,.2f}")
                        st.metric("JPY (엔)", f"¥{int(foreign_currency.get('jpy', 0)):,}")
                    with col2:
                        st.metric("GBP (파운드)", f"£{float(foreign_currency.get('gbp', 0)):,.2f}")
                        st.metric("CNY (위안)", f"¥{float(foreign_currency.get('cny', 0)):,.2f}")

            with tab4:
                with st.container():
                    st.markdown('<div class="section-title">투자 성향 진단</div>', unsafe_allow_html=True)
                    
                    # 읽기 모드에서만 결과 표시
                    if not st.session_state["editing_mode"]:
                        if investment_profile:
                            st.write("### 투자 성향 진단 결과")
                            st.write(f"**투자 성향:** {investment_profile.get('investment_style', '미진단')}")
                            
                            if details := investment_profile.get('details'):
                                st.write("### 세부 응답")
                                st.write(f"- 투자 경험: {details.get('investment_experience', '')}")
                                st.write(f"- 투자 가능 기간: {details.get('investment_horizon', '')}")
                                st.write(f"- 손실 감내 수준: {details.get('risk_tolerance', '')}")
                                st.write(f"- 기대 수익률: {details.get('expected_return', '')}")
                                st.write(f"- 중요 투자 요소: {details.get('investment_priority', '')}")
                                st.write(f"- 금융 이해도: {details.get('financial_knowledge', '')}")
                    
                    # 새로운 진단 실행 (수정 모드이거나 이전 진단 결과가 없는 경우)
                    if st.session_state["editing_mode"] or not investment_profile:
                        st.write("### 투자 성향 진단")
                        if st.session_state["editing_mode"]:
                            st.write("투자 성향을 다시 진단합니다. 각 질문에 답변해 주세요.")
                        result = InvestmentProfiler.get_investment_score(show_result=False)  # 수정 모드에서는 결과 표시 안 함
                        investment_profile = result

            if st.button("정보 수정", type="primary"):
                st.session_state["editing_mode"] = True
                st.rerun()
