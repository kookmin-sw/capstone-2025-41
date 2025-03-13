import streamlit as st
from modules.DB import SupabaseDB



class UserManager:
    def __init__(self):
        self.db = SupabaseDB()

    def get_user_info(self, username):
        """Supabase에서 사용자 정보 가져오기"""
        user = self.db.get_user(username)  # Supabase에서 데이터 조회
        return user[0] if user else None  # 첫 번째 사용자 정보 반환 (없으면 None)


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
                    st.success("✅ 회원가입 완료!")
                    st.session_state["page"] = "login"
                    st.session_state["id"] = new_id
                    st.rerun()

        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()
