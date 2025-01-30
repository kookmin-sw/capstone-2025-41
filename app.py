import streamlit as st
from modules.user_manager import UserManager
from modules.account_manager import AccountManager
from modules.visualization import Visualization

class App():
    def __init__(self):
        if "page" not in st.session_state:
            st.session_state["page"] = "login"
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False
        if "username" not in st.session_state:
            st.session_state["username"] = None
        if "stock_df" not in st.session_state:
            st.session_state["stock_df"] = None
        if "account_df" not in st.session_state:
            st.session_state["account_df"] = None

        # 개인정보 관리 (ID, 패스워드, API KEY 등)
        self.user_manager = UserManager()

    def run(self):
        # 로그인 페이지
        if st.session_state["page"] == "login":
            self.user_manager.login()

        # 회원가입 페이지
        elif st.session_state["page"] == "sign_up":
            self.user_manager.sign_up()

        # 메인 페이지
        elif st.session_state["page"] == "main":
            user = self.user_manager.load_user()

            # 계좌 데이터 불러오기
            try:
                key = user["KEY"]
                secret = user["SECRET"]
                acc_no = user["ACC_NO"]
                mock = user["MOCK"]

                account_manager = AccountManager(key, secret, acc_no, mock)
                st.session_state["stock_df"] = account_manager.get_stock()
                st.session_state["account_df"] = account_manager.get_account()
            except:
                st.error("**⚠️데이터를 불러오는 데 실패했습니다**")

            if st.session_state["stock_df"] is not None and st.session_state["account_df"] is not None:
                total = int(st.session_state["account_df"].loc[0, '총평가금액'])
                profit = int(st.session_state["account_df"].loc[0, '평가손익합계금액'])

                st.header("📜나의 포트폴리오")
                st.metric("총자산", f"{total:,}원",
                          f"{int(st.session_state['account_df'].loc[0, '평가손익합계금액']):,}원  |  " \
                          f"{round(profit / (total - profit) * 100, 2):,.2f}%")

                # ---------------- 메인 페이지 시각화 ----------------#
                visualization = Visualization(st.session_state["stock_df"], st.session_state["account_df"])

                # 포트폴리오 도넛 차트 시각화
                visualization.portfolio_doughnut_chart()


if __name__ == "__main__":
    app = App()
    app.run()
