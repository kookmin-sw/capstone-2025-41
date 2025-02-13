import streamlit as st
import json
import os

# 사용자 데이터 저장 파일
USER_DATA_FILE = "data/user.json"

class UserManager:
    def __init__(self):
        self.user = self.load_user()

    def load_user(self):
        """사용자 데이터 로드"""
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        return {"ID": None, "PASSWORD": None, "KEY": None, "SECRET": None,
                "ACC_NO": None, "MOCK": None}

    def save_user(self):
        """사용자 데이터 저장"""
        with open(USER_DATA_FILE, "w") as f:
            json.dump(self.user, f)

    def login(self):
        """로그인 페이지"""
        st.title("🔐로그인")

        id = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")

        if st.button("로그인"):
            if self.user["ID"] == id and self.user["PASSWORD"] == password:
                st.success("✅로그인 성공!")
                st.session_state["logged_in"] = True
                st.session_state["id"] = id
                st.session_state["page"] = "main"
                st.rerun()
            else:
                st.error("⚠️아이디 또는 비밀번호가 올바르지 않습니다")

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
                    self.user["ID"] = new_id
                    self.user["PASSWORD"] = new_password
                    self.user["KEY"] = key
                    self.user["SECRET"] = secret
                    self.user["ACC_NO"] = acc_no
                    self.user["MOCK"] = mock
                    self.save_user()
                    st.success("✅회원가입 완료!")
                    st.session_state["page"] = "login"
                    st.session_state["id"] = new_id
                    st.rerun()

        if st.button("로그인 페이지로 이동"):
            st.session_state["page"] = "login"
            st.rerun()
