import streamlit as st
import pandas as pd
from modules.user_manager import UserManager
from modules.account_manager import AccountManager
from modules.visualization import Visualization
from modules.etf import ETFAnalyzer
from modules.crawling_article import crawlingArticle

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
        if "cash" not in st.session_state:
            st.session_state["cash"] = None
        if "etf_loaded" not in st.session_state:
            st.session_state["etf_loaded"] = False
        if "article_loaded" not in st.session_state:
            st.session_state["article_loaded"] = False

        # 개인정보 관리 (ID, 패스워드, API KEY 등)
        self.user_manager = UserManager()

    def run(self):
        # 사이드바 추가
        if st.session_state["logged_in"]:
            st.sidebar.title("📌 메뉴")
            # menu = st.sidebar.radio("메뉴 선택", ["자산 관리", "ETF 분석", "로그아웃"])
            menu = st.sidebar.radio("메뉴 선택", ["자산 관리", "ETF 분석", "경제 뉴스", "로그아웃"])
            
            if menu == "자산 관리":
                st.session_state["page"] = "main"
            elif menu == "ETF 분석":
                st.session_state["page"] = "etf_analysis"
            elif menu == "경제 뉴스":
                st.session_state["page"] = "economic_news"
            elif menu == "로그아웃":
                st.session_state.clear()
                st.session_state["page"] = "login"
                st.rerun()


        # 로그인 페이지
        if st.session_state["page"] == "login":
            self.user_manager.login()

        # 회원가입 페이지
        if st.session_state["page"] == "sign_up":
            self.user_manager.sign_up()

        # 메인 페이지
        if st.session_state["page"] == "main":
            user = self.user_manager.load_user()

            # 계좌 데이터 불러오기
            try:
                key = user["KEY"]
                secret = user["SECRET"]
                acc_no = user["ACC_NO"]
                mock = user["MOCK"]

                account_manager = AccountManager(key, secret, acc_no, mock)
                account_manager.save_data()
                st.session_state["stock_df"] = account_manager.get_stock()
                st.session_state["account_df"] = account_manager.get_account()
                st.session_state["cash"] = account_manager.get_cash()
            except Exception as e:
                st.error("**⚠️데이터를 불러오는 데 실패했습니다**")
                st.write(e)

            if st.session_state["stock_df"] is not None and st.session_state["account_df"] is not None:
                # 자산 증감액 및 자산 증감율
                total = int(st.session_state["account_df"].loc[0, '총평가금액']) + st.session_state["cash"]
                profit = int(st.session_state["account_df"].loc[0, '평가손익합계금액'])

                st.title("📜나의 포트폴리오")
                st.metric("총자산", f"{int(total):,}원",
                          f"{int(st.session_state['account_df'].loc[0, '평가손익합계금액']):,}원  |  " \
                          f"{round(profit / (total - profit) * 100, 2):,.2f}%")

                # ---------------- 메인 페이지 시각화 ----------------#
                visualization = Visualization(st.session_state["stock_df"],
                                              st.session_state["account_df"],
                                              st.session_state["cash"])

                # 포트폴리오 도넛 차트 시각화
                visualization.portfolio_doughnut_chart()

                cash = st.text_input("**현금**")
                if st.button("저장"):
                    account_manager.modify_cash(cash)
                    st.rerun()

        # ETF 분석 페이지
        if st.session_state["page"] == "etf_analysis":
            st.title("📈 ETF 섹터별 분석")
            st.write("ETF 데이터를 분석할 수 있는 페이지입니다.")

            if not st.session_state["etf_loaded"]:
                with st.spinner("ETF 데이터를 수집하는 중... ⏳"):
                    ETFAnalyzer.save_etf_data()
                st.session_state["etf_loaded"] = True  # 데이터 로드 완료 상태 변경

            # ✅ 자동으로 ETF 데이터 시각화
            ETFAnalyzer.visualize_etf()

        # 경제 뉴스 페이지
        if st.session_state["page"] == "economic_news":
            st.title("오늘의 경제 뉴스")

            with st.spinner("뉴스 기사를 수집하는 중... ⏳"):
                crawaling_article = crawlingArticle()
                crawaling_article.save_article()

            # 워드 클라우드 시각화
            crawaling_article.visualize_wordcloud()
            
            # 뉴스 기사 데이터프레임
            article = crawaling_article.get_article()
            st.write(article)



if __name__ == "__main__":
    app = App()
    app.run()