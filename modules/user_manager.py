import streamlit as st
from modules.DB import SupabaseDB
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
            total_debt = st.number_input("총 부채 금액 (만원)", step=1.0) * 10000
            monthly_debt_payment = st.number_input("월 부채 상환액 (만원)", step=1.0) * 10000
            average_interest_rate = st.number_input("평균 이자율 (%)", step=0.1)

            # 보유 자산
            st.markdown('<div class="section-title">보유 자산</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                cash = st.number_input("현금 (만원)", value=0.0, step=1.0) * 10000
                emergency_fund = st.number_input("비상금 (만원)", value=0.0, step=1.0) * 10000
                savings = st.number_input("예/적금 (만원)", value=0.0, step=1.0) * 10000
                funds = st.number_input("펀드/ETF (만원)", value=0.0, step=1.0) * 10000
            with col2:
                real_estate = st.number_input("부동산 (만원)", value=0.0, step=1.0) * 10000
                pension = st.number_input("연금/보험 (만원)", value=0.0, step=1.0) * 10000
                other_assets = st.number_input("코인/기타 자산 (만원)", value=0.0, step=1.0) * 10000

            # 재무 목표
            st.markdown("#### 재무 목표")
            short_term_goal = st.text_input("단기 목표 (1~2년)")
            mid_term_goal = st.text_input("중기 목표 (3~5년)")
            long_term_goal = st.text_input("장기 목표 (10년 이상)")

            # 기타 변수
            st.markdown("#### 기타 변수")
            age = st.number_input("현재 나이", step=1)
            family_structure = st.selectbox("가족 구성", ["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"])
            retirement_age = st.number_input("은퇴 예정 연령", value=65, step=1)
            housing_type = st.selectbox("주거 형태", ["자가", "전세", "월세"])

            # 투자 성향
            st.markdown("### 🧠 투자 성향")
            age_group = st.selectbox("연령대", ["20~39세", "40~49세", "50~65세", "66~79세", "80세 이상"])
            investment_horizon = st.selectbox("투자 가능 기간", ["5년 이상", "3~5년", "2~3년", "1~2년", "1년 미만"])
            investment_experience = st.radio("투자경험", ["적음", "보통", "많음"])
            knowledge_level = st.radio("금융지식 수준/이해도", ["투자 경험 없음", "일부 이해함", "깊이 있게 이해함"])
            return_tolerance = st.radio("기대 이익수준 및 손실감내 수준", 
                                      ["무조건 원금 보전", "원금 기준 ±5%", "원금 기준 ±10%", "원금 기준 ±20%", "원금 기준 ±20% 초과"])
            investment_style = st.selectbox("투자성향", ["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"])
            investment_goal = st.multiselect("투자목표", ["예적금 수준 수익", "시장 평균 이상 수익", "적극적인 자산 증식", "생계자금 운용"])
            preferred_assets = st.multiselect("선호 자산군", ["주식", "부동산", "예적금", "외화", "금", "암호화폐", "기타"])

            if st.form_submit_button("저장"):
                if new_password != confirm_password:
                    st.error("⚠️ 비밀번호가 일치하지 않습니다")
                elif not new_id or not new_password:
                    st.error("⚠️ 아이디와 비밀번호는 필수입니다")
                elif not key or not secret:
                    st.error("⚠️ API 정보를 모두 입력해주세요")
                else:
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
                        "real_estate": real_estate,
                        "pension": pension,
                        "other_assets": other_assets,
                        "short_term_goal": short_term_goal,
                        "mid_term_goal": mid_term_goal,
                        "long_term_goal": long_term_goal,
                        "age": age,
                        "family_structure": family_structure,
                        "retirement_age": retirement_age,
                        "housing_type": housing_type
                    }

                    # 투자 성향
                    investment_profile = {
                        "age_group": age_group,
                        "investment_horizon": investment_horizon,
                        "investment_experience": investment_experience,
                        "knowledge_level": knowledge_level,
                        "return_tolerance": return_tolerance,
                        "investment_style": investment_style,
                        "investment_goal": investment_goal,
                        "preferred_assets": preferred_assets
                    }

                    # 모든 정보를 personal 필드에 통합
                    personal_data = {
                        "financial": financial_data,
                        "investment_profile": investment_profile
                    }

                    # DB 저장 로직
                    user_data = {
                        "username": new_id,
                        "password": new_password,
                        "api_key": key,
                        "api_secret": secret,
                        "account_no": acc_no,
                        "mock": mock,
                        "personal": personal_data
                    }
                    
                    self.db.insert_user(user_data)
                    st.success("✅ 회원가입이 완료되었습니다!")
                    st.session_state["page"] = "login"
                    st.rerun()

        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()