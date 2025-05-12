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
from modules.llm_models.market_headline import MarketHeadlineLLM
from modules.llm_models.portfolio_alert import PortfolioAlertLLM
from modules.llm_models.risk_warning import RiskWarningLLM
from modules.llm_models.action_required import ActionRequiredLLM
from modules.llm_models.data_processor import DataProcessor
from modules.email_sender import EmailSender

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
    .feature-container {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        text-align: center;
        position: relative;
    }
    .feature-grid {
        display: flex;
        gap: 1rem;
        justify-content: center;
        align-items: stretch;
        padding: 1rem 0;
    }
    .feature-item {
        flex: 0 0 160px;
        height: 160px;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    }
    .feature-item:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    .feature-icon {
        font-size: 2rem;
        width: 50px;
        height: 50px;
        line-height: 50px;
        border-radius: 10px;
        margin: 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
    }
    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        margin: 0.5rem 0;
        padding-bottom: 0.3rem;
        text-align: center;
        color: #2E4057;
    }
    .feature-description {
        font-size: 0.8rem;
        line-height: 1.3;
        text-align: center;
        color: #666;
        margin: 0;
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
    .strategy-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .strategy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #4CAF50;
    }
    .strategy-card.selected {
        border-color: #4CAF50;
        background: #f8fff8;
    }
    .strategy-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    .strategy-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2E4057;
        margin-bottom: 10px;
    }
    .strategy-description {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.5;
    }
    .strategy-features {
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #eee;
    }
    .strategy-feature {
        display: flex;
        align-items: center;
        margin: 8px 0;
        color: #555;
    }
    .strategy-feature-icon {
        margin-right: 8px;
        color: #4CAF50;
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
                "🧪 LLM 테스트",
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
            elif menu == "🧪 LLM 테스트":
                st.session_state["page"] = "llm_test"
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
            if "current_feature" not in st.session_state:
                st.session_state.current_feature = 0

            features = [
                {
                    "icon": "💼",
                    "title": "통합 자산 관리",
                    "description": "실시간 포트폴리오 모니터링<br>주식, ETF, 현금 자산의 통합 관리",
                    "color": "#4CAF50"
                },
                {
                    "icon": "📊",
                    "title": "ETF 마켓 인사이트",
                    "description": "글로벌 ETF 분석<br>섹터별 성과 시각화",
                    "color": "#2196F3"
                },
                {
                    "icon": "📰",
                    "title": "뉴스 & 마켓 인텔리전스",
                    "description": "실시간 경제 뉴스 분석<br>키워드 트렌드 분석",
                    "color": "#FF9800"
                },
                {
                    "icon": "📑",
                    "title": "자산 진단 리포트",
                    "description": "맞춤형 포트폴리오 분석<br>자산 배분 최적화 제안",
                    "color": "#00BCD4"
                },
                {
                    "icon": "📧",
                    "title": "일일 인사이트 메일",
                    "description": "맞춤형 일일 리포트<br>투자 리스크 및 주의사항 안내",
                    "color": "#FF5722"
                },
                {
                    "icon": "🤖",
                    "title": "AI 어드바이저",
                    "description": "맞춤형 투자 상담<br>포트폴리오 분석 및 개선 제안",
                    "color": "#795548"
                },
                {
                    "icon": "📈",
                    "title": "백테스팅 시스템",
                    "description": "투자 전략 검증<br>과거 데이터 기반 시뮬레이션",
                    "color": "#607D8B"
                }
            ]

            # 모든 카드 표시
            cols = st.columns(7)
            for idx, feature in enumerate(features):
                with cols[idx]:
                    st.markdown(f'''
                        <div class="feature-item">
                            <div class="feature-icon" style="color: {feature['color']};">{feature['icon']}</div>
                            <div class="feature-title" style="--accent-color: {feature['color']};">{feature['title']}</div>
                            <div class="feature-description">{feature['description']}</div>
                        </div>
                    ''', unsafe_allow_html=True)

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

            # 워드 클라우드 시각화
            crawaling_article.visualize_wordcloud()
            
            # 뉴스 기사 데이터프레임
            article = crawaling_article.load_article()
            st.write(article)
 

        # 챗봇 페이지
        if st.session_state["page"] == "chatbot":
            chatbot_page()

        # 포트폴리오 보고서 페이지
        if st.session_state["page"] == "portfolio_report":
            personal, macro, real_estate = st.tabs(["📊 개인 포트폴리오 분석 리포트", "🌐 거시경제 동향 리포트", "🏠 부동산 동향 리포트"])

            with personal:
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
            st.title("📈 백테스팅 시스템")
            
            # 전략이 선택되지 않은 경우에만 카드 표시
            if "selected_strategy" not in st.session_state:
                # 전략 선택 UI 스타일 추가
                st.markdown("""
                <style>
                    .strategy-container {
                        display: flex;
                        gap: 20px;
                        margin: 20px 0;
                    }
                    .strategy-card {
                        flex: 1;
                        background: white;
                        border-radius: 15px;
                        padding: 25px;
                        border: 2px solid #e0e0e0;
                        transition: all 0.3s ease;
                        cursor: pointer;
                    }
                    .strategy-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                    }
                    .strategy-card.selected {
                        border-color: #4CAF50;
                        background: #f8fff8;
                        box-shadow: 0 8px 20px rgba(76,175,80,0.15);
                    }
                    .strategy-icon {
                        font-size: 2.5rem;
                        margin-bottom: 15px;
                        text-align: center;
                    }
                    .strategy-title {
                        font-size: 1.3rem;
                        font-weight: 600;
                        color: #2E4057;
                        margin-bottom: 10px;
                        text-align: center;
                    }
                    .strategy-description {
                        font-size: 1rem;
                        color: #666;
                        line-height: 1.6;
                        margin-bottom: 15px;
                    }
                    .strategy-features {
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 10px;
                        margin-top: 15px;
                    }
                    .strategy-feature {
                        display: flex;
                        align-items: center;
                        margin: 10px 0;
                        color: #555;
                        font-size: 0.95rem;
                    }
                    .strategy-feature-icon {
                        margin-right: 10px;
                        color: #4CAF50;
                        font-size: 1.1rem;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # 전략 선택 컨테이너
                st.markdown('<div class="strategy-container">', unsafe_allow_html=True)
                
                # 전략 1: 이동평균선 교차
                st.markdown(f"""
                <div class="strategy-card" onclick="document.querySelector('[data-testid=stButton] button').click()">
                    <div class="strategy-icon">📈</div>
                    <div class="strategy-title">이동평균선 교차 전략</div>
                    <div class="strategy-description">
                        단기와 장기 이동평균선의 교차를 이용한 추세 추종 전략입니다. 
                        시장의 추세를 따라가는 전략으로, 장기적인 추세가 있을 때 효과적입니다.
                    </div>
                    <div class="strategy-features">
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">📊</span>
                            MA20과 MA60 이동평균선 사용
                        </div>
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">🟢</span>
                            골든 크로스(MA20 > MA60): 매수
                        </div>
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">🔴</span>
                            데드 크로스(MA20 < MA60): 매도
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("이동평균선 교차 전략 선택", key="ma_strategy", use_container_width=True):
                    st.session_state["selected_strategy"] = "이동평균선 교차"
                    st.rerun()
                
                # 전략 2: 볼린저 밴드
                st.markdown(f"""
                <div class="strategy-card" onclick="document.querySelector('[data-testid=stButton] button').click()">
                    <div class="strategy-icon">🎯</div>
                    <div class="strategy-title">볼린저 밴드 전략</div>
                    <div class="strategy-description">
                        가격의 변동성을 이용한 평균 회귀 전략입니다.
                        주가가 과매수/과매도 구간에 도달했을 때 반전을 예상하는 전략입니다.
                    </div>
                    <div class="strategy-features">
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">📊</span>
                            20일 이동평균선 ±2표준편차
                        </div>
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">🟢</span>
                            하단밴드 터치: 매수
                        </div>
                        <div class="strategy-feature">
                            <span class="strategy-feature-icon">🔴</span>
                            상단밴드 터치: 매도
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("볼린저 밴드 전략 선택", key="bb_strategy", use_container_width=True):
                    st.session_state["selected_strategy"] = "볼린저 밴드"
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # 전략이 선택된 경우
                strategy = st.session_state["selected_strategy"]
                
                # 전략 변경 버튼
                if st.button("🔄 전략 변경하기", type="secondary"):
                    del st.session_state["selected_strategy"]
                    st.rerun()
                
                # 선택된 전략 표시
                st.success(f"선택된 전략: {strategy}")
                
                # 백테스팅 실행
                from modules.backtest import main as backtest_main
                backtest_main(strategy=strategy)
        elif st.session_state["page"] == "llm_test":
            self.llm_test_page()

    def llm_test_page(self):
        st.title("🧪 LLM 모델 테스트")
        
        # session_state 초기화
        if "market_headline" not in st.session_state:
            st.session_state.market_headline = ""
        if "portfolio_alert" not in st.session_state:
            st.session_state.portfolio_alert = ""
        if "risk_warning" not in st.session_state:
            st.session_state.risk_warning = ""
        if "action_required" not in st.session_state:
            st.session_state.action_required = ""
        
        # 사용자 ID 입력
        user_id = st.text_input("사용자 ID를 입력하세요", value="test")
        
        # 현재 날짜 가져오기
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        # 데이터 프로세서 초기화
        data_processor = DataProcessor(user_id)

        # 🔽🔽🔽 여기서부터 추가 🔽🔽🔽
        st.markdown("---")
        st.subheader("📝 개인 리포트 일괄 생성(DB저장)")
        if st.button("개인 리포트 전체 생성 및 DB 저장", type="primary"):
            from individual_report import save_individual_report
            with st.spinner("모든 사용자의 개인 리포트를 생성하여 DB에 저장 중입니다..."):
                save_individual_report()
            st.success("✅ 전체 개인 리포트가 DB에 저장되었습니다!")
        # 🔼🔼🔼 여기까지 추가 🔼🔼🔼

        # 모든 모델 결과를 한 번에 생성하는 버튼
        if st.button("모든 LLM 모델 실행하기", type="primary"):
            # 컨테이너 생성
            with st.container():
                # 4개의 컬럼 생성
                col1, col2, col3, col4 = st.columns(4)
                
                # 1. 시장 헤드라인
                with col1:
                    st.subheader("📰 시장 헤드라인")
                    with st.spinner("시장 헤드라인 생성 중..."):
                        market_data = data_processor.get_market_data()
                        model = MarketHeadlineLLM()
                        st.session_state.market_headline = model.generate(**market_data, current_date=current_date)
                        st.success(st.session_state.market_headline)
                
                # 2. 포트폴리오 알림
                with col2:
                    st.subheader("💼 포트폴리오 알림")
                    with st.spinner("포트폴리오 알림 생성 중..."):
                        portfolio_data = data_processor.get_portfolio_data()
                        model = PortfolioAlertLLM()
                        st.session_state.portfolio_alert = model.generate(**portfolio_data, current_date=current_date)
                        st.success(st.session_state.portfolio_alert)
                
                # 3. 리스크 경고
                with col3:
                    st.subheader("⚠️ 리스크 경고")
                    with st.spinner("리스크 경고 생성 중..."):
                        risk_data = data_processor.get_risk_data()
                        model = RiskWarningLLM()
                        st.session_state.risk_warning = model.generate(**risk_data, current_date=current_date)
                        st.success(st.session_state.risk_warning)
                
                # 4. 투자 액션
                with col4:
                    st.subheader("🎯 투자 액션")
                    with st.spinner("투자 액션 생성 중..."):
                        investment_data = data_processor.get_investment_data()
                        model = ActionRequiredLLM()
                        st.session_state.action_required = model.generate(**investment_data, current_date=current_date)
                        st.success(st.session_state.action_required)

        # 이메일 발송 섹션
        st.markdown("---")
        st.subheader("📧 이메일 발송")
        
        # 이메일 주소 입력
        user_email = st.text_input("이메일 주소를 입력하세요")
        
        # 이메일 발송 버튼
        if st.button("이메일 발송하기"):
            if not user_email:
                st.error("이메일 주소를 입력해주세요.")
                return
                
            if not all([st.session_state.market_headline, 
                       st.session_state.portfolio_alert, 
                       st.session_state.risk_warning, 
                       st.session_state.action_required]):
                st.error("먼저 '모든 LLM 모델 실행하기' 버튼을 눌러 알림을 생성해주세요.")
                return
            
            # 이메일 발송
            email_sender = EmailSender()
            if email_sender.send_daily_alerts(
                user_email, 
                st.session_state.market_headline,
                st.session_state.portfolio_alert,
                st.session_state.risk_warning,
                st.session_state.action_required
            ):
                st.success("이메일이 성공적으로 발송되었습니다!")
            else:
                st.error("이메일 발송 중 오류가 발생했습니다.")

def backtest_page():
    st.title("📈 백테스팅 시스템")
    
    # 전략 선택
    strategy = st.radio(
        "📊 백테스팅 전략",
        ["이동평균선 교차", "볼린저 밴드"],
        horizontal=True
    )
    
    # 전략 설명
    if strategy == "이동평균선 교차":
        st.info("""
        **이동평균선 교차 전략**
        - 20일 이동평균선(MA20)과 60일 이동평균선(MA60)을 사용
        - 골든 크로스(MA20 > MA60): 매수 신호
        - 데드 크로스(MA20 < MA60): 매도 신호
        """)
    else:
        st.info("""
        **볼린저 밴드 전략**
        - 20일 이동평균선을 중심으로 상하 2표준편차 범위 설정
        - 하단밴드 터치: 매수 신호
        - 상단밴드 터치: 매도 신호
        """)
    
    # 백테스팅 실행
    backtest_page(strategy=strategy)

if __name__ == "__main__":
    app = App()
    app.run()