import streamlit as st
from modules.DB import SupabaseDB



class UserManager:
    def __init__(self):
        self.db = SupabaseDB()

    def get_user_info(self, username):
        """Supabase에서 사용자 정보 가져오기"""
        user = self.db.get_user(username)  # Supabase에서 데이터 조회
        return user[0] if user else None  # 첫 번째 사용자 정보 반환 (없으면 None)

    def update_user_info(self, username, updated_data):
        """사용자 정보 수정"""
        return self.db.client.table("users").update(updated_data).eq("username", username).execute()


    def login(self):
        """로그인 페이지"""
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
        """회원가입 페이지"""
        with st.form("personal_information"):
            st.header("📝회원가입")

            # 회원가입
            new_id = st.text_input("아이디")
            new_password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            
            # 개인 정보
            age = st.number_input("나이", min_value=0, max_value=120, step=1)
            gender = st.selectbox("성별", ["선택 안 함", "남성", "여성"])
            investment_type = st.selectbox("투자 성향", ["보수형", "중립형", "공격형"])
            investment_goal = st.selectbox("투자 목적", ["자산 증식", "은퇴 준비", "단기 수익", "기타"])
            investment_horizon = st.selectbox("투자 기간", ["1년 이하", "1~3년", "3~5년", "5년 이상"])
            risk_tolerance = st.selectbox("리스크 허용도", ["낮음", "중간", "높음"])
            monthly_investment = st.number_input("월 평균 투자 가능 금액 (원)", step=10000)
            preferred_assets = st.multiselect("선호 자산군", ["주식", "ETF", "부동산", "채권", "대체투자", "기타"])            

            # 계좌 불러오기
            key = st.text_input("한국투자증권의 **APP Key**를 입력하세요")
            secret = st.text_input("한국투자증권의 **APP Secret**를 입력하세요")
            acc_no = st.text_input("한국투자증권의 **계좌번호**를 입력하세요")
            mock = st.checkbox("모의투자 계좌입니다")

            if st.form_submit_button("저장"):
                if new_password != confirm_password:
                    st.error("⚠️비밀번호가 일치하지 않습니다")
                elif not new_id or not new_password:
                    st.error("⚠️아이디와 비밀번호를 입력해주세요")
                elif not key or not secret:
                    st.error("⚠️한국투자증권 API를 입력해주세요")
                else:
                    user_data = {
                        "username": new_id,
                        "password": new_password,
                        "api_key": key,
                        "api_secret": secret,
                        "account_no": acc_no,
                        "mock": mock
                    }
                    self.db.insert_user(user_data)

                    # personal만 따로 JSON으로 저장
                    personal_data = {
                        "age": age,
                        "gender": gender,
                        "investment_type": investment_type,
                        "investment_goal": investment_goal,
                        "investment_horizon": investment_horizon,
                        "risk_tolerance": risk_tolerance,
                        "monthly_investment": monthly_investment,
                        "preferred_assets": preferred_assets
                    }
                    self.db.insert_user_personal(new_id, personal_data)
                    st.success("✅ 회원가입 완료!")
                    st.session_state["page"] = "login"
                    st.session_state["id"] = new_id
                    st.rerun()

        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()
