from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import streamlit as st
from dotenv import load_dotenv
import os
from modules.DB import SupabaseDB

class BaseLLM:
    def __init__(self):
        api_key = st.secrets["gemini"]["api_key"] 

        # LLM 초기화
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=api_key
        )
        st.session_state["question_llm"] = self.model
        self.db = SupabaseDB()

    def get_prompt_template(self):
        raise NotImplementedError("Subclasses must implement get_prompt_template()")
        
    def generate(self, username, **kwargs):
        # 사용자의 개인 리포트 가져오기
        report_data = self.db.get_individual_report(username)
        
        # 디버깅: 리포트 데이터 확인
        print(f"\n=== {self.__class__.__name__} 디버깅 ===")
        print(f"사용자: {username}")
        print(f"리포트 데이터 존재 여부: {report_data is not None}")
        if report_data:
            print("리포트 섹션:")
            for section, content in report_data.items():
                if isinstance(content, dict) and "content" in content:
                    print(f"- {section}: {content['content'][:100]}...")
                else:
                    print(f"- {section}: {str(content)[:100]}...")
        print("========================\n")
        
        # 리포트 데이터를 kwargs에 추가
        if report_data:
            kwargs['report_data'] = report_data
            
        prompt = self.get_prompt_template()
        
        # 디버깅: 최종 프롬프트 확인
        print("=== 최종 프롬프트 ===")
        print(prompt.format(**kwargs))
        print("===================\n")
        
        response = self.model.invoke(prompt.format(**kwargs))
        return response.content 