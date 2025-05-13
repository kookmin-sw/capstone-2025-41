from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from pydantic import BaseModel, RootModel
from typing import List
from DB import SupabaseDB
from dotenv import load_dotenv
import os
import streamlit as st

# .env 파일의 환경 변수 불러오기
load_dotenv()

# 1. Supabase에서 데이터 불러오기
db = SupabaseDB()
id_lst = db.get_all_user_id()
articles = db.get_article_data_today_and_yesterday()

# 2. Gemini LLM 설정
api_key = os.getenv("OPENAI_KEY")
llm = ChatGoogleGenerativeAI(
    model="gpt-4.1",
    temperature=0,
    google_api_key=api_key
)

# 3. Pydantic 스키마 정의
class NewsItem(BaseModel):
    title: str
    url: str
    reason: str
    summary: str  # 본문 요약 추가

class NewsList(RootModel[List[NewsItem]]):
    pass

parser = PydanticOutputParser(pydantic_object=NewsList)
format_instructions = parser.get_format_instructions()

# 4. 프롬프트 구성 (정교한 뉴스 추천 유도)
prompt_template = PromptTemplate(
    input_variables=["keywords", "articles", "format_instructions"],
    template="""
    당신은 금융 분야에 특화된 뉴스 추천 AI입니다.

    다음은 사용자가 현재 보유 중인 자산 키워드입니다:
    {keywords}

    그리고 다음은 오늘 수집된 주요 경제 뉴스 기사입니다:
    {articles}

    이 중에서 아래 조건을 가장 잘 충족하는 상위 3개의 뉴스를 선정해 주세요:

    1. 뉴스 제목 또는 본문 내용이 자산 키워드(예: 종목명, 산업군, ETF 등)와 직접적으로 연관되어야 합니다.
    2. 해당 뉴스가 사용자의 자산 가치에 긍정적 또는 부정적 영향을 줄 수 있는 내용일수록 우선적으로 선택합니다.
    3. 뉴스 간 중복성이 없도록 하며, 다양한 자산과 연관된 기사를 선별합니다.

    각 뉴스에 대해 아래 JSON 형식에 맞게, 간결하고 명확한 관련 이유와 본문 요약을 포함하여 출력하세요.

    - title: 뉴스 제목
    - url: 뉴스 링크
    - reason: 추천 이유 (사용자의 자산과 관련된 간단한 설명)
    - summary: 뉴스 본문 요약 (3줄 이내)

    ❗주의: 반드시 JSON 형식만 출력하세요. 해설, 설명, 마크다운 등은 포함하지 마세요.

    {format_instructions}
    """
)

# 5. LangChain 체인 구성
chain = LLMChain(
    llm=llm,
    prompt=prompt_template
)

# 6. 사용자별 뉴스 추천 수행
for user_id in id_lst:
    stocks = db.get_stock_data(user_id)

    # 자산 키워드와 기사 본문 포함 구성
    user_keywords = [stock["상품명"] for stock in stocks]
    formatted_articles = "\n".join([
        f"- {a['title']}: {a['main']} ({a['url']})"
        for a in articles
    ])

    # 7. LLM 호출 및 파싱
    try:
        raw_output = chain.run({
            "keywords": ", ".join(user_keywords),
            "articles": formatted_articles,
            "format_instructions": format_instructions
        })

        result = parser.parse(raw_output)
        response = result.root  # List[NewsItem]

    except Exception as e:
        print(f"❌ 모델 실행 또는 파싱 오류 발생: {e}")
        print(raw_output if 'raw_output' in locals() else "모델 응답 없음")
        response = None

    # 8. 결과 저장
    if response:
        json_articles = [
            {
                "title": item.title,
                "url": item.url,
                "reason": item.reason,
                "summary": item.summary
            }
            for item in response
        ]

        try:
            db.insert_recommended_articles(user_id, json_articles)
            print(f"✅ 추천 뉴스가 사용자 {user_id}에 대해 저장되었습니다.")
        except Exception as e:
            print(f"⚠️ Supabase 저장 중 오류 발생: {e}")

