import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from modules.user_manager import UserManager
from modules.account_manager import AccountManager
from modules.visualization import Visualization
from modules.etf import ETFAnalyzer
from modules.etf_kr import ETFAnalyzer as ETFAnalyzerKR
from modules.crawling_article import crawlingArticle
from modules.collect_economic_data import collectEconomicData
from modules.chatbot_question import chatbot_page
from modules.chatbot_report import chatbot_page2
from modules.mypage import MyPage
from modules.AI_report import chatbot_page3, chatbot_page4
from modules.backtest import main as backtest_page

# 페이지 설정
st.set_page_config(
    page_title="Fynai - AI 기반 자산 관리 대시보드",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .logo-img {
        max-width: 200px;
        margin-bottom: 1rem;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
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
</style>
""", unsafe_allow_html=True)

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
        if "etf_us_loaded" not in st.session_state:  # 미국 ETF 데이터 로드 상태
            st.session_state["etf_us_loaded"] = False
        if "etf_kr_loaded" not in st.session_state:  # 한국 ETF 데이터 로드 상태
            st.session_state["etf_kr_loaded"] = False
        if "article_loaded" not in st.session_state:
            st.session_state["article_loaded"] = False
            
        # LLM 세션 상태 추가
        if "question_llm" not in st.session_state:
            st.session_state["question_llm"] = None
        if "report_llm" not in st.session_state:
            st.session_state["report_llm"] = None
        if "chat_memory" not in st.session_state:
            st.session_state["chat_memory"] = None

        # Supabase 사용자 관리
        self.user_manager = UserManager()

    def run(self):
        # 사이드바 추가
        if st.session_state["logged_in"]:
            st.sidebar.title("📌 메뉴")
            menu = st.sidebar.radio("메뉴 선택", [
                "💰 자산 현황",
                "👤 투자 프로필",
                "📊 ETF 분석",
                "📰 금융 뉴스",
                "📑 자산 진단",
                "🤖 AI 어드바이저",
                "📈 백테스팅",
                "로그아웃"
            ])
            
            if menu == "💰 자산 현황":
                st.session_state["page"] = "main"
            if menu == "👤 투자 프로필":
                st.session_state["page"] = "my_page"
            elif menu == "📊 ETF 분석":
                st.session_state["page"] = "etf_analysis"
            elif menu == "📰 금융 뉴스":
                st.session_state["page"] = "economic_news"
            elif menu == "🤖 AI 어드바이저":
                st.session_state["page"] = "chatbot"
            elif menu == "📑 자산 진단":
                st.session_state["page"] = "portfolio_report"
            elif menu == "📈 백테스팅":
                st.session_state["page"] = "backtest"
            elif menu == "로그아웃":
                st.session_state.clear()
                st.session_state["page"] = "login"
                st.rerun()

        # 로그인 페이지
        if st.session_state["page"] == "login":
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown('<div class="main-header">', unsafe_allow_html=True)
                st.image("assets/Fynai.png", use_column_width=True)
                st.markdown('<h1 class="main-title">Fynai</h1>', unsafe_allow_html=True)
                st.markdown('<p class="sub-title">AI 기반 스마트 자산 관리 솔루션</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            self.user_manager.login()

        # 회원가입 페이지
        if st.session_state["page"] == "sign_up":
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown('<div class="main-header">', unsafe_allow_html=True)
                st.image("assets/Fynai.png", use_column_width=True)
                st.markdown('<h1 class="main-title">Fynai</h1>', unsafe_allow_html=True)
                st.markdown('<p class="sub-title">AI 기반 스마트 자산 관리 솔루션</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            self.user_manager.sign_up()

        # 메인 페이지 (자산 관리)
        if st.session_state["page"] == "main":
            st.markdown('<div class="main-header">', unsafe_allow_html=True)
            st.image("assets/Fynai.png", width=150)
            st.markdown('<h1 class="main-title">자산 현황</h1>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

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
                # 사용자 정보 가져오기
                user = self.user_manager.get_user_info(st.session_state["id"])
                financial_data = user.get("personal", {}).get("financial", {}) if user else {}

                # 자산 데이터 준비
                asset_data = {
                    "현금": float(financial_data.get("cash", 0)),
                    "비상금": float(financial_data.get("emergency_fund", 0)),
                    "예/적금": float(financial_data.get("savings", 0)),
                    "펀드/ETF": float(financial_data.get("funds", 0)),
                    "부동산": float(financial_data.get("real_estate", 0)),
                    "연금/보험": float(financial_data.get("pension", 0)),
                    "코인/기타 자산": float(financial_data.get("other_assets", 0))
                }
                
                # 주식 데이터 추가
                if st.session_state["stock_df"] is not None:
                    for _, stock in st.session_state["stock_df"].iterrows():
                        asset_data[stock["상품명"]] = float(stock["평가금액"])

                # 총자산 계산
                total = sum(v for v in asset_data.values() if v > 0)
                profit = int(st.session_state["account_df"].loc[0, '평가손익합계금액'])

                st.title("📜 나의 포트폴리오")
                st.metric("총자산", f"{int(total):,}원",
                          f"{int(st.session_state['account_df'].loc[0, '평가손익합계금액']):,}원  |  " \
                          f"{round(profit / (total - profit) * 100, 2):,.2f}%")

                # 통합 자산 도넛 차트 시각화
                visualization = Visualization(st.session_state["stock_df"],
                                              st.session_state["account_df"],
                                              st.session_state["cash"])

                # 통합 자산 도넛 차트 시각화
                visualization.integrated_assets_doughnut_chart(financial_data)




        # ETF 분석 페이지 (트리맵 적용)
        if st.session_state["page"] == "etf_analysis":
            st.title("📊 ETF 섹터 분석")
            
            # 스타일 적용
            st.markdown("""
                <style>
                    .stTabs {
                        background-color: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .stTab {
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        margin: 5px;
                        padding: 10px;
                    }
                    .stTab:hover {
                        background-color: #e9ecef;
                    }
                    div[data-baseweb="tab-list"] {
                        gap: 10px;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # 탭 생성
            tab_us, tab_kr = st.tabs(["🌎 미국 S&P500", "🌏 한국 KOSPI"])
            
            with tab_us:
                analyzer = ETFAnalyzer()  # 미국 ETF 분석기
                if not st.session_state.get("etf_us_loaded"):
                    with st.spinner("미국 ETF 데이터를 수집하는 중... ⏳"):            
                        analyzer.save_etf_data()
                    st.session_state["etf_us_loaded"] = True
                    st.success("미국 ETF 데이터 로드 완료!")
                analyzer.visualize_etf()
            
            with tab_kr:
                analyzer_kr = ETFAnalyzerKR()  # 한국 ETF 분석기
                if not st.session_state.get("etf_kr_loaded"):
                    with st.spinner("한국 ETF 데이터를 수집하는 중... ⏳"):            
                        analyzer_kr.save_etf_data()
                    st.session_state["etf_kr_loaded"] = True
                    st.success("한국 ETF 데이터 로드 완료!")
                analyzer_kr.visualize_etf()

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
 

        # 챗봇 페이지
        if st.session_state["page"] == "chatbot":
            chatbot_page()

        # 포트폴리오 보고서 페이지
        if st.session_state["page"] == "portfolio_report":
            personal, macro, real_estate = st.tabs(["📊 개인 포트폴리오 분석 리포트", "🌐 거시경제 동향 리포트", "🏠 부동산 동향 리포트"])

            with personal:
                st.subheader("개인 포트폴리오 분석")
                chatbot_page2()

            with macro:
                chatbot_page3()

            with real_estate:
                chatbot_page4()

        if st.session_state["page"] == "my_page":
                my_page = MyPage()
                my_page.show()

        # 백테스팅 페이지
        if st.session_state["page"] == "backtest":
            backtest_page()


if __name__ == "__main__":
    app = App()
    app.run()