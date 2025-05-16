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
'''def init_llm():
    api_key = st.secrets["gemini"]["api_key"]
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key
    )
    st.session_state["report_llm"] = llm
    return llm'''

def init_llm():
    api_key = os.getenv("GEMINI_KEY")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key
    )
    return llm

def generate_section_content(llm, user_info, asset_summary, economic_summary, stock_summary, macro_report, real_estate_report, recommended_articles):
    # 디버깅: 프롬프트에 전달되는 데이터 확인
    print("\n=== 프롬프트 데이터 확인 ===")
    print("\n[세계 경제 지표 보고서]")
    print(macro_report if macro_report else "None")
    print("\n[부동산 시장 보고서]")
    print(real_estate_report if real_estate_report else "None")
    print("\n[추천 뉴스]")
    print(recommended_articles if recommended_articles else "None")
    print("========================\n")

    # user_info에서 필요한 데이터 추출
    personal_info = user_info.get("personal_info", {})
    investment_profile = user_info.get("investment_profile", {})
    investment_details = investment_profile.get("details", {})
    financial = user_info.get("financial", {})

    # recommended_articles가 문자열인 경우 JSON으로 파싱
    if isinstance(recommended_articles, str):
        try:
            recommended_articles = json.loads(recommended_articles)
        except json.JSONDecodeError:
            print("JSON 파싱 오류 발생")
            recommended_articles = []
    
    # recommended_articles가 리스트인 경우 포맷팅
    if isinstance(recommended_articles, list):
        formatted_articles = "\n".join([
            f"- {article['title']}\n  이유: {article['reason']}\n  요약: {article['summary']}\n  링크: {article['url']}"
            for article in recommended_articles
        ])
    else:
        formatted_articles = "데이터 없음"

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

[세계 경제 지표 보고서]
{macro_report}

[부동산 시장 보고서]
{real_estate_report}

[추천 뉴스]
{formatted_articles}

[작성 가이드라인]
1. 전문성: 모든 분석과 제안은 객관적 데이터와 전문적 지표에 기반해야 합니다.
2. 실행가능성: 제시하는 모든 전략은 구체적이고 실현 가능해야 합니다.
3. 맞춤화: 고객의 상황과 성향을 고려한 개인화된 제안이어야 합니다.
4. 위험관리: 잠재적 위험요소를 명확히 식별하고 대응 방안을 제시해야 합니다.
5. 이해용이성: 전문 용어는 반드시 쉬운 설명을 덧붙여야 합니다.
6. 실시간성: 현재 시장 상황과 포트폴리오 상태를 최우선으로 반영해야 합니다.

[필수 포함 요소]
각 섹션은 반드시 [섹션명]으로 시작하며, 다음 내용을 포함해야 합니다:

1. [요약 섹션]
   1) 고객 프로필 요약
      - 연령, 직업, 자산규모 등 기본 정보
      - 현재 재무 상태의 핵심 특징
      - 최근 시장 변동에 따른 영향

   2) 투자 성향 분석
      - 투자 스타일과 위험 감수 성향
      - 투자 경험과 금융 지식 수준
      - 현재 시장 상황에 대한 적응도

   3) 핵심 제안사항 (3가지 이내)
      - 가장 시급한 재무 개선 사항
      - 단기/중기/장기 실행 전략
      - 실시간 시장 기회/위험 대응 방안

2. [마이데이터 분석]
   1) 자산 구성 분석
      - 항목별 자산 비중
      - 자산 배분의 특징과 문제점
      - 최근 수익/손실 실적

   2) 현금흐름 분석
      - 월간 수입/지출 구조
      - 저축 가능 금액과 활용 방안
      - 시장 변동에 따른 대응 방안

   3) 부채 현황
      - 총 부채 규모와 이자율
      - 상환 계획과 부채 최적화 방안
      - 금리 변동 리스크 대응

   4) 투자자산 성과 분석
      - 수익률과 위험 지표
      - 포트폴리오 효율성 평가
      - 실시간 시장 대응 필요성

3. [재무 건전성 평가]
   1) 핵심 재무비율 분석
      - 부채비율, 유동성비율 등
      - 재무 건전성 지표 해석
      - 시장 변동성 대비 준비도

   2) 위험 지표 평가
      - 변동성과 집중도 분석
      - 위험 관리 필요성
      - 실시간 위험 모니터링 방안

   3) 수익성 지표 분석
      - ROI, 샤프비율 등
      - 수익성 개선 방안
      - 현재 시장 기회 활용 방안

