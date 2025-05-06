import streamlit as st
import json
from dotenv import load_dotenv
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from langchain_core.messages import HumanMessage, AIMessage
from modules.DB import SupabaseDB
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import initialize_agent, AgentType
# agent 미도입 시 필요 없을듯
from modules.tools import (
    get_asset_summary_tool,
    get_economic_summary_tool,
    get_etf_summary_tool
)
from modules.tools import (
    get_asset_summary_text,
    get_etf_summary_text,
    get_economic_summary_text,
    get_owned_stock_summary_text
)
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def init_agent():
    if "agent" not in st.session_state:
        tools = [get_asset_summary_tool]
        st.session_state["agent"] = initialize_agent(
            tools=tools,
            llm=st.session_state["llm"],
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
        )


def get_user_id():
    return st.session_state.get("id")

def make_investment_chain(model, asset_summary: str, etf_summary: str, economic_summary: str, stock_summary: str, personal_summary: str):
    # 보고서 데이터 가져오기
    report_content = ""
    if "report_data" in st.session_state:
        report = st.session_state["report_data"]
        report_sections = [
            ("요약", "summary"),
            ("마이데이터 분석", "mydata"),
            ("재무 건전성 평가", "financial_status"),
            ("투자 성향 진단", "investment_style"),
            ("포트폴리오 전략", "portfolio"),
            ("위험관리 전략", "scenario"),
            ("실행 로드맵", "action_guide")
        ]
        
        for section_name, section_key in report_sections:
            if section_key in report:
                report_content += f"\n[{section_name}]\n"
                report_content += report[section_key]["content"]
                report_content += "\n"

    full_prompt_template = PromptTemplate.from_template("""
당신은 방금 생성된 개인 맞춤형 투자 포트폴리오 분석 보고서에 대해 사용자의 질문에 답변하는 전문가입니다.
아래는 방금 생성된 보고서의 전체 내용입니다:

{report_content}

사용자는 이 보고서의 내용에 대해 자유롭게 질문할 것입니다.
질문은 보고서의 특정 부분에 대한 상세 설명 요청일 수도 있고, 
보고서 전반에 대한 종합적인 질문일 수도 있으며,
보고서 내용과 현재 시장 상황을 연계한 질문일 수도 있습니다.

당신의 역할은:
1. 보고서의 내용을 완벽히 이해하고 있는 전문가로서 답변하기
2. 사용자의 질문 의도를 정확히 파악하여 관련된 모든 정보를 종합적으로 제공하기
3. 필요한 경우 보고서의 다른 섹션의 내용도 연계하여 설명하기

아래의 추가 정보들은 보고서 내용을 보완하는 데 활용하세요:
- 자산 요약: {asset_summary}
- ETF 정보: {etf_summary}
- 경제 지표: {economic_summary}
- 보유 주식: {stock_summary}
- 투자자 프로필: {personal_summary}

사용자 질문: {user_input}

답변 시 주의사항:
1. 보고서의 내용을 중심으로 답변하되, 필요시 추가 정보를 활용해 보완하세요.
2. 전문 용어는 쉽게 풀어서 설명하세요.
3. 답변은 한국어로 작성하세요.
4. 논리적이고 체계적으로 설명하세요.
""")

    return (
        RunnableLambda(lambda inputs: full_prompt_template.format(**inputs))
        | model
        | StrOutputParser()
    )




# 🤖 챗봇 초기화
def init_chatbot():
    api_key = st.secrets["gemini"]["api_key"] 

    if "question_llm" not in st.session_state:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key
        )
        st.session_state["question_llm"] = llm

    if "chat_memory" not in st.session_state:
        st.session_state["chat_memory"] = ConversationSummaryBufferMemory(
            llm=st.session_state["question_llm"],
            return_messages=True
        )

    if "conversation" not in st.session_state:
        st.session_state["conversation"] = ConversationChain(
            llm=st.session_state["question_llm"],
            memory=st.session_state["chat_memory"],
            verbose=False
        )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    init_agent()  # agent도 함께 초기화


# 💬 챗봇 페이지
def chatbot_page():
    st.title("🧠 투자 조언 챗봇")
    init_chatbot()
    
    username = get_user_id()
    supabase = SupabaseDB()
    user_info = supabase.get_user(username)

    if not user_info or "id" not in user_info[0]:
        st.error("❌ Supabase에서 해당 사용자를 찾을 수 없습니다.")
        st.stop()

    asset_summary = get_asset_summary_text()
    etf_summary = get_etf_summary_text()
    economic_summary = get_economic_summary_text()

    # personal summary 준비
    personal = user_info[0].get("personal", {})
    if isinstance(personal, str):
        try:
            personal = json.loads(personal)
        except json.JSONDecodeError:
            personal = {}

    # 문자열 형태로 요약 (LLM-friendly)
    personal_summary = "\n".join([f"{k}: {v}" for k, v in personal.items()])
    #st.text(personal_summary)
    
    # 사용자 종목 요약 가져오기
    stock_summary = get_owned_stock_summary_text()

    # 보고서 내용 가져오기
    report_content = ""
    if "report_data" in st.session_state:
        report = st.session_state["report_data"]
        report_sections = [
            ("요약", "summary"),
            ("마이데이터 분석", "mydata"),
            ("재무 건전성 평가", "financial_status"),
            ("투자 성향 진단", "investment_style"),
            ("포트폴리오 전략", "portfolio"),
            ("위험관리 전략", "scenario"),
            ("실행 로드맵", "action_guide")
        ]
        
        for section_name, section_key in report_sections:
            if section_key in report:
                report_content += f"\n[{section_name}]\n"
                report_content += report[section_key]["content"]
                report_content += "\n"

    # 체인 초기화 (자산 요약 포함)
    if "investment_chain" not in st.session_state:
        st.session_state["investment_chain"] = make_investment_chain(
            st.session_state["conversation"].llm,
            asset_summary,
            etf_summary,
            economic_summary,
            personal_summary,
            stock_summary
        )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # 이전 대화 출력
    for role, msg in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(msg)

    user_input = st.chat_input("메시지를 입력하세요...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state["chat_history"].append(("user", user_input))

        with st.spinner("응답 중..."):
            response = st.session_state["investment_chain"].invoke({
                "user_input": user_input,
                "asset_summary": asset_summary,
                "etf_summary": etf_summary,
                "economic_summary": economic_summary,
                "personal_summary": personal_summary,
                "stock_summary": stock_summary,
                "report_content": report_content if "report_data" in st.session_state else ""
            })

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state["chat_history"].append(("assistant", response))
    
    
    #st.text(report_content)
    

    # 사이드바에 대화 초기화 버튼 추가
    with st.sidebar:
        if st.button("💨 대화 초기화"):
            for key in ["chat_memory", "conversation", "chat_history", "investment_chain", "agent"]:
                st.session_state.pop(key, None)
            st.rerun()
 