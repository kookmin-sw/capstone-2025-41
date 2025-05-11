from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import streamlit as st
from dotenv import load_dotenv
import os

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

    def get_prompt_template(self):
        raise NotImplementedError("Subclasses must implement get_prompt_template()")
        
    def generate(self, **kwargs):
        prompt = self.get_prompt_template()
        formatted_prompt = prompt.format(**kwargs)
        response = self.model.invoke(formatted_prompt)
        return response.content 