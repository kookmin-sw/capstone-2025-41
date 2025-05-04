import streamlit as st
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from fpdf import FPDF
import tempfile
from modules.tools import (
    get_asset_summary_text,
    get_etf_summary_text,
    get_economic_summary_text,
    get_owned_stock_summary_text
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.units import inch

def get_user_id():
    return st.session_state.get("id")

def init_llm():
    if "llm" not in st.session_state:
        api_key = st.secrets["gemini"]["api_key"]
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key
        )
        st.session_state["llm"] = llm

def generate_section_content(llm, user_info, asset_summary, economic_summary, stock_summary):
    # user_info에서 필요한 데이터 추출
    if isinstance(user_info, str):
        try:
            user_info = json.loads(user_info)
        except json.JSONDecodeError:
            user_info = {}
    
    financial = user_info.get("financial", {})
    investment_profile = user_info.get("investment_profile", {})
    investment_details = investment_profile.get("details", {})

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
""")
    
    formatted_prompt = prompt.format(
        age=financial.get("age", "미입력"),
        occupation=financial.get("occupation", "미입력"),
        family_structure=financial.get("family_structure", "미입력"),
        retirement_age=financial.get("retirement_age", "미입력"),
        housing_type=financial.get("housing_type", "미입력"),
        investment_style=investment_profile.get("investment_style", "미입력"),
        total_score=investment_profile.get("total_score", "미입력"),
        investment_experience=investment_details.get("investment_experience", "미입력"),
        investment_horizon=investment_details.get("investment_horizon", "미입력"),
        risk_tolerance=investment_details.get("risk_tolerance", "미입력"),
        expected_return=investment_details.get("expected_return", "미입력"),
        investment_priority=investment_details.get("investment_priority", "미입력"),
        financial_knowledge=investment_details.get("financial_knowledge", "미입력"),
        short_term_goal=financial.get("short_term_goal", "미입력"),
        mid_term_goal=financial.get("mid_term_goal", "미입력"),
        long_term_goal=financial.get("long_term_goal", "미입력"),
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
    
    # personal 필드가 문자열인 경우 JSON으로 파싱
    if isinstance(user_info.get("personal"), str):
        try:
            user_info["personal"] = json.loads(user_info["personal"])
        except json.JSONDecodeError:
            user_info["personal"] = {}

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
    
    progress_text = "보고서 생성 중..."
    progress_bar = st.progress(0)
    
    # 한 번의 API 호출로 모든 섹션 생성
    section_contents = generate_section_content(
        llm,
        user_info.get("personal", {}),  # personal 필드만 전달
        asset_summary,
        economic_summary,
        stock_summary
    )
    
    # 결과 포맷팅
    report = {}
    for i, (section_key, section_title) in enumerate(sections.items()):
        report[section_key] = {
            "title": section_title,
            "content": section_contents.get(section_key, "섹션 내용을 찾을 수 없습니다.")
        }
        progress_bar.progress((i + 1) / len(sections))
    
    progress_bar.empty()
    return report

def generate_pdf_report(report_data):
    # 폰트 등록
    pdfmetrics.registerFont(TTFont('NanumGothic', 'fonts/NanumGothic-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('NanumGothicBold', 'fonts/NanumGothic-Bold.ttf'))
    registerFontFamily('NanumGothic', normal='NanumGothic', bold='NanumGothicBold')

    # PDF 스타일 설정
    styles = getSampleStyleSheet()
    
    # 기본 스타일
    styles.add(ParagraphStyle(
        name='Korean',
        fontName='NanumGothic',
        fontSize=10,
        leading=16,
        textColor='#333333'
    ))
    
    # 제목 스타일
    styles.add(ParagraphStyle(
        name='KoreanTitle',
        fontName='NanumGothicBold',
        fontSize=24,
        leading=30,
        spaceAfter=30,
        textColor='#1a237e',
        alignment=1  # 중앙 정렬
    ))
    
    # 섹션 제목 스타일
    styles.add(ParagraphStyle(
        name='KoreanSection',
        fontName='NanumGothicBold',
        fontSize=16,
        leading=24,
        spaceBefore=20,
        spaceAfter=12,
        textColor='#0d47a1',
        borderWidth=1,
        borderColor='#bbdefb',
        borderPadding=5,
        borderRadius=5,
        backColor='#e3f2fd'
    ))
    
    # 강조 텍스트 스타일
    styles.add(ParagraphStyle(
        name='KoreanEmphasis',
        fontName='NanumGothicBold',
        fontSize=11,
        leading=18,
        textColor='#d32f2f'
    ))

    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        doc = SimpleDocTemplate(
            tmp_file.name,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        # 문서 내용 생성
        story = []
        
        # 제목 추가
        title = Paragraph("투자 포트폴리오 분석 리포트", styles['KoreanTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # 각 섹션 추가
        for section_key, section_data in report_data.items():
            # 섹션 제목
            section_title = Paragraph(section_data['title'], styles['KoreanSection'])
            story.append(section_title)
            
            # 섹션 내용
            content = section_data['content']
            
            # 내용을 문단으로 분리하고 스타일 적용
            paragraphs = content.split('\n')
            for para in paragraphs:
                if para.strip():
                    # 강조할 내용 (예: 숫자, 중요 키워드)에 스타일 적용
                    if any(keyword in para for keyword in ['수익률', '위험', '목표', '전략']):
                        p = Paragraph(para, styles['KoreanEmphasis'])
                    else:
                        p = Paragraph(para, styles['Korean'])
                    story.append(p)
                    story.append(Spacer(1, 8))

            # 섹션 구분선
            story.append(Spacer(1, 20))
            story.append(Paragraph('<hr width="100%" color="#bbdefb"/>', styles['Korean']))
            story.append(Spacer(1, 20))

        # PDF 생성
        doc.build(story)
        return tmp_file.name

def chatbot_page2():
    st.title("📊 투자 포트폴리오 분석 리포트")

    # 사이드바 개선
    with st.sidebar:
        st.title("🛠️ 보고서 설정")
        
        if st.button("🔄 보고서 초기화 및 재생성"):
            for key in ["llm", "report_data"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    init_llm()
    
    username = get_user_id()
    supabase = SupabaseDB()
    user_info = supabase.get_user(username)

    if not user_info or "id" not in user_info[0]:
        st.error("❌ Supabase에서 해당 사용자를 찾을 수 없습니다.")
        st.stop()

    # 데이터 수집
    asset_summary = get_asset_summary_text()
    economic_summary = get_economic_summary_text()
    stock_summary = get_owned_stock_summary_text()

    # 보고서 생성 프로세스 개선
    if "report_data" not in st.session_state:
        with st.spinner("🤖 AI가 포트폴리오를 분석하고 있습니다..."):
            progress_text = "보고서 생성 중..."
            progress_bar = st.progress(0)
            
            report = generate_portfolio_report(
                st.session_state["llm"],
                user_info[0],
                asset_summary,
                economic_summary,
                stock_summary
            )
            progress_bar.empty()
            st.success("✅ 보고서 생성이 완료되었습니다!")
            st.session_state["report_data"] = report
    else:
        report = st.session_state["report_data"]

    # 섹션 헤더 디자인 개선
    sections = [
        ("📋 요약", "summary", True),
        ("📈 마이데이터 분석", "mydata", False),
        ("💰 재무 건전성 평가", "financial_status", False),
        ("👤 투자 성향 진단", "investment_style", False),
        ("📊 포트폴리오 전략", "portfolio", False),
        ("⚠️ 위험관리 전략", "scenario", False),
        ("📅 실행 로드맵", "action_guide", False),
        ("📚 부록", "appendix", False)
    ]
    
    # 섹션별 내용 표시
    for title, key, default_expanded in sections:
        st.header(title)
        with st.expander("내용 보기", expanded=default_expanded):
            content = report[key]["content"]
            # 마크다운 형식의 텍스트를 보기 좋게 표시
            st.markdown(content)

    # PDF 다운로드 버튼
    col1, col2, col3 = st.columns([6, 3, 6])
    with col2:
        try:
            # PDF 생성
            pdf_path = generate_pdf_report(st.session_state["report_data"])
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            
            st.download_button(
                label="📥 PDF",
                data=pdf_bytes,
                file_name="portfolio_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF 생성 중 오류가 발생했습니다: {str(e)}")