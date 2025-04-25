import streamlit as st
from modules.DB import SupabaseDB
import json

class MyPage:
    def __init__(self):
        self.db = SupabaseDB()
        if "editing_mode" not in st.session_state:
            st.session_state["editing_mode"] = False

    def show(self):
        # 페이지 제목과 설명
        st.title("👤 마이페이지")
        st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
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
        .section-title {
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .masked-text {
            font-family: monospace;
            letter-spacing: 2px;
        }
        </style>
        """, unsafe_allow_html=True)

        # 사용자 정보 가져오기
        user = self.db.get_user(st.session_state["id"])
        if not user:
            st.error("사용자 정보를 찾을 수 없습니다.")
            return

        user = user[0]
        personal_data = user.get("personal", {})
        financial_data = personal_data.get("financial", {})
        investment_profile = personal_data.get("investment_profile", {})

        if st.session_state["editing_mode"]:
            # 수정 모드 UI
            tab1, tab2, tab3 = st.tabs(["🔑 계정 정보", "💰 재무 정보", "🧠 투자 성향"])
            
            with tab1:
                with st.container():
                    st.markdown('<div class="section-title">계정 정보</div>', unsafe_allow_html=True)
                    username = st.text_input("아이디", value=user.get("username", ""))
                    password = st.text_input("비밀번호", value="", type="password")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">API 정보</div>', unsafe_allow_html=True)
                    api_key = st.text_input("한국투자증권 APP Key", value=user.get("api_key", ""), type="password")
                    api_secret = st.text_input("APP Secret", value=user.get("api_secret", ""), type="password")
                    account_no = st.text_input("계좌번호", value=user.get("account_no", ""))
                    mock = st.checkbox("모의투자 계좌입니다", value=user.get("mock", False))
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                with st.container():
                    st.markdown('<div class="section-title">현금 흐름</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        monthly_income = st.number_input("월 실수령 수입 (만원)", value=float(financial_data.get("monthly_income", 0))/10000, step=1.0) * 10000
                    with col2:
                        fixed_expenses = st.number_input("고정 지출 (만원)", value=float(financial_data.get("fixed_expenses", 0))/10000, step=1.0) * 10000
                    with col3:
                        variable_expenses = st.number_input("변동 지출 (만원)", value=float(financial_data.get("variable_expenses", 0))/10000, step=1.0) * 10000
                    monthly_savings = monthly_income - fixed_expenses - variable_expenses

                    st.markdown('<div class="section-title">부채 현황</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_debt = st.number_input("총 부채 금액 (만원)", value=float(financial_data.get("total_debt", 0))/10000, step=1.0) * 10000
                    with col2:
                        monthly_debt_payment = st.number_input("월 부채 상환액 (만원)", value=float(financial_data.get("monthly_debt_payment", 0))/10000, step=1.0) * 10000
                    with col3:
                        average_interest_rate = st.number_input("평균 이자율 (%)", value=float(financial_data.get("average_interest_rate", 0)), step=0.1)

                    st.markdown('<div class="section-title">보유 자산</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        cash = st.number_input("현금 (만원)", value=float(financial_data.get("cash", 0))/10000, step=1.0) * 10000
                        emergency_fund = st.number_input("비상금 (만원)", value=float(financial_data.get("emergency_fund", 0))/10000, step=1.0) * 10000
                        savings = st.number_input("예/적금 (만원)", value=float(financial_data.get("savings", 0))/10000, step=1.0) * 10000
                        funds = st.number_input("펀드/ETF (만원)", value=float(financial_data.get("funds", 0))/10000, step=1.0) * 10000
                    with col2:
                        real_estate = st.number_input("부동산 (억원)", value=float(financial_data.get("real_estate", 0))/100000000, step=0.1) * 100000000
                        pension = st.number_input("연금/보험 (만원)", value=float(financial_data.get("pension", 0))/10000, step=1.0) * 10000
                        other_assets = st.number_input("코인/기타 자산 (만원)", value=float(financial_data.get("other_assets", 0))/10000, step=1.0) * 10000

                    st.markdown('<div class="section-title">재무 목표</div>', unsafe_allow_html=True)
                    short_term_goal = st.text_input("단기 목표 (1~2년)", value=financial_data.get("short_term_goal", ""))
                    mid_term_goal = st.text_input("중기 목표 (3~5년)", value=financial_data.get("mid_term_goal", ""))
                    long_term_goal = st.text_input("장기 목표 (10년 이상)", value=financial_data.get("long_term_goal", ""))

                    st.markdown('<div class="section-title">기타 변수</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        age = st.number_input("현재 나이", value=financial_data.get("age", 0), step=1)
                        family_structure = st.selectbox("가족 구성", ["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"], 
                                                      index=["싱글", "기혼", "기혼+자녀1", "기혼+자녀2", "기혼+자녀3+"].index(financial_data.get("family_structure", "싱글")))
                    with col2:
                        retirement_age = st.number_input("은퇴 예정 연령", value=financial_data.get("retirement_age", 65), step=1)
                        housing_type = st.selectbox("주거 형태", ["자가", "전세", "월세"], 
                                                  index=["자가", "전세", "월세"].index(financial_data.get("housing_type", "자가")))

            with tab3:
                with st.container():
                    st.markdown('<div class="section-title">투자 성향</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        age_group = st.selectbox("연령대", ["20~39세", "40~49세", "50~65세", "66~79세", "80세 이상"],
                                               index=["20~39세", "40~49세", "50~65세", "66~79세", "80세 이상"].index(investment_profile.get("age_group", "20~39세")))
                        investment_horizon = st.selectbox("투자 가능 기간", ["5년 이상", "3~5년", "2~3년", "1~2년", "1년 미만"],
                                                        index=["5년 이상", "3~5년", "2~3년", "1~2년", "1년 미만"].index(investment_profile.get("investment_horizon", "5년 이상")))
                        investment_experience = st.radio("투자경험", ["적음", "보통", "많음"],
                                                       index=["적음", "보통", "많음"].index(investment_profile.get("investment_experience", "적음")))
                    with col2:
                        knowledge_level = st.radio("금융지식 수준/이해도", ["투자 경험 없음", "일부 이해함", "깊이 있게 이해함"],
                                                 index=["투자 경험 없음", "일부 이해함", "깊이 있게 이해함"].index(investment_profile.get("knowledge_level", "투자 경험 없음")))
                        return_tolerance = st.radio("기대 이익수준 및 손실감내 수준", 
                                                  ["무조건 원금 보전", "원금 기준 ±5%", "원금 기준 ±10%", "원금 기준 ±20%", "원금 기준 ±20% 초과"],
                                                  index=["무조건 원금 보전", "원금 기준 ±5%", "원금 기준 ±10%", "원금 기준 ±20%", "원금 기준 ±20% 초과"].index(investment_profile.get("return_tolerance", "무조건 원금 보전")))
                    investment_style = st.selectbox("투자성향", ["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"],
                                                  index=["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"].index(investment_profile.get("investment_style", "안정형")))
                    investment_goal = st.multiselect("투자목표", ["예적금 수준 수익", "시장 평균 이상 수익", "적극적인 자산 증식", "생계자금 운용"],
                                                   default=investment_profile.get("investment_goal", []))
                    preferred_assets = st.multiselect("선호 자산군", ["주식", "부동산", "예적금", "외화", "금", "암호화폐", "기타"],
                                                    default=investment_profile.get("preferred_assets", []))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("저장", type="primary"):
                    # 재무 정보
                    financial_data = {
                        "monthly_income": monthly_income,
                        "fixed_expenses": fixed_expenses,
                        "variable_expenses": variable_expenses,
                        "monthly_savings": monthly_savings,
                        "total_debt": total_debt,
                        "monthly_debt_payment": monthly_debt_payment,
                        "average_interest_rate": average_interest_rate,
                        "cash": cash,
                        "emergency_fund": emergency_fund,
                        "savings": savings,
                        "funds": funds,
                        "real_estate": real_estate,
                        "pension": pension,
                        "other_assets": other_assets,
                        "short_term_goal": short_term_goal,
                        "mid_term_goal": mid_term_goal,
                        "long_term_goal": long_term_goal,
                        "age": age,
                        "family_structure": family_structure,
                        "retirement_age": retirement_age,
                        "housing_type": housing_type
                    }

                    # 투자 성향
                    investment_profile = {
                        "age_group": age_group,
                        "investment_horizon": investment_horizon,
                        "investment_experience": investment_experience,
                        "knowledge_level": knowledge_level,
                        "return_tolerance": return_tolerance,
                        "investment_style": investment_style,
                        "investment_goal": investment_goal,
                        "preferred_assets": preferred_assets
                    }

                    # 모든 정보를 personal 필드에 통합
                    personal_data = {
                        "financial": financial_data,
                        "investment_profile": investment_profile
                    }

                    # DB 업데이트
                    updated_data = {
                        "username": username,
                        "password": password if password else user.get("password", ""),
                        "api_key": api_key if api_key else user.get("api_key", ""),
                        "api_secret": api_secret if api_secret else user.get("api_secret", ""),
                        "account_no": account_no,
                        "mock": mock,
                        "personal": personal_data
                    }

                    # 사용자 정보 업데이트
                    self.db.update_user_info(st.session_state["id"], updated_data)
                    st.success("✅ 정보가 성공적으로 저장되었습니다!")
                    st.session_state["editing_mode"] = False
                    st.rerun()
            with col2:
                if st.button("취소", type="secondary"):
                    st.session_state["editing_mode"] = False
                    st.rerun()
        else:
            # 읽기 모드 UI
            tab1, tab2, tab3 = st.tabs(["🔑 계정 정보", "💰 재무 정보", "🧠 투자 성향"])
            
            with tab1:
                with st.container():
                    st.markdown('<div class="section-title">계정 정보</div>', unsafe_allow_html=True)
                    st.write(f"**아이디:** {user.get('username', '')}")
                    st.write(f"**비밀번호:** {'*' * 8}")
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">API 정보</div>', unsafe_allow_html=True)
                    st.write(f"**한국투자증권 APP Key:** {'*' * 8}")
                    st.write(f"**APP Secret:** {'*' * 8}")
                    st.write(f"**계좌번호:** {user.get('account_no', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                with st.container():
                    st.markdown('<div class="section-title">현금 흐름</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("월 실수령 수입", f"{int(financial_data.get('monthly_income', 0)):,}원")
                    with col2:
                        st.metric("고정 지출", f"{int(financial_data.get('fixed_expenses', 0)):,}원")
                    with col3:
                        st.metric("변동 지출", f"{int(financial_data.get('variable_expenses', 0)):,}원")
                    st.metric("월 평균 저축 가능액", f"{int(financial_data.get('monthly_savings', 0)):,}원", 
                             delta=f"{int(financial_data.get('monthly_savings', 0) - financial_data.get('fixed_expenses', 0) - financial_data.get('variable_expenses', 0)):,}원")

                    st.markdown('<div class="section-title">부채 현황</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("총 부채 금액", f"{int(financial_data.get('total_debt', 0)):,}원")
                    with col2:
                        st.metric("월 부채 상환액", f"{int(financial_data.get('monthly_debt_payment', 0)):,}원")
                    with col3:
                        st.metric("평균 이자율", f"{financial_data.get('average_interest_rate', 0)}%")

                    st.markdown('<div class="section-title">보유 자산</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("현금", f"{int(financial_data.get('cash', 0))/10000:,.0f}만원")
                        st.metric("비상금", f"{int(financial_data.get('emergency_fund', 0))/10000:,.0f}만원")
                        st.metric("예/적금", f"{int(financial_data.get('savings', 0))/10000:,.0f}만원")
                        st.metric("펀드/ETF", f"{int(financial_data.get('funds', 0))/10000:,.0f}만원")
                    with col2:
                        st.metric("부동산", f"{int(financial_data.get('real_estate', 0))/100000000:,.1f}억원")
                        st.metric("연금/보험", f"{int(financial_data.get('pension', 0))/10000:,.0f}만원")
                        st.metric("코인/기타 자산", f"{int(financial_data.get('other_assets', 0))/10000:,.0f}만원")

                    st.markdown('<div class="section-title">재무 목표</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**단기 목표 (1~2년):**")
                        st.info(financial_data.get('short_term_goal', ''))
                    with col2:
                        st.write(f"**중기 목표 (3~5년):**")
                        st.info(financial_data.get('mid_term_goal', ''))
                    with col3:
                        st.write(f"**장기 목표 (10년 이상):**")
                        st.info(financial_data.get('long_term_goal', ''))

                    st.markdown('<div class="section-title">기타 변수</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("현재 나이", f"{financial_data.get('age', '')}세")
                        st.metric("가족 구성", financial_data.get('family_structure', ''))
                    with col2:
                        st.metric("은퇴 예정 연령", f"{financial_data.get('retirement_age', '')}세")
                        st.metric("주거 형태", financial_data.get('housing_type', ''))

            with tab3:
                with st.container():
                    st.markdown('<div class="section-title">투자 성향</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("연령대", investment_profile.get('age_group', ''))
                        st.metric("투자 가능 기간", investment_profile.get('investment_horizon', ''))
                        st.metric("투자경험", investment_profile.get('investment_experience', ''))
                    with col2:
                        st.metric("금융지식 수준", investment_profile.get('knowledge_level', ''))
                        st.metric("손실감내 수준", investment_profile.get('return_tolerance', ''))
                        st.metric("투자성향", investment_profile.get('investment_style', ''))
                    
                    st.write("**투자목표:**")
                    for goal in investment_profile.get('investment_goal', []):
                        st.info(goal)
                    
                    st.write("**선호 자산군:**")
                    for asset in investment_profile.get('preferred_assets', []):
                        st.info(asset)

            if st.button("정보 수정", type="primary"):
                st.session_state["editing_mode"] = True
                st.rerun()
