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
        with st.form("investment_profile"):
            st.header("📝 회원가입 및 투자성향 설문")

            # 로그인 정보
            new_id = st.text_input("아이디")
            new_password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")

            # 기본 정보
            age_group = st.selectbox("연령대", ["20~39세", "40~49세", "50~65세", "66~79세", "80세 이상"])
            investment_horizon = st.selectbox("투자 가능 기간", ["5년 이상", "3~5년", "2~3년", "1~2년", "1년 미만"])

            # 투자 경험
            investment_experience = st.radio("투자경험", [
                "적음",
                "보통",
                "많음"
            ])

            # 금융지식 수준
            knowledge_level = st.radio("금융지식수준/이해도", [
                "투자 경험 없음",
                "일부 이해함",
                "깊이 있게 이해함"
            ])

            # 기대 수익/손실 감내 수준
            return_tolerance = st.radio("기대 이익수준 및 손실감내수준", [
                "무조건 원금 보전",
                "원금 기준 ±5%",
                "원금 기준 ±10%",
                "원금 기준 ±20%",
                "원금 기준 ±20% 초과"
            ])

            # 투자 성향
            investment_style = st.selectbox("투자성향", [
                "안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"
            ])

            # 투자 목표
            investment_goal = st.multiselect("투자목표", [
                "예적금 수준 수익", "시장 평균 이상 수익", "적극적인 자산 증식", "생계자금 운용"
            ])

            # 선호 종목
            preferred_assets = st.multiselect("선호 자산군", [
                "주식", "부동산", "예적금", "외화", "금", "암호화폐", "기타"
            ])

            # API 정보
            key = st.text_input("한국투자증권 APP Key")
            secret = st.text_input("APP Secret")
            acc_no = st.text_input("계좌번호")
            mock = st.checkbox("모의투자 계좌입니다")

            if st.form_submit_button("저장"):
                if new_password != confirm_password:
                    st.error("⚠️ 비밀번호가 일치하지 않습니다")
                elif not new_id or not new_password:
                    st.error("⚠️ 아이디와 비밀번호는 필수입니다")
                elif not key or not secret:
                    st.error("⚠️ API 정보를 모두 입력해주세요")
                else:
                    # DB 저장 로직
                    user_data = {
                        "username": new_id,
                        "password": new_password,
                        "api_key": key,
                        "api_secret": secret,
                        "account_no": acc_no,
                        "mock": mock
                    }
                    self.db.insert_user(user_data)

                    profile = {
                        "age_group": age_group,
                        "investment_horizon": investment_horizon,
                        "investment_experience": investment_experience,
                        "knowledge_level": knowledge_level,
                        "return_tolerance": return_tolerance,
                        "investment_style": investment_style,
                        "investment_goal": investment_goal,
                        "preferred_assets": preferred_assets
                    }

                    self.db.insert_user_personal(new_id, profile)
                    st.success("✅ 회원가입이 완료되었습니다!")
                    st.session_state["page"] = "login"
                    st.rerun()


        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()