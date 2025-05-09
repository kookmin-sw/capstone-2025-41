import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os
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
from modules.AI_report import get_real_estate_report, get_macro_report
from modules.backtest import main as backtest_page
import base64

# 페이지 설정
st.set_page_config(
    page_title="Fynai - AI 기반 자산 관리 대시보드",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# 로고 이미지 경로 설정
LOGO_PATH = os.path.join("assets", "Fynai_white.png")

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0 2rem 0;
        margin-bottom: 0;
        background: linear-gradient(135deg, #2E4057 0%, #1a2634 100%);
        border-radius: 24px;
        margin-bottom: 3rem;
    }
    .logo-img {
        max-width: 180px;
        margin-bottom: 1rem;
        filter: drop-shadow(0 6px 12px rgba(0,0,0,0.18));
        border-radius: 18px;
        transition: transform 0.3s;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.8rem;
    }
    .sub-title {
        font-size: 1.3rem;
        color: #E0E0E0;
        margin-bottom: 1.5rem;
    }
    .landing-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    .feature-item {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
        border-left: 4px solid #4CAF50;
    }
    .feature-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.15);
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.8rem;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #2E4057;
    }
    .feature-description {
        font-size: 0.9rem;
        color: #495057;
        line-height: 1.4;
    }
    .auth-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 2rem;
    }
    .auth-button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 1.2rem 2.8rem;
        text-decoration: none;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1.2rem;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.13);
    }
    .auth-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def load_logo():
    try:
        if os.path.exists(LOGO_PATH):
            return get_base64_encoded_image(LOGO_PATH)
        else:
            st.error("로고 이미지를 찾을 수 없습니다.")
            return None
    except Exception as e:
        st.error(f"로고 로딩 중 오류가 발생했습니다: {str(e)}")
        return None

class App():
    def __init__(self):
        if "page" not in st.session_state:
            st.session_state["page"] = "landing"
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
                st.session_state["page"] = "landing"
                st.rerun()

        # 랜딩 페이지
        if st.session_state["page"] == "landing":
            logo_base64 = load_logo()
            st.markdown(f'''
            <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
                <div style="background: linear-gradient(135deg, #2E4057 0%, #1a2634 100%); padding: 4rem 0 1.5rem 0; border-radius: 0 0 24px 24px; margin-bottom: 3rem;">
                    <div style="text-align: center; max-width: 900px; margin: 0 auto;">
                        <img src="data:image/png;base64,{logo_base64}" alt="Fynai Logo" style="max-width: 240px; margin-bottom: 1.5rem; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.18)); border-radius: 18px; transition: transform 0.3s;">
                        <h1 style="color: white; font-size: 3.2rem; margin-bottom: 0.8rem; font-weight: 800;">Fynai</h1>
                        <p style="font-size: 1.5rem; color: #E0E0E0; margin-bottom: 1.5rem;">AI 기반 스마트 자산 관리 솔루션</p>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem;">
                        <div style="flex: 1; max-width: 200px;">
                            ''' , unsafe_allow_html=True)
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button('🔐 로그인', use_container_width=True):
                    st.session_state["page"] = "login"
                    st.rerun()
            with col2:
                if st.button('📝 회원가입', use_container_width=True):
                    st.session_state["page"] = "sign_up"
                    st.rerun()
            
            # 주요 기능 소개
            st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
            
            # 기능 1
            st.markdown('''
                <div class="feature-item">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">실시간 자산 분석</div>
                    <div class="feature-description">AI 기반 실시간 자산 분석<br>최적 투자 전략 제안</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # 기능 2
            st.markdown('''
                <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">AI 투자 어드바이저</div>
                    <div class="feature-description">맞춤형 투자 조언<br>포트폴리오 최적화</div>
                </div>
            ''', unsafe_allow_html=True)
            
            # 기능 3
            st.markdown('''
                <div class="feature-item">
                    <div class="feature-icon">📈</div>
                    <div class="feature-title">백테스팅 시스템</div>
                    <div class="feature-description">과거 데이터 기반<br>투자 전략 검증</div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

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

            with real_estate:
                get_real_estate_report()

            with macro:
                get_macro_report()

        if st.session_state["page"] == "my_page":
                my_page = MyPage()
                my_page.show()

        # 백테스팅 페이지
        if st.session_state["page"] == "backtest":
            backtest_page()


if __name__ == "__main__":
    app = App()
    app.run()