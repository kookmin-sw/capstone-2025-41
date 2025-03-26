import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from modules.user_manager import UserManager
from modules.account_manager import AccountManager
from modules.visualization import Visualization
from modules.etf import ETFAnalyzer
from modules.crawling_article import crawlingArticle
from modules.collect_economic_data import collectEconomicData

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

        # Supabase 사용자 관리
        self.user_manager = UserManager()

    def run(self):
        # 사이드바 추가
        if st.session_state["logged_in"]:
            st.sidebar.title("📌 메뉴")
            menu = st.sidebar.radio("메뉴 선택", ["자산 관리", "마이페이지", "ETF 분석", "경제 뉴스", "경제 지표", "로그아웃"])
            
            if menu == "자산 관리":
                st.session_state["page"] = "main"
            if menu == "마이페이지":
                st.session_state["page"] = "my_page"
            elif menu == "ETF 분석":
                st.session_state["page"] = "etf_analysis"
            elif menu == "경제 뉴스":
                st.session_state["page"] = "economic_news"
            elif menu == "경제 지표":
                st.session_state["page"] = "economic_data"
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

        # 메인 페이지 (자산 관리)
        if st.session_state["page"] == "main":
            user = self.user_manager.get_user_info(st.session_state["id"])  # Supabase에서 사용자 정보 가져오기

            if not user:
                st.error("⚠️ 사용자 정보를 불러올 수 없습니다. 다시 로그인해 주세요.")
                st.session_state["logged_in"] = False
                st.session_state["page"] = "login"
                st.rerun()
                return

            # 계좌 데이터 불러오기 및 저장
            try:
                key = user["api_key"]
                secret = user["api_secret"]
                acc_no = user["account_no"]
                mock = user["mock"]
                user_id = user["id"]  # `user_id` 가져오기

                # `user_id`를 추가하여 AccountManager 객체 생성
                account_manager = AccountManager(key, secret, acc_no, mock, user_id)    
                # 기존 데이터 확인 후 저장 (중복 삽입 방지)
                existing_stocks = account_manager.db.get_stock_data(user_id)
                existing_accounts = account_manager.db.get_account_data(user_id)
                existing_cash = account_manager.db.get_cash_data(user_id)

                # 데이터가 없을 경우에만 저장 실행
                if not existing_stocks or not existing_accounts or existing_cash is None:
                    account_manager.save_data(user_id)  # S

                st.session_state["stock_df"] = account_manager.get_stock()
                st.session_state["account_df"] = account_manager.get_account()
                st.session_state["cash"] = account_manager.get_cash()
            except Exception as e:
                st.error("**⚠️ 데이터를 불러오는 데 실패했습니다**")
                st.write(e)


            if st.session_state["stock_df"] is not None and st.session_state["account_df"] is not None:
                # 자산 증감액 및 자산 증감율
                total = int(st.session_state["account_df"].loc[0, '총평가금액']) + st.session_state["cash"]
                profit = int(st.session_state["account_df"].loc[0, '평가손익합계금액'])

                st.title("📜 나의 포트폴리오")
                st.metric("총자산", f"{int(total):,}원",
                          f"{int(st.session_state['account_df'].loc[0, '평가손익합계금액']):,}원  |  " \
                          f"{round(profit / (total - profit) * 100, 2):,.2f}%")

                # ---------------- 메인 페이지 시각화 ----------------#
                visualization = Visualization(st.session_state["stock_df"],
                                              st.session_state["account_df"],
                                              st.session_state["cash"])

                # 포트폴리오 도넛 차트 시각화
                visualization.portfolio_doughnut_chart()

                # expander 상태를 관리하는 세션 변수 추가 (초기 상태: 닫힘)
                if "expander_open" not in st.session_state:
                    st.session_state["expander_open"] = False

                with st.expander("💰 현금 잔액 수정", expanded=st.session_state["expander_open"]):
                    cash = st.text_input("현금 잔액", value=str(st.session_state["cash"] or 0))
                    
                    if st.button("저장"):
                        account_manager.modify_cash(cash)
                        st.success("💰 현금이 업데이트되었습니다!")
                        
                        # 현금 업데이트 후 expander를 닫도록 상태 변경
                        st.session_state["cash"] = cash
                        st.session_state["expander_open"] = False  
                        st.rerun()
                    
                    # 사용자가 expander를 열면 상태를 유지
                    st.session_state["expander_open"] = True




        # ETF 분석 페이지 (트리맵 적용)
        if st.session_state["page"] == "etf_analysis":
            analyzer = ETFAnalyzer()  # 인스턴스 생성
            if not st.session_state["etf_loaded"]:
                with st.spinner("ETF 데이터를 수집하는 중... ⏳"):            
                    analyzer.save_etf_data()  # 인스턴스에서 메서드 호출
                st.session_state["etf_loaded"] = True  # 데이터 로드 완료 상태 변경

            # 트리맵으로 변경
            analyzer.visualize_etf()  # 트리맵 시각화

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

        if st.session_state["page"] == "economic_data":
            st.title("경제 지표")

            collect_economic_data = collectEconomicData()

            #------------------ 최근 10년간 일별 국내 데이터 ------------------#
            start = (datetime.today() - relativedelta(years=10)).strftime("%Y%m%d")
            end = datetime.today().strftime("%Y%m%d")

            # 국고채(3년), 국고채(10년), 기준금리, KOSPI, KOSDAQ, 원/달러 환율
            daily_domestic_code_lst = [
                ("817Y002", "010200000"), ("817Y002", "010210000"), ("722Y001", "0101000"), ("802Y001", "0001000"),
                ("802Y001", "0089000"),
                ("731Y001", "0000001")
            ]
            freq = "D"  # 일별

            dataset_daily = collect_economic_data.daily_domestic(start, end, daily_domestic_code_lst, freq)
            st.subheader("일별 국내 데이터")
            st.write(dataset_daily)

            # ------------------ 최근 10년간 월별 국내 데이터 ------------------#
            start = (datetime.today() - relativedelta(years=10)).strftime("%Y%m")
            end = datetime.today().strftime("%Y%m")
            code_lst = [
                ("901Y027", "I61BC/I28B"), ("901Y027", "I61E/I28B"), ("901Y009", "0"), ("404Y014", "*AA"),
                ("301Y017", "SA000"),
                ("901Y093", "H69A/R70A"), ("901Y094", "H69A/R70A"), ("901Y095", "H69A/R70A"), ("901Y089", "100")
            ]  # 실업률, 고용률, CPI, PPI, 경상수지, 주택가격지수
            freq = "M"  # 월별

            dataset_monthly = collect_economic_data.monthly_domestic(start, end, code_lst, freq)
            st.subheader("월별 국내 데이터")
            st.write(dataset_monthly)

        if st.session_state["page"] == "my_page":
            st.title("👤 마이페이지")

            user = self.user_manager.get_user_info(st.session_state["id"])
            if not user:
                st.error("⚠️ 사용자 정보를 불러올 수 없습니다. 다시 로그인해 주세요.")
                st.session_state["logged_in"] = False
                st.session_state["page"] = "login"
                st.rerun()
                return

            # 상태 변수 초기화
            if "editing_user_info" not in st.session_state:
                st.session_state["editing_user_info"] = False

            if not st.session_state["editing_user_info"]:
                # 수정 전 기본 화면
                st.subheader("📌 내 계정 정보")
                st.write(f"**아이디:** {user['username']}")
                st.write(f"**비밀번호:** {'•' * len(user['password'])}")
                st.write(f"**계좌 번호:** {user['account_no']}")

                if st.button("정보 수정"):
                    st.session_state["editing_user_info"] = True
                    st.rerun()

            else:
                # 수정 폼
                st.subheader("📌 내 계정 정보 수정")

                with st.form("edit_user_info"):
                    st.text_input("아이디", value=user["username"], disabled=True)
                    new_password = st.text_input("비밀번호", type="password", value=user["password"])
                    new_account_no = st.text_input("계좌 번호", value=user["account_no"])
                    new_api_key = st.text_input("한국투자증권 APP Key", value=user["api_key"])
                    new_api_secret = st.text_input("한국투자증권 APP Secret", value=user["api_secret"])

                    col1, col2 = st.columns(2)
                    with col1:
                        save = st.form_submit_button("저장")
                    with col2:
                        cancel = st.form_submit_button("취소")

                if save:
                    updated_data = {
                        "password": new_password,
                        "account_no": new_account_no,
                        "api_key": new_api_key,
                        "api_secret": new_api_secret
                    }
                    self.user_manager.update_user_info(user["username"], updated_data)
                    st.success("✅ 정보가 성공적으로 수정되었습니다!")
                    st.session_state["editing_user_info"] = False
                    st.rerun()

                elif cancel:
                    st.session_state["editing_user_info"] = False
                    st.rerun()


if __name__ == "__main__":
    app = App()
    app.run()
