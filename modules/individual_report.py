import os
import streamlit as st
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from modules.tools import (
    get_asset_summary_text,
    get_economic_summary_text,
    get_owned_stock_summary_text
)

# .env 파일의 환경 변수 불러오기
load_dotenv()

def init_llm():
    api_key = os.getenv("GEMINI_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key
    )
    st.session_state["report_llm"] = llm
    return llm

def generate_section_content(llm, user_info, asset_summary, economic_summary, stock_summary):
    # user_info에서 필요한 데이터 추출
    personal_info = user_info.get("personal_info", {})
    investment_profile = user_info.get("investment_profile", {})
    investment_details = investment_profile.get("details", {})
    financial = user_info.get("financial", {})

    prompt = PromptTemplate.from_template("""
당신은 15년 경력의 자산관리 전문가이자 포트폴리오 매니저입니다.
당신의 주요 역할은 고객의 재무 상태를 종합적으로 분석하고, 맞춤형 자산관리 전략을 제시하는 것입니다.

[고객 기본 정보]
- 연령: {age}세
- 직업: {occupation}
- 가족구성: {family_structure}
- 은퇴 희망 연령: {retirement_age}세
- 거주형태: {housing_type}

[투자 성향 정보]
- 투자 성향: {investment_style}
- 투자 경험: {investment_experience}
- 투자 기간: {investment_horizon}
- 감내 가능 위험: {risk_tolerance}
- 기대 수익률: {expected_return}
- 투자 우선순위: {investment_priority}
- 금융지식 수준: {financial_knowledge}

[투자 목표]
- 단기 목표: {short_term_goal}
- 중기 목표: {mid_term_goal}
- 장기 목표: {long_term_goal}

[현금 흐름]
1. 수입/지출
   - 월 수입: {monthly_income:,}원
   - 고정 지출: {fixed_expenses:,}원
   - 변동 지출: {variable_expenses:,}원
   - 월 저축액: {monthly_savings:,}원

2. 부채 현황
   - 총 부채: {total_debt:,}원
   - 월 상환액: {monthly_debt_payment:,}원
   - 평균 이자율: {average_interest_rate}%
   - 주택담보대출: {mortgage:,}원
   - 개인대출: {personal_loan:,}원
   - 신용카드: {credit_card:,}원
   - 기타부채: {other_debt:,}원

[보유 자산]
1. 현금성 자산
   - 현금: {cash:,}원
   - 비상금: {emergency_fund:,}원
   - 예/적금: {savings:,}원

2. 투자 자산
   - 부동산: {real_estate:,}원
   - 펀드: {funds:,}원
   - ETF: {etfs:,}원
   - 가상화폐: {crypto:,}원
   - 주식: {stock_summary}, {asset_summary}

3. 보험/연금
   - 연금: {pension:,}원
   - 보험: {insurance:,}원

4. 외화 자산
   - USD: ${usd:,.2f}
   - EUR: €{eur:,.2f}
   - JPY: ¥{jpy:,.0f}
   - GBP: £{gbp:,.2f}
   - CNY: ¥{cny:,.2f}

[시장 환경]
{economic_summary}

[작성 가이드라인]
1. 전문성: 모든 분석과 제안은 객관적 데이터와 전문적 지표에 기반해야 합니다.
2. 실행가능성: 제시하는 모든 전략은 구체적이고 실현 가능해야 합니다.
3. 맞춤화: 고객의 상황과 성향을 고려한 개인화된 제안이어야 합니다.
4. 위험관리: 잠재적 위험요소를 명확히 식별하고 대응 방안을 제시해야 합니다.
5. 이해용이성: 전문 용어는 반드시 쉬운 설명을 덧붙여야 합니다.

[필수 포함 요소]
각 섹션은 반드시 [섹션명]으로 시작하며, 다음 내용을 포함해야 합니다:

1. [요약 섹션]
   - 고객 프로필 요약 (연령, 직업, 자산규모)
   - 투자 성향 분석
   - 핵심 제안사항 (3가지 이내)

2. [마이데이터 분석]
   - 자산 구성 분석 (항목별 비중)
   - 현금흐름 분석 (월간 수입/지출)
   - 부채 현황 (총액, 이자율, 상환계획)
   - 투자자산 성과 분석

3. [재무 건전성 평가]
   - 핵심 재무비율 분석 (부채비율, 유동성비율 등)
   - 위험 지표 평가 (변동성, 집중도 등)
   - 수익성 지표 분석 (ROI, 샤프비율 등)

4. [투자 성향 진단]
   - 위험 감수성향 평가
   - 투자 스타일 분석
   - 투자 목표 정합성 검토

5. [포트폴리오 전략]
   - 현재 자산배분 평가
   - 목표 포트폴리오 제시
   - 리밸런싱 계획 (단계별 조정안)

6. [위험관리 전략]
   - 주요 위험요소 식별
   - 시나리오별 대응 전략
   - 위험 모니터링 계획

7. [실행 로드맵]
   - 단기 과제 (3개월 이내)
   - 중기 과제 (3개월~1년)
   - 장기 과제 (1년 이상)

8. [부록]
   - 용어 설명
   - 데이터 출처
   - 참고 지표 설명

응답은 반드시 한국어로 작성해주세요.
각 섹션은 아래 형식으로 작성해주세요:

[요약 섹션]
(내용)

[마이데이터 분석]
(내용)

[재무 건전성 평가]
(내용)

[투자 성향 진단]
(내용)

[포트폴리오 전략]
(내용)

[위험관리 전략]
(내용)

[실행 로드맵]
(내용)

[부록]
(내용)

각 섹션별로 체계적으로 정리해주세요. 가독성에 신경을 써 주세요.
""")

    formatted_prompt = prompt.format(
        age=personal_info.get("age", "미입력"),
        occupation=personal_info.get("occupation", "미입력"),
        family_structure=personal_info.get("family_structure", "미입력"),
        retirement_age=personal_info.get("retirement_age", "미입력"),
        housing_type=personal_info.get("housing_type", "미입력"),
        investment_style=investment_profile.get("investment_style", "미입력"),
        total_score=investment_profile.get("total_score", "미입력"),
        investment_experience=investment_details.get("investment_experience", "미입력"),
        investment_horizon=investment_details.get("investment_horizon", "미입력"),
        risk_tolerance=investment_details.get("risk_tolerance", "미입력"),
        expected_return=investment_details.get("expected_return", "미입력"),
        investment_priority=investment_details.get("investment_priority", "미입력"),
        financial_knowledge=investment_details.get("financial_knowledge", "미입력"),
        short_term_goal=personal_info.get("short_term_goal", "미입력"),
        mid_term_goal=personal_info.get("mid_term_goal", "미입력"),
        long_term_goal=personal_info.get("long_term_goal", "미입력"),
        monthly_income=financial.get("monthly_income", 0),
        fixed_expenses=financial.get("fixed_expenses", 0),
        variable_expenses=financial.get("variable_expenses", 0),
        monthly_savings=financial.get("monthly_savings", 0),
        total_debt=financial.get("total_debt", 0),
        monthly_debt_payment=financial.get("monthly_debt_payment", 0),
        average_interest_rate=financial.get("average_interest_rate", 0),
        mortgage=financial.get("mortgage", 0),
        personal_loan=financial.get("personal_loan", 0),
        credit_card=financial.get("credit_card", 0),
        other_debt=financial.get("other_debt", 0),
        cash=financial.get("cash", 0),
        emergency_fund=financial.get("emergency_fund", 0),
        savings=financial.get("savings", 0),
        real_estate=financial.get("real_estate", 0),
        funds=financial.get("funds", 0),
        etfs=financial.get("etfs", 0),
        crypto=financial.get("crypto", 0),
        pension=financial.get("pension", 0),
        insurance=financial.get("insurance", 0),
        usd=financial.get("foreign_currency", {}).get("usd", 0),
        eur=financial.get("foreign_currency", {}).get("eur", 0),
        jpy=financial.get("foreign_currency", {}).get("jpy", 0),
        gbp=financial.get("foreign_currency", {}).get("gbp", 0),
        cny=financial.get("foreign_currency", {}).get("cny", 0),
        stock_summary=stock_summary,
        asset_summary=asset_summary,
        economic_summary=economic_summary
    )

    response = llm.invoke(formatted_prompt).content

    # 섹션 제목과 키 매핑
    section_mapping = {
        "요약 섹션": "summary",
        "마이데이터 분석": "mydata",
        "재무 건전성 평가": "financial_status",
        "투자 성향 진단": "investment_style",
        "포트폴리오 전략": "portfolio",
        "위험관리 전략": "scenario",
        "실행 로드맵": "action_guide",
        "부록": "appendix"
    }

    # 응답을 섹션별로 파싱
    sections = {}
    current_section = None
    current_content = []

    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 새로운 섹션 시작 확인
        is_section_header = False
        for section_title, section_key in section_mapping.items():
            if f"[{section_title}]" in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = section_key
                current_content = []
                is_section_header = True
                break

        if not is_section_header and current_section:
            current_content.append(line)

    # 마지막 섹션 처리
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)

    # 누락된 섹션에 기본값 설정
    for section_key in section_mapping.values():
        if section_key not in sections or not sections[section_key].strip():
            sections[section_key] = "섹션 내용이 생성되지 않았습니다. 새로고침을 시도해주세요."

    return sections


