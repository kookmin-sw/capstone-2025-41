import streamlit as st
from modules.DB import SupabaseDB
from modules.investment_profile import InvestmentProfiler
import json


class UserManager:
    def __init__(self):
        self.db = SupabaseDB()

    def get_user_info(self, username):
        """Supabase에서 사용자 정보 가져오기"""
        user = self.db.get_user(username)
        return user[0] if user else None

    def update_user_info(self, username, updated_data):
        """사용자 정보 수정"""
        return self.db.client.table("users").update(updated_data).eq("username", username).execute()

    def login(self):
        st.title("🔐로그인")

        id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")

        if st.button("로그인"):
            user = self.db.get_user(id)
            if user and user[0]["password"] == password:
                st.success(f"✅ 로그인 성공! {id}님 환영합니다.")
                st.session_state["logged_in"] = True
                st.session_state["id"] = id
                st.session_state["page"] = "main"
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

        if st.button("회원가입"):
            st.session_state["page"] = "sign_up"
            st.rerun()

    def sign_up(self):
        with st.form("sign_up_form"):
            st.header("📝 회원가입")

            # 로그인 정보
            new_id = st.text_input("아이디")
            new_password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")

            # API 정보
            key = st.text_input("한국투자증권 APP Key")
            secret = st.text_input("APP Secret")
            acc_no = st.text_input("계좌번호")
            mock = st.checkbox("모의투자 계좌입니다")

            # 개인 정보
            st.markdown("### 👤 개인 정보")
            
            # 기본 정보
            st.markdown("#### 기본 정보")
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("현재 나이", step=1)
                occupation = st.text_input("직업")
                family_structure = st.selectbox("가족 구성", ["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"])
            with col2:
                retirement_age = st.number_input("은퇴 예정 연령", value=65, step=1)
                housing_type = st.selectbox("주거 형태", ["자가", "전세", "월세"])

            # 재무 목표
            st.markdown("#### 재무 목표")
            short_term_goal = st.text_input("단기 목표 (1~2년)")
            mid_term_goal = st.text_input("중기 목표 (3~5년)")
            long_term_goal = st.text_input("장기 목표 (10년 이상)")

            # 재무 정보
            st.markdown("### 💰 재무 정보")
            
            # 현금 흐름
            st.markdown("#### 현금 흐름")
            monthly_income = st.number_input("월 실수령 수입 (만원)", step=1.0) * 10000
            fixed_expenses = st.number_input("고정 지출 (만원)", step=1.0) * 10000
            variable_expenses = st.number_input("변동 지출 (만원)", step=1.0) * 10000
            monthly_savings = monthly_income - fixed_expenses - variable_expenses

            # 부채 현황
            st.markdown("#### 부채 현황")
            col1, col2, col3 = st.columns(3)
            with col1:
                mortgage = st.number_input("주택담보대출 (만원)", min_value=0, step=1) * 10000
            with col2:
                personal_loan = st.number_input("개인대출 (만원)", min_value=0, step=1) * 10000
            with col3:
                credit_card = st.number_input("신용카드 (만원)", min_value=0, step=1) * 10000
            other_debt = st.number_input("기타 부채 (만원)", min_value=0, step=1) * 10000
            
            # 총 부채 계산
            total_debt = mortgage + personal_loan + credit_card + other_debt
            st.metric("총 부채 금액", f"{int(total_debt/10000):,}만원")
            
            # 월 부채 상환액 입력
            monthly_debt_payment = st.number_input("월 부채 상환액 (만원)", step=1.0) * 10000
            average_interest_rate = st.number_input("평균 이자율 (%)", step=0.1)

            # 보유 자산
            st.markdown("#### 보유 자산")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("현금성 자산")
                cash = st.number_input("현금 (만원)", min_value=0, value=0, step=1) * 10000
                emergency_fund = st.number_input("비상금 (만원)", min_value=0, value=0, step=1) * 10000
                savings = st.number_input("적금 (만원)", min_value=0, value=0, step=1) * 10000

            with col2:
                st.subheader("투자 자산")
                real_estate = st.number_input("부동산 (억원)", min_value=0.0, value=0.0, step=0.1) * 100000000
                funds = st.number_input("펀드 (만원)", min_value=0, value=0, step=1) * 10000
                etfs = st.number_input("ETF (만원)", min_value=0, value=0, step=1) * 10000
                crypto = st.number_input("가상화폐 (만원)", min_value=0, value=0, step=1) * 10000

            with col3:
                st.subheader("보험/연금")
                pension = st.number_input("연금 (만원)", min_value=0, value=0, step=1) * 10000
                insurance = st.number_input("보험 (만원)", min_value=0, value=0, step=1) * 10000

            # 외화 자금 섹션
            st.markdown("#### 외화 자금")
            col1, col2 = st.columns(2)
            with col1:
                usd = st.number_input("USD (달러)", min_value=0.0, value=0.0, step=0.01)
                eur = st.number_input("EUR (유로)", min_value=0.0, value=0.0, step=0.01)
                jpy = st.number_input("JPY (엔)", min_value=0, value=0)
            with col2:
                gbp = st.number_input("GBP (파운드)", min_value=0.0, value=0.0, step=0.01)
                cny = st.number_input("CNY (위안)", min_value=0.0, value=0.0, step=0.01)

            # 투자 성향
            st.markdown("### 🧠 투자 성향")
            result = InvestmentProfiler.get_investment_score(show_result=False)
            investment_profile = result

            # 제출 버튼
            submit = st.form_submit_button("회원가입")

            if submit:
                if new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                    return

                # personal 데이터 구조화
                personal_data = {
                    "financial": {
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
                    },
                    "personal_info": {
                        "age": age,
                        "occupation": occupation,
                        "family_structure": family_structure,
                        "retirement_age": retirement_age,
                        "housing_type": housing_type,
                        "short_term_goal": short_term_goal,
                        "mid_term_goal": mid_term_goal,
                        "long_term_goal": long_term_goal
                    },
                    "investment_profile": investment_profile
                }

                # 사용자 데이터 저장
                user_data = {
                    "username": new_id,
                    "password": new_password,
                    "api_key": key,
                    "api_secret": secret,
                    "account_no": acc_no,
                    "mock": mock,
                    "personal": json.dumps(personal_data, ensure_ascii=False)
                }

                try:
                    self.db.insert_user(user_data)
                    st.success("✅ 회원가입이 완료되었습니다!")
                    st.session_state["page"] = "login"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 회원가입 중 오류가 발생했습니다: {str(e)}")

        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()