4. [투자 성향 진단]
   1) 위험 감수성향 평가
      - 현재 위험 감수 수준
      - 적정 위험 수준 제안
      - 시장 변동성 대응 방안

   2) 투자 스타일 분석
      - 현재 투자 스타일의 특징
      - 개선이 필요한 부분
      - 시장 상황에 따른 조정 필요성

   3) 투자 목표 정합성 검토
      - 목표와 전략의 일치성
      - 목표 달성 가능성 평가
      - 실시간 목표 조정 필요성

5. [포트폴리오 전략]
   1) 현재 자산배분 평가
      - 현재 포트폴리오 구조
      - 개선이 필요한 부분
      - 실시간 리밸런싱 필요성

   2) 목표 포트폴리오 제시
      - 이상적인 자산 배분
      - 단계별 조정 계획
      - 시장 기회 활용 방안

   3) 리밸런싱 계획
      - 단계별 조정 방안
      - 실행 일정과 방법
      - 실시간 시장 대응 전략

6. [위험관리 전략]
   1) 주요 위험요소 식별
      - 시장 위험
      - 개인 재무 위험
      - 실시간 위험 모니터링

   2) 시나리오별 대응 전략
      - 긍정적/부정적 시나리오
      - 대응 방안
      - 실시간 대응 체계

   3) 위험 모니터링 계획
      - 주요 모니터링 지표
      - 정기 검토 주기
      - 실시간 알림 설정

7. [실행 로드맵]
   1) 단기 과제 (3개월 이내)
      - 시급한 개선 사항
      - 구체적 실행 계획
      - 실시간 시장 대응

   2) 중기 과제 (3개월~1년)
      - 중기 목표 설정
      - 단계별 실행 계획
      - 시장 변동성 대응

   3) 장기 과제 (1년 이상)
      - 장기 목표 설정
      - 지속적 관리 방안
      - 시장 사이클 대응

8. [부록]
   1) 용어 설명
      - 전문 용어 정의
      - 이해를 돕는 설명
      - 실시간 시장 용어

   2) 데이터 출처
      - 분석에 사용된 데이터
      - 참고 자료
      - 실시간 데이터 소스

   3) 참고 지표 설명
      - 주요 지표 설명
      - 활용 방법
      - 실시간 모니터링 방법

응답은 반드시 한국어로 작성해주세요.
각 섹션은 위의 형식과 동일하게 작성해주세요.
- 각 섹션별로 체계적으로 정리해주세요.
- 무엇보다 고객의 투자 성향과 현재 상황에 가장 큰 중점을 두어야 합니다.
- 숫자는 **간결하게**, 인사이트는 **구체적으로**
- 지나치게 일반적인 조언은 피하고, 차별화된 전략 제안 포함
- 실시간 시장 상황과 포트폴리오 상태를 최우선으로 반영해주세요.
- 출력 시 마크다운의 취소선(`~~text~~`)은 절대 사용하지 마세요.
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
        economic_summary=economic_summary,
        macro_report=macro_report,
        real_estate_report=real_estate_report,
        formatted_articles=formatted_articles
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

    # 섹션 순서 정의
    section_order = [
        "summary",
        "mydata",
        "investment_style",
        "financial_status",
        "portfolio",
        "scenario",
        "action_guide",
        "appendix"
    ]

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
    for section_key in section_order:
        if section_key not in sections or not sections[section_key].strip():
            sections[section_key] = "섹션 내용이 생성되지 않았습니다. 새로고침을 시도해주세요."

    # 정의된 순서대로 섹션 재정렬
    ordered_sections = {}
    for section_key in section_order:
        if section_key in sections:
            ordered_sections[section_key] = sections[section_key]

    return ordered_sections


def generate_portfolio_report(llm, user_info, asset_summary, economic_summary, stock_summary, macro_report, real_estate_report, recommended_articles):
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
        "investment_style": "투자 성향 진단",
        "financial_status": "재무 건전성 평가",
        "portfolio": "포트폴리오 전략",
        "scenario": "위험관리 전략",
        "action_guide": "실행 로드맵",
        "appendix": "부록"
    }

    # 한 번의 API 호출로 모든 섹션 생성
    section_contents = generate_section_content(
        llm,
        user_info,
        asset_summary,
        economic_summary,
        stock_summary,
        macro_report,
        real_estate_report,
        recommended_articles
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
        
        # 추가 데이터 수집
        macro_report = supabase.get_macro_report()
        real_estate_report = supabase.get_real_estate_report()
        
        # users 테이블의 id 가져오기
        user_data = supabase.get_user(username)
        user_id = user_data[0].get("id") if user_data else None
        
        # id로 추천 뉴스 가져오기
        recommended_articles = supabase.get_recommended_articles(user_id) if user_id else None

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
            stock_summary,
            macro_report,
            real_estate_report,
            recommended_articles
        )

        supabase.insert_individual_report(username, report)

if __name__ == "__main__":
    save_individual_report()