def generate_portfolio_report(llm, user_info, asset_summary, economic_summary, stock_summary):
    # user_info가 문자열인 경우 JSON으로 파싱
    if isinstance(user_info, str):
        try:
            user_info = json.loads(user_info)
        except json.JSONDecodeError:
            user_info = {}

    # 섹션 제목 정의
    sections = {
        "summary": "요약 섹션",
        "mydata": "마이데이터 분석",
        "financial_status": "재무 건전성 평가",
        "investment_style": "투자 성향 진단",
        "portfolio": "포트폴리오 전략",
        "scenario": "위험관리 전략",
        "action_guide": "실행 로드맵",
        "appendix": "부록"
    }

    # 한 번의 API 호출로 모든 섹션 생성
    section_contents = generate_section_content(
        llm,
        user_info,  # 전체 user_info 전달
        asset_summary,
        economic_summary,
        stock_summary
    )

    # 결과 포맷팅
    report = {}
    for section_key, section_title in sections.items():
        report[section_key] = {
            "title": section_title,
            "content": section_contents.get(section_key, "섹션 내용을 찾을 수 없습니다.")
        }

    return report

def save_individual_report():
    # LLM 초기화
    llm = init_llm()

    supabase = SupabaseDB()
    username_lst = supabase.get_all_user_name()

    for username in username_lst:
        user_info = supabase.get_user(username)

        # 데이터 수집
        asset_summary = get_asset_summary_text()
        economic_summary = get_economic_summary_text()
        stock_summary = get_owned_stock_summary_text()

        # 보고서 생성 프로세스 개선
        with st.spinner("🤖 AI가 포트폴리오를 분석하고 있습니다..."):
            progress_text = "보고서 생성 중..."
            progress_bar = st.progress(0)

            # personal 필드에서 데이터 추출
            personal_data = user_info[0].get("personal", {})
            user_data = {
                "personal_info": personal_data.get("personal_info", {}),
                "investment_profile": personal_data.get("investment_profile", {}),
                "financial": personal_data.get("financial", {})
            }

            report = generate_portfolio_report(
                llm,
                user_data,
                asset_summary,
                economic_summary,
                stock_summary
            )

            supabase.insert_individual_report(username, report)

            # 진행률 업데이트
            progress_bar.progress(1.0)
            progress_bar.empty()

            st.success("✅ 보고서 생성이 완료되었습니다!")

if __name__ == "__main__":
    save_individual_report()