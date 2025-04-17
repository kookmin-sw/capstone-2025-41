import streamlit as st
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
    get_economic_summary_text
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

def make_investment_chain(model, asset_summary: str, etf_summary: str, economic_summary: str):
    full_prompt_template = PromptTemplate.from_template("""
Here is the user's asset summary:

{asset_summary}
                                                        
And here is the ETF information summary:
{etf_summary}

And finally, here is the Summary of Latest Economic Indicators:
{economic_summary}                                                                                                                                                                      

Based on these information, 
I'm going to ask you some investment-related questions, so please answer them accordingly.

Question: {user_input}

Please respond in Korean. 
                                                                                                             
""")


    return (
        RunnableLambda(lambda inputs: full_prompt_template.format(**inputs))
        | model
        | StrOutputParser()
    )




# 🤖 챗봇 초기화
def init_chatbot():
    api_key = st.secrets["gemini"]["api_key"] 

    '''if "llm" not in st.session_state:
        llm = ChatOpenAI(
        model_name = "gpt-4o-mini",
        openai_api_key = api_key)
        
        st.session_state["llm"] = llm'''

    if "llm" not in st.session_state:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key
        )
        st.session_state["llm"] = llm

    if "chat_memory" not in st.session_state:
        st.session_state["chat_memory"] = ConversationSummaryBufferMemory(
            llm=st.session_state["llm"],
            return_messages=True
        )

    

    if "conversation" not in st.session_state:
        st.session_state["conversation"] = ConversationChain(
            llm=st.session_state["llm"],
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


    # 체인 초기화 (자산 요약 포함)
    if "investment_chain" not in st.session_state:
        st.session_state["investment_chain"] = make_investment_chain(
            st.session_state["conversation"].llm,
            asset_summary,
            etf_summary,
            economic_summary
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
                "economic_summary": economic_summary
                })

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state["chat_history"].append(("assistant", response))

    # 사이드바에 대화 초기화 버튼 추가
    with st.sidebar:
        if st.button("💨 대화 초기화"):
            for key in ["chat_memory", "conversation", "chat_history", "investment_chain", "agent"]:
                st.session_state.pop(key, None)
            st.rerun()
 